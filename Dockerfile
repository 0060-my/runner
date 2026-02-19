FROM myoung34/github-runner:latest

USER root

RUN apt-get update && apt-get install -y python3

CMD /bin/sh -c "/usr/local/bin/entrypoint.sh & python3 -m http.server \$PORT"
