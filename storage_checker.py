#!/usr/bin/env python

__author__ = 'Moreno Zolfo (moreno.zolfo@oist.jp)'
__version__ = '0.2'
__date__ = '26 Aug 2022'


import os, sys
import argparse
import configparser
from hpc_report import *

parser=argparse.ArgumentParser()

parser.add_argument('param', help="The parameter for which the alert is launched",choices=['storage','report'])
parser.add_argument('channel', help="The channel name where an alert is launched")

config = configparser.ConfigParser()
config.read('hpc.conf')

args = parser.parse_args()
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