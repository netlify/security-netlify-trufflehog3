```
              _,-""""-..__
         |`,-'_. `  ` ``  `--'""".
         ;  ,'  | ``  ` `  ` ```  `.
       ,-'   ..-' ` ` `` `  `` `  ` |==.
     ,'    ^    `  `    `` `  ` `.  ;   \
    `}_,-^-   _ .  ` \ `  ` __ `   ;    #
       `"---"' `-`. ` \---""`.`.  `;
                  \\` ;       ; `. `,
                   ||`;      / / | |
      jrei        //_;`    ,_;' ,_;"
```
# security-netlify-trufflehog3
This repository is meant to hold trufflehog3 secret-scanning utility

# Security Netlify Trufflehog Parse
[trufflehog is a container scanning tool from https://github.com/feeltheajf/trufflehog3. This action is written in python and executes trufflehog, then parses the trufflehog report to provide extra functionality, such as: suppression handling, alerting to slack, opening github issues with labels specifying risk level, by specifying which severity levels of notifications.

## Inputs

#### `trufflehog_report_file_path`

location of trufflehog report that will be parsed

#### `suppression_file_path` 

path/name of suppression list file
Sometimes a particular vulnerability does not need to be addressed. This can be due to the environment or other priority directives. To suppress the vulnerability from the alerted findings, add the contents of the `Layer SHA256` value to a `suppressions-trufflehog` file, and indicate the path as an comment. You can also add the commit hash to suppress an entire commit. 

#### `ignore_paths_file_path` 

path/name of ignore_paths list file
Please try to suppress by the commit or SHA256 using the `suppressions-trufflehog3` file first. 

But sometimes a particular path does not need to be addressed. This can be due to the environment or other priority directives. To suppress the path from the alerted findings, add the full path to the `ignore-paths-trufflehog` file, and leave a comment if neccessary. 

You can also use paths with a wildcard `*`, such as `some_directory/some_nested_directory/*. This works by stripping the wildcard and comparing to the startswith() of the filepath. 

#### `create_github_issue`

boolean if user wishes to create github issues

#### `create_slack_notification` 

boolean if user wishes to create slack alert

#### `secret_scan_slack_webhook` 

secret_scan_slack_webhook: ${{ secrets.SECRET_SCAN_SLACK_WEBHOOK }}

#### `secret_scan_gh_access_token`         

secret_scan_gh_access_token: ${{ secrets.GITHUB_TOKEN }}

#### `github_repo_name`

github_repo_name: ${{ github.repository }}

#### `github_server`

github_server: ${{ github.server_url }} 


## Example Usage 
First you must call the trufflehog action or get trufflehog directly and use it to produce a json report:

```
      - name: Trufflehog3 Secret Scan and Report Parser
        uses: netlify/security-netlify-trufflehog3@v0.5.1
        with:
          trufflehog_report_file_path: 'trufflehog_report.json'
          suppression_file_path: '.github/workflows/trufflehog3-files/suppressions-trufflehog3'
          ignore_paths_file_path: '.github/workflows/trufflehog3-files/ignore-paths-trufflehog3'
          create_github_issue: 'true'
          create_slack_notification: 'false'
          secret_scan_slack_webhook: ${{ secrets.SECRET_SCAN_SLACK_WEBHOOK }}
          secret_scan_gh_access_token: ${{ secrets.GITHUB_TOKEN }}
          github_repo_name: ${{ github.repository}}
          github_server: ${{ github.server_url }}
```

## Manually testing locally on your repo

- The easiest way to test the secret scan is to install trufflehog3 using pip.
- Also clone or fetch the script from https://github.com/netlify/security-netlify-trufflehog3
- Unfortunately, even though you are running locally, you have to set the `GITHUB_REPO` env var to be your repo name, but it will run with any value. 
- Then you can run the python code that uses trufflehog3 to create and parse the report:

```
#python3 trufflehog_python.py -p suppressions-trufflehog3 -i ignore-paths-trufflehog3
```

By optionally setting the appropriate env vars you can also test creating github issues or slack alerting

### Alerting to Slack
This tool can alert to slack. By specifying `-s/--slack=true` as an argument in python trufflehog execution, it will send an alert to slack for each finding. The default is `false`.

You must also have envvar `SECRET_SCAN_SLACK_WEBHOOK`

### Creating Github Issues
This tool can create issues in github. By specifying `-g/--github=true` as an argument in python trufflehog execution, it will create a github issue for each finding. The default is `false`.

ou must also have envvar `SECRET_SCAN_GH_ACCESS_TOKEN`
