FROM myoung34/github-runner:latest

USER root

RUN apt-get update && apt-get install -y python3

WORKDIR /app

COPY server.py /app/server.py

EXPOSE 8080

CMD ["python3", "/app/server.py"]



