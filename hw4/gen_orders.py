
import pandas as pd
import numpy as np

import math
import copy
import datetime as dt

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep


def find_events(d_data, target, action, days_hold, amount, order_file):

	print 'Finding Events'
	
	# Creating an empty dataframe
	df_close = d_data['actual_close']
	df_events = copy.deepcopy(df_close)
	df_events = df_events * np.NAN

	ldt_timestamps = df_close.index
	ls_symbols = df_close.columns
	n_events = 0

	f = open(order_file, 'w')

	for s_sym in ls_symbols:
		for i in range(1, len(ldt_timestamps)):
			# Do something here
			f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]] 
			f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]

			if f_symprice_today < target and f_symprice_yest >= target :
				df_events[s_sym].ix[ldt_timestamps[i]] = 1
				n_events = n_events + 1

				if action.upper() == 'BUY':
					action_r = 'SELL'
				else:
					action_r = 'BUY'

				date_hold = i + days_hold
				if date_hold >= len(ldt_timestamps):
					date_hold = -1;

				f.write("%s,%s,%s,%d\n" % (ldt_timestamps[i].strftime("%Y,%m,%d"), s_sym, action, amount))
				f.write("%s,%s,%s,%d\n" % (ldt_timestamps[date_hold].strftime("%Y,%m,%d"), s_sym, action_r, amount))

			print '\r', n_events,

	f.close()
	return df_events



if __name__ == '__main__':

	timestamp = raw_input("Enter Start Date: ")
	timestamp = timestamp.split('-')
	dt_start = dt.datetime(int(timestamp[0]), int(timestamp[1]), int(timestamp[2]))

	timestamp = raw_input("Enter End Date: ")
	timestamp = timestamp.split('-')
	dt_end = dt.datetime(int(timestamp[0]), int(timestamp[1]), int(timestamp[2]))

	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
	dataobj = da.DataAccess('Yahoo')

	sym_list_name = raw_input('Enter Symbol List Name: ')
	ls_symbols = dataobj.get_symbols_from_list(sym_list_name.strip())
	#ls_symbols = dataobj.get_symbols_from_list("sp5002008")
	#ls_symbols = dataobj.get_symbols_from_list("sp5002012")
	ls_symbols.append('SPY')

	order_file = raw_input('Enter Order File Name:')
	graph_file = raw_input('Enter Graph File Name:')
	
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	# How exactly does this work?
	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
		d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)

	target = raw_input("Enter Target:")
	target = target.strip()
	target = int(target) * 1.0


	action = raw_input("Enter Action on Event: ")
	action = action.strip().upper()

	days_hold = raw_input("Enter number of days to hold: ")
	days_hold = int(days_hold.strip())

	amount = raw_input("Enter number of shares for this action: ")
	amount = int(amount.strip())

	df_events = find_events(d_data, target, action, days_hold, amount, order_file)
	
	print "Profiling Events"
	ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
		s_filename=graph_file, b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')
