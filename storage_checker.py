#!/usr/bin/env python

__author__ = 'Moreno Zolfo (moreno.zolfo@oist.jp)'
__version__ = '0.2'
__date__ = '26 Aug 2022'


import os, sys
import argparse
import configparser
from hpc_report import *

parser=argparse.ArgumentParser()
defaultConfigFile = '{}/hpc.conf'.format(os.path.dirname(os.path.realpath(sys.argv[0])))

parser.add_argument('param', help="The parameter for which the alert is launched",choices=['storage','report'])
parser.add_argument('channel', help="The channel name where an alert is launched")
parser.add_argument('--config', help="The path to a config file with settings. Default: {}".format(defaultConfigFile),default=defaultConfigFile)

config = configparser.ConfigParser()
args = parser.parse_args()

if os.path.isfile(args.config):
	config.read(args.config)
else:
	print("Cannot access config file {}".format(args.config))
	sys.exit(1)

myhost = os.uname()[1]

data=None

if args.param == 'storage':

	rt,storage = get_report_deigo(config)

	if rt:
		message=":floppy_disk: *Storage Alert*"
		data = {'text':message,'attachments':[]}
		for sto in storage.keys():
			data['attachments'].append({'text':storage[sto]['heading'],'color':storage[sto]['color'],"footer": 'HPC notifier from {}'.format(myhost),'fields':storage[sto]['ffields']})

if data and args.channel in config['channels']:
	check_send_message(config,data,args.channel,args.param)