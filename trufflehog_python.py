#!/usr/bin/env python3

import json
import requests
import argparse
import codecs
import subprocess
import os
import hashlib
import time
import glob
from slack import WebClient
from slack.errors import SlackApiError
from github import Github

# github actions is having issues calling trufflehog3 on some files due to LFS problems.
# this could be better.
git_lfs_problem_repos = [ 'repo-name'
                        ]

def new_scan(report_path):
#    process = subprocess.Popen(['/usr/local/bin/trufflehog3',
    process = subprocess.Popen(['trufflehog3',
                                '--output', report_path,
                                '--format', 'json',
                                '--no-entropy',
                                '--max-depth=1000',
                                '--line-numbers',
                                '--no-current',
                                './'
                                ], 
                           stdout=subprocess.PIPE,
                           universal_newlines=True)

    while True:
        output = process.stdout.readline()
        print(output.strip())
        # Do something else
        return_code = process.poll()
        if return_code is not None:
            print('RETURN CODE', return_code)
            # Process has finished, read rest of the output 
            for output in process.stdout.readlines():
                print(output.strip())
            break

def parse_report_for_issues(repo_name, report_path, suppressions_path, ignore_paths, slack_webhook, slack_alert, github_issue):
    filename = report_path 
    with open(filename, 'r+') as json_file:
        json_data = json.load(json_file)
        for issue in json_data:
            #print("Entire Issue: {}\n".format(issue))         
            message = "New Finding Alert\n"
            message += "--Repo: " + repo_name + "\n"
            message += "--Date: " + json.dumps(issue['date']) + "\n"
            message += "--Path: " + json.dumps(issue['path']) + "\n"
            message += "--Branch: " + json.dumps(issue['branch']) + "\n"
            message += "--Commit Hash: " + json.dumps(issue['commitHash']) + "\n"
            message += "--Commit: " + json.dumps(issue['commit']) + "\n"
            message += "--Reason: " + json.dumps(issue['reason']) + "\n"
            #hack - Hard to deal with some specific long strings or other paths we dont care about   
            for found_string in issue['stringsFound']:
                if os.path.exists(ignore_paths):
                    file = open(ignore_paths, 'r')
                    file_lines = file.readlines()
                    #count = 0
                    for line in file_lines:
                        #print("Line{}: {}".format(count, line.strip().split(' ', 1)[0]))
                        if json.dumps(issue['path']) == line.strip().split(' ', 1)[0]:
                            print("--String Discovered: Redacted - too long")
                            message += "--String Discovered: Redacted - too long\n"
                        else:
                            print("--String Discovered: " + json.dumps(found_string))
                            message += "--String Discovered: " + json.dumps(found_string) + "\n"
                else:
                    print("--String Discovered: " + json.dumps(found_string) + "\n")
                    message += "--String Discovered: " + json.dumps(found_string) + "\n"
            digest = hashlib.sha256()
            digest.update(str.encode(repo_name) + str.encode(json.dumps(issue['path'])) + str.encode(json.dumps(found_string)))
            issue_title = "secret discovered - " + json.dumps(issue['path'] + " - " + digest.hexdigest() )
            message += "--SHA256: " + digest.hexdigest() + "\n"
            print(message)
            print("\n")

            # Checking if commitHash or sha256 digest is in suppressions file
            suppressions_matched = "false"
            if os.path.exists(suppressions_path):
                file = open(suppressions_path, 'r')
                file_lines = file.readlines()              
                for line in file_lines:
                    #print("Line{}: {}".format(count, line.strip().split(' ', 1)[0]))
                    if json.dumps(issue['commitHash']).strip('\"') == line.strip().split(' ', 1)[0] or digest.hexdigest() == line.strip().split(' ', 1)[0]:
                        suppressions_matched = "true"
                
            #Suppress notifications of these paths explicitly
            path_matched = "false"
            if os.path.exists(ignore_paths):
                file = open(ignore_paths, 'r')
                file_lines = file.readlines()
                for line in file_lines:
                    #print("Line from file: {}".format(line.strip().split(' ', 1)[0]))
                    #print("Line from report: ", json.dumps(issue['path']).strip('"'))
                    if json.dumps(issue['path']).strip('"') == line.strip().split(' ', 1)[0]:
                        path_matched = "true"

            #If not suppressed, send to slack and/or github
            if suppressions_matched == "false" and path_matched == "false":
                #print("Message: " + message)
                #print("\n")
                if slack_alert == "true":
                    send_slack_alert(slack_webhook, message)
                if github_issue == "true":
                    dedup_and_create_gh_issue(message, issue_title)
                    
    #except:
        #print(" [ERROR] Cannot open file: " + filename)

