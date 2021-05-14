
FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY trufflehog_python.py /trufflehog_python.py

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

#ENTRYPOINT ["sh", "-c", "python3 /trufflehog_python.py --github=false --slack=false"]

