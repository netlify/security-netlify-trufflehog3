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
[trufflehog is a container scanning tool from <needed>. This action is written in python and executes trufflehog, then parses the trufflehog report to provide extra functionality, such as: suppression handling, alerting to slack, opening github issues with labels specifying risk level, by specifying which severity levels of notifications.

## Inputs

#### `trufflehog_report_file_path`

**Required** - location of trufflehog report that will be parsed

#### `suppression_file_path` 

path/name of suppression list file
Sometimes a particular vulnerability does not need to be addressed. This can be due to the environment or other priority directives. To suppress the vulnerability from the alerted findings, add the contents of the `Layer SHA256` value to a `suppressions-trufflehog` file, and indicate the path as an comment. 

#### `ignore_paths_file_path` 

path/name of ignore_paths list file
Sometimes a particular path does not need to be addressed. This can be due to the environment or other priority directives. To suppress the path from the alerted findings, add the full path to the `ignore-paths-trufflehog` file, and leave a comment if neccessary. 

#### `create_github_issue`

boolean if user wishes to create github issues

#### `create_slack_notification` 

boolean if user wishes to create slack alert

#### `secret_scan_slack_webhook` 

secret_scan_slack_webhook: ${{ secrets.SECRET_SCAN_SLACK_WEBHOOK }}

#### `secret_scan_gh_access_token`         

secret_scan_gh_access_token: ${{ secrets.GITHUB_TOKEN }}

####  `github_repo_name`

github_repo_name: ${{ github.repository}}


## Example Usage 
First you must call the trufflehog action or get trufflehog directly and use it to produce a json report:

```
      - name: trufflehog Parse Report
        uses: netlify/security-netlify-trufflehog@v0.1
        with:
          trufflehog_report_file_path: 'trufflehog_report.json'
          suppression_file_path: 'suppressions'
          create_github_issue: 'true'
          create_slack_notification: 'false'
          secret_scan_slack_webhook: ${{ secrets.SECRET_SCAN_SLACK_WEBHOOK }}
          secret_scan_gh_access_token: ${{ secrets.GITHUB_TOKEN }}
          github_repo_name: ${{ github.repository}}
```

## Manually running the python script on your trufflehog report

### Alerting to Slack
This tool can alert to slack. By specifying `-s/--slack=true` as an argument in `.github/workflows/trufflehog-main.yml` python trufflehog execution, it will send an alert to slack for each finding. The default is `false`.

You must also have envvar `SECRET_SCAN_SLACK_WEBHOOK`

### Creating Github Issues
This tool can create issues in github. By specifying `-g/--github=true` as an argument in `.github/workflows/trufflehog-main.yml` python trufflehog execution, it will create a github issue for each finding. The default is `false`.
