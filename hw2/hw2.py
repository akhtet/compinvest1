
import pandas as pd
import numpy as np

import math
import copy
import datetime as dt

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep


def find_events(ls_symbols, d_data):

	df_close = d_data['actual_close']

	print 'Finding Events'

	# Creating an empty dataframe
	df_events = copy.deepcopy(df_close)
	df_events = df_events * np.NAN

	ldt_timestamps = df_close.index

	n_events = 0

	target = raw_input("Target:")
	target = target.strip()
	target = int(target) * 1.0

	for s_sym in ls_symbols:
		for i in range(1, len(ldt_timestamps)):
			# Do something here
			f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]] 
			f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]

			if f_symprice_today < target and f_symprice_yest >= target :
				df_events[s_sym].ix[ldt_timestamps[i]] = 1
				n_events = n_events + 1	

	print n_events
	return df_events



if __name__ == '__main__':
	
	dt_start = dt.datetime(2008, 1, 1)
	dt_end = dt.datetime(2009, 12, 31)

	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

	dataobj = da.DataAccess('Yahoo')

	sym_list_name = raw_input('Enter Symbol List Name:')
	ls_symbols = dataobj.get_symbols_from_list(sym_list_name.strip())
	#ls_symbols = dataobj.get_symbols_from_list("sp5002008")
	#ls_symbols = dataobj.get_symbols_from_list("sp5002012")
	ls_symbols.append('SPY')
	
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
	ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	# How exactly does this work?
	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
		d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)

	df_events = find_events(ls_symbols, d_data)

	print "Creating Study"
	ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
		s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')
