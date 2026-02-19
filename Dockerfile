FROM myoung34/github-runner:latest

USER root

RUN apt-get update && apt-get install -y python3

COPY server.py /home/runner/server.py

ENTRYPOINT []

CMD ["/bin/sh", "-c", "cd /home/runner && python3 server.py"]




