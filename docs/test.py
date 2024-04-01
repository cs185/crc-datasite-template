import pandas as pd
import re
import time
# from env import *
import os
from datetime import date
import json
import pickle
import sys


def load_data(mode, datadir):
	print("loading -->",mode)
	columns=[
		"ads_cnt",
		"dir_cnt",
		"file_cnt",
		"has_subdirs",
		"lin",
		"log_size_sum",
		"log_size_sum_overflow",
		"name",
		"other_cnt",
		"parent",
		"phys_size_sum",
		"container",
		"enforced",
		"id",
		"include_snapshots",
		"linked",
		"notifications",
		"path",
		"persona",
		"ready",
		"thresholds__advisory",
		"thresholds__advisory_exceeded",
		"thresholds__advisory_last_exceeded",
		"thresholds__hard",
		"thresholds__hard_exceeded",
		"thresholds__hard_last_exceeded",
		"thresholds__percent_advisory",
		"thresholds__percent_soft",
		"thresholds__soft",
		"thresholds__soft_exceeded",
		"thresholds__soft_grace",
		"thresholds__soft_last_exceeded",
		"thresholds_include_overhead",
		"type",
		"usage__inodes",
		"usage__logical",
		"usage__physical"
		"date",
		"filename"
	]

	# picklefilepath=os.path.join(datadir,'%s.pickle' %mode)

	# if os.path.exists(picklefilepath):
	# 	with open(picklefilepath, 'rb') as f:
	# 		df=pickle.load(f)
	# 	already_loaded_files=list(df['filename'].unique())
	# else:
	df=pd.DataFrame(columns=columns)
	# 	already_loaded_files=[]
	# 	with open(picklefilepath, 'wb') as f:
	# 		pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)

	subkeys=[
		"thresholds__advisory",
		"thresholds__advisory_exceeded",
		"thresholds__advisory_last_exceeded",
		"thresholds__hard",
		"thresholds__hard_exceeded",
		"thresholds__hard_last_exceeded",
		"thresholds__percent_advisory",
		"thresholds__percent_soft",
		"thresholds__soft",
		"thresholds__soft_exceeded",
		"thresholds__soft_grace",
		"thresholds__soft_last_exceeded",
		"usage__inodes",
		"usage__logical",
		"usage__physical"
	]

	# find all filenames start with "nfs" or "smb"
	if mode=="nfs":
		filenames=[f for f in os.listdir(datadir) if re.match("nfs-[0-9]+\.json",f)]
	elif mode=="smb":
		filenames=[f for f in os.listdir(datadir) if re.match("smb-[0-9]+\.json",f)]

	c=0
	last_c=0
	updatestep=50
	# already_loaded=[f for f in filenames if f in already_loaded_files]

	# print("already loaded %d of %d files" %(len(already_loaded),len(filenames)))

	# filenames=[f for f in filenames if f not in already_loaded_files]

	print("Loading %d files" %len(filenames))

	st=time.time()

	# find all filenames start with "quota"
	quotafilenamelist=[f for f in os.listdir(datadir) if f.startswith("quota")]

	dfrows=[]

	# iterate over files
	for filename in filenames:
		filepath=os.path.join(datadir,filename)
		# get the starting figures
		filedatestr=re.search("[0-9]+",filename).group(0)
		yyyy=int(filedatestr[0:4])
		mm=int(filedatestr[4:6])
		dd=int(filedatestr[6:8])

		# get the quota files at the same day
		quotafilenameshortlist=[f for f in quotafilenamelist if f.startswith("quota-%s" %filedatestr[:8])]
	
		if len(quotafilenameshortlist)!=0:
			quotafilename=quotafilenameshortlist[0]
			quotafilepath=os.path.join(datadir,quotafilename)
			# read from "nfs" or "smb" files
			d=open(filepath)
			t=d.read()
			d.close()
			data=json.loads(t)

			# read from "quota" files
			d=open(quotafilepath)
			t=d.read()
			d.close()
			quota_data=json.loads(t)


			quota_by_netid={}
			# iterate over "quota" field, which is the field we care about
			if 'quotas' in quota_data: 
				for quota in quota_data['quotas']:
					quotadata=dict(quota)
					qp=quotadata['path']
					quotadatakeys=list(quotadata.keys())
					#flatten the dict
					topkeys=[]

					# the long keys defined above
					for k in subkeys:
						try:
							# topkey: threshold, usage
							topkey,subkey=k.split("__")
							if topkey in quotadata:
								if subkey in quotadata[topkey]:
									qdv=quotadata[topkey][subkey]
								else:
									qdv=None
							else:
								qdv=None

							# set the key in subkeys as a key in quotadata with value of the subkeys in the data
							quotadata[k]=qdv

							topkeys.append(topkey)
						except:
							print("failed with key %s on file %s" %(k,quotafilepath))
							# pretty print the data
							print(json.dumps(quotadata,indent=2))
							exit()

					# delete the top key fields from the quota data
					for topkey in list(set(topkeys)):
						del(quotadata[topkey])

					# iterate over the quota paths (not really the file path)
					if '/%s/' %mode in qp:
						# get the word after the slash after the mode in this path (possibly netid)
						identifier=re.search('(?<=/%s/)[a-z|A-Z|0-9|_|-]+'%mode,qp).group(0)
						# put this quota data to quota_by_netid as value with key as the identifier
						if identifier not in quota_by_netid:
							quota_by_netid[identifier]=quotadata
						else:
							# get the key (field) from the quotadata
							for k in quotadata:
								# get the value corresponding to the key
								qdv=quotadata[k]
								# accumulate the numeric field of each quota data in quota_by_netid
								if type(qdv)==int:
									if quota_by_netid[identifier][k] is None:
										quota_by_netid[identifier][k]=qdv
									else:
										quota_by_netid[identifier][k]+=qdv

				# iterate over "usage_data" in nfs file,
				# which is the list of usage data that takes up the majority
				if 'usage_data' in data:
					for item in data['usage_data']:
						itemdict=dict(item)

						itemdict['filename']=filename
						identifier=itemdict['name']
						# this usage data is from the same day the file is created. So just put the date into the data
						itemdict['date']=date(yyyy, mm, dd)
						# merge quota into usage:
						# put all the values in the quota data with the same identifier to the current usage data
						if identifier in quota_by_netid:
							quota=quota_by_netid[identifier]
							for k in quota:
								itemdict[k]=quota[k]

							# TODO: why do we need this?
							itemdictrow={k:itemdict[k] for k in itemdict}
							dfrows.append(itemdictrow)
