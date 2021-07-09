
FROM python:3

RUN apt-get update && \
    apt-get install -y python3 python3-pip git && \
    apt-get clean

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY * /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

#ENTRYPOINT ["sh", "-c", "python3 /trufflehog_python.py --report-path=trufflehog_report.json --github=false --slack=false"]

