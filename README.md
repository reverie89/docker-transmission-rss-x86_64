# Transmission-RSS in a Docker image (Alpine)

## Overview
Written with inspiration from [nning's transmission-rss](https://github.com/nning/transmission-rss)
Simple script based on [alpine 3.7 + python 2.7](https://hub.docker.com/r/lsiobase/alpine.python/) to pull RSS feeds.
Tested on Jackett's RSS feeds only.

## Features
- Run at your specified interval in seconds (default: 600)
- Regex matching or use simple string contains
- Torrents added will be saved in `torrent.log` and will not be added into Transmission anymore (until you remove it from the log)
- Torrents that cannot be added will have its error output in `errors.log` and its links added to `excludeLinks.txt`
- If you have specific titles that want to be excluded from the search, use excludeTitles.txt
- If `start-paused` is set to true, torrents added into transmission will not start immediately. If this option is missing, the default behavior will be set to false i.e. torrents will start as they are added
- If you only want to get torrents published after a specific date/time, use the "fromDate" option in the following format: `YYYY-MM-DD HH:MM:SS`

## Deploy
```
docker run -d \
  --name transmission-rss \
  --restart=unless-stopped \
  -v /opt/docker/transmission-rss:/config \
  reverie89/transmission-rss
```

Edit `config.yaml` to your liking before starting container

## Tips
- If your transmission server is located in another network, remember to specify --net flag when running docker
- You must input valid RSS feed links otherwise the script will be stuck!

## Docker troubleshooting
Check logs of gitbucket server container:
```bash
$ docker logs transmission-rss
```

Review how things are deployed inside a running container, you can do this by executing a _bash shell_ through _docker's exec_ command:
```bash
docker exec -it transmission-rss /bin/bash
```
