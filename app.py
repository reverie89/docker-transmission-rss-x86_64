#!/usr/bin/env python
# -*- coding: utf-8 -*-

print "Starting script..."

import yaml, feedparser # pip install
import io, time, re, subprocess

from datetime import datetime, timedelta

fileTorrentLog = "/config/torrent.log"
fileConfigYaml = "/config/config.yaml"
fileExcludeLinks = "/config/excludeLinks.txt"
fileExcludeTitles = "/config/excludeTitles.txt"
fileErrorsLog = "/config/errors.log"

# fix %z datetime bug for Python 2.7
def dt_parse(t):
    ret = datetime.strptime(t[0:24],'%a, %d %b %Y %H:%M:%S') # Jackett's RSS feed date format: Sat, 21 Apr 2018 17:48:00 +0800
    if t[26]=='+':
        ret-=timedelta(hours=int(t[27:29]),minutes=int(t[30:]))
    elif t[26]=='-':
        ret+=timedelta(hours=int(t[27:29]),minutes=int(t[30:]))
    return ret

# create files if don't exist already
io.open(fileTorrentLog, "a", encoding="UTF8").close()
io.open(fileExcludeLinks, "a", encoding="UTF8").close()
io.open(fileExcludeTitles, "a", encoding="UTF8").close()
io.open(fileErrorsLog, "a", encoding="UTF8").close()

# run until script terminates, usually as a result of modification of config.yaml detected by another bash script
while True:
	# read files into memory
	with io.open(fileTorrentLog, "r", encoding="UTF8") as stream:
		torrentList = [] if (stream is None) else [line.rstrip() for line in stream]
	with io.open(fileExcludeLinks, "r", encoding="UTF8") as stream:
		excludeLinksList = [] if (stream is None) else [line.rstrip() for line in stream]
	with io.open(fileExcludeTitles, "r", encoding="UTF8") as stream:
		excludeTitlesList = [] if (stream is None) else [line.rstrip() for line in stream]

	# open config.yaml for configuration parameters
	with io.open(fileConfigYaml, "r") as stream:

		try:
			config = yaml.load(stream)
			# set defaults in case not defined in config.yaml
			host = "http://127.0.0.1"
			port = "9091"
			rpcpath = "/transmission"
			username = "transmission"
			password = "transmission"
			update_interval = "600" if (config["update_interval"] is None) else config["update_interval"]
			for transmission in config["server"]:
				for key, value in transmission.iteritems():
					if (key == "host"):
						host = value
					if (key == "port"):
						port = value
					if (key == "rpc_path"):
						rpcpath = value
					if (key == "username"):
						username = value
					if (key == "password"):
						password = value
			# fix paths if necessary
			host = ("http://" + host) if (host[:4] != "http") else host
			rpcpath = ("/" + rpcpath) if (rpcpath[0] != "/") else rpcpath
			# open feeds
			for feed in config["feeds"]:
				#print "Opening %s" % feed["url"]
				if (feed.get("regex") is None):
					feed["regex"] = ""
				#print "Regex is: %s" % feed["regex"]
				if (feed.get("contains") is None):
					feed["contains"] = ""
				#print "Regex is: %s" % feed["regex"]
				if (feed.get("fromDate") is None):
					feed["fromDate"] = datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
				else:
					feed["fromDate"] = datetime.strptime(feed["fromDate"], "%Y-%m-%d %H:%M:%S")
				#print "From date is: %s" % feed["fromDate"]
				if ( (feed.get("startPaused") is None) or (feed.get("startPaused") == "false") ):
					feed["startPaused"] = ""
				else:
					feed["startPaused"] = "--start-paused"
				#print "Start torrents paused is: %s" % feed["startPaused"]
				print "Opening RSS feed: %s" % feed["url"]
				for item in feedparser.parse(feed["url"]).entries:
					# check if torrents listed in RSS feed fulfill conditions as per config.yaml
					if ( (not item["title"] in excludeTitlesList) and \
					(not item["link"] in excludeLinksList) and \
					(dt_parse(item["published"]) >= feed["fromDate"]) and \
					(re.match(feed["regex"], item["title"])) and \
					(feed["contains"] in item["title"]) and \
					(not item["title"] in torrentList) ):
						#print "Title: %s " % item["title"]
						#print "Published later than: %s" % feed["fromDate"]
						#print "Published: %s" % dt_parse(item["published"])
						#print "Link: %s" % item["link"]

						# run transmission-remote, if output text at the end of string = "success", add to torrent log
						# transmission-remote http://127.0.0.1:9091/transmission --auth username:password --add <file> --start-paused
						try:
							subprocess.check_output(["transmission-remote", \
										host + ":" + str(port) + rpcpath, \
										"--auth", username + ":" + password, \
										"--add", item["link"], \
										feed["startPaused"] ])
							print "Adding to torrent log: %s" % item["title"]
							with io.open(fileTorrentLog, "a", encoding="UTF8") as torrentLog:
								torrentLog.write( item["title"] + "\n" )
							#torrentList.append( item["title"] )
						except subprocess.CalledProcessError as exc:
							print "Could not add torrent. See errors.log for details. Adding link to exclude list: %s" % item["title"]
							with io.open(fileExcludeLinks, "a", encoding="UTF8") as excludeLinks:
								excludeLinks.write( item["link"] + "\n" )
							#excludeLinksList.append( item["link"] )
							with io.open(fileErrorsLog, "a", encoding="UTF8") as errorLog:
								errorLog.write( "Torrent: " + item["title"] + " : " + str(exc) + "\n" )

		except yaml.YAMLError as exc:
			print(exc)

	print "Script complete, waiting for next run in %s seconds" % update_interval
	time.sleep(update_interval)