def get_slack_webhook_from_env() -> str:
    slack_webhook=os.environ.get('SECRET_SCAN_SLACK_WEBHOOK', None) 
    if slack_webhook is None:
        raise ValueError(
            'Must provide slack_webhook.'
        )
    return slack_webhook

def get_gh_access_token_from_env() -> str:
    gh_access_token=os.environ.get('SECRET_SCAN_GH_ACCESS_TOKEN', None)
    if gh_access_token is None:
        raise ValueError(
            'Must provide github_access_token.'
        )
    return gh_access_token

def get_repo_from_env() -> str:
    repo_path = os.environ.get('GITHUB_REPO', None)
    if repo_path is None:
        raise ValueError(
               'Must provide repo.',
               'eg. netlify/repo_to_scan' 
        )
    return repo_path

def matches_issue_in_repo(repo_path, g, issue_title):
    issues = get_issues_from_repo(repo_path, g)
    for issue in issues:
#        print(f"Issue : {issue.title} \n")
        if issue.title == issue_title:
            print("Issue " + issue.title + " already exists\n")
            issue_matched = "true"
            return issue_matched
        
def get_issues_from_repo(repo_path, g):
    repo = g.get_repo(repo_path)
    return repo.get_issues()

def dedup_and_create_gh_issue(message, issue_title):
    repo_path = get_repo_from_env()
    print("Repo Path: " + repo_path + "\n")
    gh_access_token = get_gh_access_token_from_env()
    g = Github(gh_access_token)
    issue_matched = matches_issue_in_repo(repo_path, g, issue_title)
    if issue_matched != "true":
        create_gh_issue(message, issue_title, repo_path, g)

def create_gh_issue(message, issue_title, repo_path, g):
    repo = g.get_repo(repo_path)
    i = repo.create_issue(
        title=issue_title,
        body=message,
        labels=[
             "security", 
             "security-risk: low",
             "trufflehog"
        ]
    )

def send_slack_alert(slack_webhook, message):
    data = {
        'text': message,
        'username': 'Trufflehog-Bot',
        'icon_emoji': ':boar:'
    }

    response = requests.post(slack_webhook, data=json.dumps(
        data), headers={'Content-Type': 'application/json'})

def main():
    slack_webhook = "Null"
    slack_alert = "false"
    github_issue = "false"
    repo_name = get_repo_from_env()  

    parser = argparse.ArgumentParser(description="Trufflehog Secret Scanner")
    parser.add_argument('-r',"--report-path",required=True,default="trufflehog_report.json",help="Location of Required Filepath of Trufflehog Report File to be Parsed")
    parser.add_argument('-p',"--suppressions-path",required=False,default="suppressions-trufflehog",help="Location of Optional Suppressions List File")
    parser.add_argument('-i',"--ignore-paths",required=False,default="ignore-paths-trufflehog",help="Location of Optional Paths-to-Ignore List File")
    parser.add_argument('-g',"--github",required=False,default=False,help="Create a Github Issue for Each Secret Found")
    parser.add_argument('-s',"--slack",required=False,default=False,help="Send a Slack Alert for Each Secret Found")
    args = parser.parse_args()

    if args.slack == "True" or args.slack == "true" or args.slack == "T" or args.slack == "t":
        slack_alert = "true"
    if args.github == "True" or args.github == "true" or args.github == "T" or args.github == "t":
        github_issue = "true"

    if slack_alert == "true":
        slack_webhook = get_slack_webhook_from_env()

    message = "Starting Trufflehog3 Scan and Report Parse\n"
    print(message)
    if slack_alert == "true":
        send_slack_alert(slack_webhook, message)
    
    new_scan(args.report_path)
    parse_report_for_issues(repo_name, args.report_path, args.suppressions_path, args.ignore_paths, slack_webhook, slack_alert, github_issue)

    message = "Trufflehog3 Scan and Report Parse Complete\n"
    print(message)
    if slack_alert == "true":
        send_slack_alert(slack_webhook, message)

if __name__ == "__main__":
    main()
