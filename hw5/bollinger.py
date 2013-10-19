
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import sys
import csv
import copy
import datetime as dt


def get_parameters():

	symbol = raw_input("Symbol :")
	symbol = symbol.strip()

	timestamp = raw_input("Enter Start Date: ")
	timestamp = timestamp.split('-')
	dt_start = dt.datetime(int(timestamp[0]), int(timestamp[1]), int(timestamp[2]))

	timestamp = raw_input("Enter End Date: ")
	timestamp = timestamp.split('-')
	dt_end = dt.datetime(int(timestamp[0]), int(timestamp[1]), int(timestamp[2]))

	lookback = int(raw_input("Lookback period :"))

	fname  = raw_input("Report file name :")
	return symbol, dt_start, dt_end, lookback, fname	


def	read_market_data(symbol, dt_start, dt_end, lookback):

	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
	dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	ldf_data = dataobj.get_data(ldt_timestamps, [symbol], ['close'])

	d_data = dict(zip(['close'], ldf_data))
	d_data['close'] = d_data['close'].fillna(method='ffill')	
	d_data['close'] = d_data['close'].fillna(method='bfill')	
	d_data['close'] = d_data['close'].fillna(1.0)

	return d_data['close']


def get_bollinger(d_close):
	
	ts_close = pd.TimeSeries(index=sorted(d_close.index))
	ts_mean = pd.TimeSeries(index=sorted(d_close.index))
	ts_std = pd.TimeSeries(index=sorted(d_close.index))
	ts_upper = pd.TimeSeries(index=sorted(d_close.index))
	ts_lower = pd.TimeSeries(index=sorted(d_close.index))
	ts_bollinger = pd.TimeSeries(index=sorted(d_close.index))

	for timestamp in d_close.index:
		price = d_close.ix[timestamp]
		mean = np.mean(d_close.ix[0:timestamp])
		std = np.std(d_close.ix[0:timestamp])
		bollinger = (price - mean) / (std)

		ts_close[timestamp] = price
		ts_mean[timestamp] = mean
		ts_std[timestamp] = std
		ts_upper[timestamp] = mean + std
		ts_lower[timestamp] = mean - std
		ts_bollinger[timestamp] = bollinger
	
	for timestamp in sorted(ts_close.index):
		print ts_close[timestamp], ts_mean[timestamp], ts_std[timestamp]
		print ts_close[timestamp], ts_mean[timestamp], ts_std[timestamp]

	ts_dict = {}
	ts_dict['Mean'] = ts_mean
	ts_dict['Close'] = ts_close
	ts_dict['Std'] = ts_std
	ts_dict['Upper'] = ts_upper
	ts_dict['Lower'] = ts_lower
	ts_dict['Bollinger'] = ts_bollinger

	return ts_dict


def get_bollinger_2(d_close):
	
	ts_price = pd.TimeSeries(d_close, index=sorted(d_close.index))
	ts_mean = pd.rolling_mean(d_close, 20)
	ts_std = pd.rolling_std(d_close, 20)
	ts_upper = ts_mean + ts_std
	ts_lower = ts_mean - ts_std
	ts_bollinger = (ts_price - ts_mean) / ts_std

	ts_bollinger.fillna(method='bfill')
	ts_bollinger.fillna(method='ffill')
	ts_bollinger.fillna(1.0)
		
	ts_dict = {}
	ts_dict['Price'] = ts_price
	ts_dict['Mean'] = ts_mean
	ts_dict['Upper'] = ts_upper
	ts_dict['Lower'] = ts_lower

	v_up = []
	v_down = []

	for timestamp in sorted(ts_bollinger.index):
		blger = ts_bollinger[timestamp]
		print timestamp, blger
		if blger >= 1.0:
			v_up.append(timestamp)	
		elif blger <= -1.0:
			v_down.append(timestamp)
	
	return ts_dict, {'Bollinger':ts_bollinger}, v_up, v_down


def plot_data(ts_plot, ts_plot_2, v_up, v_down, filename):

	plt.clf()
	fig = plt.figure()
	fig.add_subplot(211)

	for key in sorted(ts_plot.keys()):
		plt.plot(ts_plot[key].index, ts_plot[key], alpha=0.4)

	for timestamp in v_up:
		plt.axvline(x = timestamp, linewidth=0.1, color='r')

	for timestamp in v_down:
		plt.axvline(x = timestamp, linewidth=0.1, color='g')

	plt.legend(sorted(ts_plot.keys()))
	fig.autofmt_xdate(rotation=45)

	fig.add_subplot(212)

	for key in sorted(ts_plot_2.keys()):
		plt.plot(ts_plot_2[key].index, ts_plot_2[key], alpha=0.4)

	for timestamp in v_up:
		plt.axvline(x = timestamp, linewidth=0.1, color='r')

	for timestamp in v_down:
		plt.axvline(x = timestamp, linewidth=0.1, color='g')
	
	fig.autofmt_xdate(rotation=45)
	plt.savefig(filename, format='pdf')


if __name__ == '__main__':

	symbol, dt_start, dt_end, lookback, fname = get_parameters() 

	df_close = read_market_data(symbol, dt_start, dt_end, lookback)

	ts_dict, ts_dict_2, v_up, v_down = get_bollinger_2(df_close[symbol])
	
	plot_data(ts_dict, ts_dict_2, v_up, v_down, fname)