# 							if identifier =="georgep":
# 								del(itemdictrow['date'])
# 								print(json.dumps(itemdictrow,indent=2))
		# one file iterated, one c increment
		c+=1
		if (last_c-c)%updatestep==0:
			steptime=time.time()-st
			print("loaded",c,"in",steptime,"seconds")
			last_c=c
			st=time.time()

	# put the merged data (that is merged from usage data from nfs file and quota data from quota file)
	# into a dataframe
	df=pd.DataFrame.from_records(dfrows)
	df=df.sort_values(by=['name'])
	return df

# import pandas as pd
#
#
# class DataLoader:
#     def __init__(self, config):
#         self.config = config
#         self.data_df = pd.read_csv(self.config["data_dir"], header=None)
#         if config["target_cols"]:
#             self.data_df = self.data_df[["target_cols"]]
#
#     def clean_data(self, filter_funcs):
#         for col, filter_func in filter_funcs:
#             self.data_df = self.data_df.drop(labels=filter_func(self.data_df[col]))
#
#     def map_data(self, map_funcs):
#         for col, map_func in map_funcs:
#             self.data_df[col] = self.data_df[col].apply(map_func, axis=0)
#
#     def get_data(self):
#         return self.data_df


import logging

import dash
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import numpy as np
import pandas as pd
import json
import re
import flask


def init_dashboard(server, data_dir):
	dash_app = Dash(__name__, server=server, routes_pathname_prefix='/dash/')

	df = pd.read_csv(data_dir)

	date_col = server.config["DATE_COL"]
	ratio_cols = server.config["RATIO_COLS"]
	dropdown_col = server.config["DROP_DOWN_COL"]

	# make the data frame sorted by the date
	df[date_col] = pd.to_datetime(df[date_col], format='%Y-%m-%d')
	df = df.sort_values(date_col)

	# parse date range
	daterange = list(df[date_col].unique())

	# parse RATIO_COLS values, which is the groups of the data
	groups = ratio_cols if ratio_cols else None

	# parse dropdown values
	targets = df[dropdown_col].unique() if dropdown_col else None

	# parse the other columns as the data shown in the graph as options
	data_cols = [col for col in df.columns if col not in [date_col, dropdown_col] + groups]

	controls = dbc.Card(
		[
			dcc.Dropdown(
				targets,
				targets[0] if targets else None,
				id='dropdown',
				multi=False
			),

			dcc.DatePickerRange(
				id='daterangepicker',
				min_date_allowed=pd.Timestamp(min(daterange)),
				max_date_allowed=pd.Timestamp(max(daterange)),
				start_date=pd.Timestamp(min(daterange)),
				end_date=pd.Timestamp(max(daterange))
			),

			dcc.RadioItems(
				groups,
				groups[0] if groups else None,
				inline=True,
				id='radio',
				inputStyle={"marginLeft": "10px", "marginRight": "3px"}
			) if groups else None,

			dcc.Checklist(
				data_cols,
				[data_cols[0]],
				inline=False,
				id='checklist'
			),

			html.Hr()
		]
	)

	dash_app.layout = dbc.Container(
		[
			dbc.Row(
				[
					dbc.Col(
						html.H1(
							server.config["SITE_NAME"],
							style={"margin": "10px"}
						)
					),
					dbc.Col(
						html.H6(
							f"By {server.config['AUTHOR']}"
						)
					)
				],
			),
			dbc.Row(
				[
					dbc.Col(
						html.Div(
							[controls]
						),
						width=12, xs=12, sm=12, md=12, lg=6
					),
					dbc.Col(
						html.Div(
							[dcc.Graph(id="graph")]
						),
						width=12, xs=12, sm=12, md=12, lg=6
					)
				]
			),
		]
	)

	@callback(
		Output('graph', 'figure'),
		# get the dates from the date range picker
		Input('daterangepicker', 'start_date'),
		Input('daterangepicker', 'end_date'),
		Input('checklist', 'value'),
		Input('dropdown', 'value'),
		Input('radio', 'value'),
	)
	def update_graph(start_date, end_date, column_names, target=None, group=None):
		try:
			data = df

			if target:
				data = data[data[dropdown_col] == target]

			start_date = pd.to_datetime(start_date)
			end_date = pd.to_datetime(end_date)

			# data[date_col] = pd.to_datetime(df[date_col], format='%y-%m-%d')

			data = data[(data[date_col] >= start_date) & (data[date_col] <= end_date)]

			fig = go.Figure()

			for column_name in column_names:
				fig.add_trace(
					go.Scatter(
						x=data[date_col],
						y=data[column_name],
						# color=group,
						mode='lines',
						name=column_name
					)
				)

			return fig
		except Exception as e:
			logging.exception("Error in callback")
			return html.Div(f"An error occurred: {e}")

	return dash_app

# if __name__ == '__main__':
# 	dash_app.run(debug=True, host=dash_app.server.config['APP_HOST'], port=dash_app.server.config['APP_PORT'])

