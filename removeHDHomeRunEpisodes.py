#!/usr/local/bin/python2.7

import os, ConfigParser, StringIO
from collections import deque

# config {
# config_file = path to hdhomerun.conf
# episodes = dictionary of showname, maximum episodes
#     special key "default" for default value

config_file = "/usr/local/etc/hdhomerun.conf"
episodes = {
    "Jeopardy!": 10,
    "default": 5
}

# } end config

# add fake [section] to config file for ConfigParser to work
ini_str = '[root]\n' + open(config_file, 'r').read()
ini_fp = StringIO.StringIO(ini_str)
config = ConfigParser.RawConfigParser()
config.readfp(ini_fp)

# read RecordPath key value
if config.has_option('root', 'RecordPath'):
    dvrdir = config.get('root', 'RecordPath')
else:
    raise Exception('Config file not found')

# iterate over the dvr recordings directory
for show in os.listdir(dvrdir):
    # skip if show isn't a directory or it's the Live TV dir
    if not os.path.isdir(os.path.join(dvrdir, show)) or show == "Live TV":
        continue

    # if we have custom configuration for this show, use it
    if show in episodes:
        maxeps = episodes[show]
    else:
        maxeps = episodes['default']

    # iterate over episodes
    files = os.listdir(os.path.join(dvrdir, show))

    # if the number of files is greater than the maximum defined...
    if len(files) > maxeps:
        #print show, "has too many episodes"
        # build a dictionary of {filename: ctime}
        files_dict = dict ([ (f, os.lstat(os.path.join(dvrdir, show, f)).st_ctime) for f in files ])
        # build queue object of episodes, oldest episode first
        file_queue = deque(sorted(files_dict, key=files_dict.__getitem__))

        # delete episodes from disk[/queue] until we satisfy maxeps
        while len(file_queue) > maxeps:
            remove_ep = file_queue.popleft()
            #print "deleting episode", remove_ep
            os.remove(os.path.join(dvrdir, show, remove_ep))
