FROM lsiobase/alpine.python:3.7

COPY app.py config.yaml /
COPY entrypoint.sh /usr/local/bin/

RUN apk add --no-cache transmission-cli && \
    pip install --no-cache-dir -U feedparser pyyaml && \
    chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT "/usr/local/bin/entrypoint.sh"
