#!/usr/bin/env python
__author__ = 'Moreno Zolfo (moreno.zolfo@oist.jp)'
__version__ = '0.2'
__date__ = '26 Aug 2022'

import subprocess
import os
import requests
import json
import time

def check_send_message(conf,data,channel,param):

	host = os.uname()[1]

	tpf = '{}/slack_notify_{}_{}.tmp'.format(conf['paths']['data_folder'],host,param)

	lt = os.path.getmtime(tpf) if os.path.isfile(tpf) else 0
	ct= time.time()
	
	if ct-lt > int(conf['channels']['notification_limit']):

		signalFile = open(tpf,'w')
		signalFile.write(str(lt)+' '+str(ct))
		signalFile.close()

		return send_message(conf['channels'][channel],data)
	else:
		return None

def send_message(chn,data):
	return requests.post(chn, data=json.dumps(data), headers={'Content-Type': 'application/json'})


def get_report_deigo(conf):
	
	rp = {}
	rt = 0

	for pathAlias in ['Flash','Bucket']:
		sshProcess = subprocess.Popen(['ssh','deigo','df -h',conf['paths'][pathAlias],'|','tail -n1'],stdout = subprocess.PIPE,universal_newlines=True)
		for line in sshProcess.stdout:
			_,size,used,avail,use_percent,mnt = line.strip().split()


			if int(use_percent.replace('%','')) > float(conf['thr']['storage_percent_warning']):
				rt = 1
				if int(use_percent.replace('%','')) > float(conf['thr']['storage_percent_critical']):
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
					"value": '`{}`'.format(conf['paths'][pathAlias]),
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