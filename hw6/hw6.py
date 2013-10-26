
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import datetime as dt

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep


def get_parameters():

	listname = raw_input("List Name :")
	listname = listname.strip()

	timestamp = raw_input("Enter Start Date: ")
	timestamp = timestamp.split('-')
	dt_start = dt.datetime(int(timestamp[0]), int(timestamp[1]), int(timestamp[2]))

	timestamp = raw_input("Enter End Date: ")
	timestamp = timestamp.split('-')
	dt_end = dt.datetime(int(timestamp[0]), int(timestamp[1]), int(timestamp[2]))

	lookback = int(raw_input("Lookback period :"))

	n_target_a = float(raw_input("Target A :"))
	n_target_b = float(raw_input("Target B :"))

	fname  = raw_input("Report file name :")
	return listname, dt_start, dt_end, lookback, n_target_a, n_target_b, fname	




def	read_market_data(s_listname, dt_start, dt_end):

	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
	
	dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	#dataobj = da.DataAccess('Yahoo')
	ls_symbols = dataobj.get_symbols_from_list(s_listname)
	ls_symbols.append('SPY')	

	ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ['close'])

	d_data = dict(zip(['close'], ldf_data))
	d_data['close'] = d_data['close'].fillna(method='ffill')	
	d_data['close'] = d_data['close'].fillna(method='bfill')	
	d_data['close'] = d_data['close'].fillna(1.0)

	return d_data




def get_bollinger(df_close):

	df_mean = pd.DataFrame(columns=df_close.columns, index=df_close.index)
	df_mean = pd.rolling_mean(df_close, 20)
	
	df_std = pd.DataFrame(columns=df_close.columns, index=df_close.index)
	df_std = pd.rolling_std(df_close, 20)

	df_upper = pd.DataFrame(columns=df_close.columns, index=df_close.index)
	df_upper = df_mean + df_std

	df_lower = pd.DataFrame(columns=df_close.columns, index=df_close.index)
	df_lower = df_mean - df_std

	df_bollinger = pd.DataFrame(columns=df_close.columns, index=df_close.index)
	df_bollinger = (df_close - df_mean) / df_std

	for s_symbol in df_bollinger.columns:
		df_bollinger[s_symbol].fillna(method='bfill')
		df_bollinger[s_symbol].fillna(method='ffill')
		df_bollinger[s_symbol].fillna(1.0)

	return df_bollinger
	



def find_events(df_bollinger, n_target_a, n_target_b):

	df_events = pd.DataFrame(columns=df_bollinger.columns, index=df_bollinger.index)
	df_events = df_bollinger * np.NAN
	n_events = 0

	for s_symbol in df_bollinger.columns:
		for i in range(1, len(df_bollinger.index)):
			n_price_today = df_bollinger[s_symbol].ix[i]	
			n_price_yest = df_bollinger[s_symbol].ix[i - 1]	

			if n_price_today <= n_target_a and n_price_yest >= n_target_a and df_bollinger['SPY'][i] >= n_target_b:
				df_events[s_symbol][i] = 1
				n_events = n_events + 1
				print '\r', n_events, 

	print ''
	return df_events




if __name__ == '__main__':

	s_listname, dt_start, dt_end, n_lookback, n_target_a, n_target_b, s_fname = get_parameters()	

	d_data = read_market_data(s_listname, dt_start, dt_end) 

	df_bollinger = get_bollinger(d_data['close'])

	df_events = find_events(df_bollinger, n_target_a, n_target_b)

	print df_events

	ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
		s_filename=s_fname, b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')

	#gen_orders

	#market sim

	#analyze 
