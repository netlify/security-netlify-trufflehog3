#!/bin/bash

PARAMS_STRING=""

# ARG- Must Supply Trufflehog3 Report Path 
if [ ! -z "$1" ]
then
	PARAMS_STRING+="--report-path=$1"
fi

# ARG - Suppressions List File Path
if [ ! -z "$2" ]
then
	PARAMS_STRING+=" --suppressions-path=$2"
fi

# ARG - Paths-to-Ingore List File Path
if [ ! -z "$2" ]
then
	PARAMS_STRING+=" --ignore-paths=$3"
fi

# ARG - Create Github Issues Bool
if [ ! -z "$3" ]
then
	PARAMS_STRING+=" --github=$4"
fi

# ARG - Create Slack Notifications Bool
if [ ! -z "$5" ]
then
	PARAMS_STRING+=" --slack=$5"
fi

echo "$PARAMS_STRING"
 
#python3 trufflehog_python.py --report-path="trufflehog_report.json" 
python3 /trufflehog_python.py $PARAMS_STRING 
