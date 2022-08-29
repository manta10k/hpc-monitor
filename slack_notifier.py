#!/usr/bin/env python
__author__ = 'Moreno Zolfo (moreno.zolfo@oist.jp)'
__version__ = '0.2'
__date__ = '26 Aug 2022'

import requests
import json
import os
import argparse
import sys
import time
import math    
import numpy as np

import subprocess
from conf import SLACK_Conf
import psutil
## uncomment this for standalone use 
##class SLACK_Conf:
##	wb_url = ###WEBHOOK###
##	data_folder = "/home/moreno.zolfo/"
##	notification_limit = 900 #15 min

parser=argparse.ArgumentParser()

parser.add_argument('param', help="The parameter for which the alert is launched",choices=['storage-bucket','report'])
parser.add_argument('channel', help="The channel where an alert is launched", choices=['private','public'])

#parser.add_argument('--value',default="", help="optional additional message to display in the notification")
args = parser.parse_args()
myhost = os.uname()[1]
loads=psutil.getloadavg()
numcores=psutil.cpu_count()

# this defines when a trigger is launched basing on
# the load-per-core at 1, 5 and 15 minutes
# e.g. 2 means "2x the number of cores"

load_triggers=(2.2, 1.6, 1.4)

# these are only for visualization purposes
# the actual triggering of the notification 
# is based on Glances config file

cpu_warning_perc = 95
memory_warning_perc = 90
iowait_warning_perc = 20
temperature_warning = 90
data=None

def get_report_deigo(conf):
	
	rp = {}
	rt = 0
	for pathAlias in ['Flash','Bucket']:
		sshProcess = subprocess.Popen(['ssh','deigo','df -h',conf.pathAliases[pathAlias],'|','tail -n1'],stdout = subprocess.PIPE,universal_newlines=True)
		for line in sshProcess.stdout:
			_,size,used,avail,use_percent,mnt = line.strip().split()

			if int(use_percent.replace('%','')) > 10:
				rt = 1
				if int(use_percent.replace('%','')) > 90:
					fl=':large_red_square:'
					color='#eb0000'
				else:
					fl=':large_yellow_square:'
					color='#eb9900'
			else:
				fl=':large_green_square:'
				color='#13be05'

		rp[pathAlias]={

			'size':size,
			'used':used,
			'avail':avail,
			'use_percent':use_percent,
			'heading':'*{}*'.format(pathAlias),
			'color':color,
			'ffields':[
				{
					"title": "Mountpoint",
					"value": '`{}`'.format(conf.pathAliases[pathAlias]),
					'short':True
				},
				{
					"title": "Used",
					"value": '{} of {}'.format(use_percent,size),
					'short':True
				},
				{
					"title": "Available",
					"value": '{}'.format(avail),
					'short':True
				}
			]
		}

	return (rt,rp)

if args.param == 'storage-bucket':

	rt,storage = get_report_deigo(SLACK_Conf)

	if rt:
		message=":floppy_disk: *Storage Alert*"

		data = {'text':message,'attachments':[]}

		for sto in storage.keys():
			print(sto)
			data['attachments'].append({'text':storage[sto]['heading'],'color':storage[sto]['color'],"footer": 'HPC notifier from {}'.format(myhost),'fields':storage[sto]['ffields']})


# Temporary file to avoid too many notifications 
# if the condition persists
# limit can be set in seconds as
# SLACK_Conf.notification_limit
if data:
	tpf = SLACK_Conf.data_folder+'/slack_notify_'+myhost+'_'+args.param+'.tmp'

	if os.path.isfile(tpf):
		lt= os.path.getmtime(tpf)
	else:
		lt=0

	ct= time.time()
	wb_url = SLACK_Conf.wb_url if args.channel == 'private' else  SLACK_Conf.wb_url_public # string containing the webhook url

	if ct-lt > SLACK_Conf.notification_limit :

		signalFile = open(tpf,'w')
		signalFile.write(str(lt)+' '+str(ct))
		signalFile.close()

		response = requests.post(wb_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})

else:
	print("No data!")