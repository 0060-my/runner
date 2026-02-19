FROM myoung34/github-runner:latest

USER root

RUN apt-get update && apt-get install -y python3

ENTRYPOINT []

CMD ["/bin/sh", "-c", "/run.sh & mkdir -p /health && cd /health && python3 -m http.server $PORT"]

