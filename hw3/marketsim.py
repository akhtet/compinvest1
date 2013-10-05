
import sys
import csv
import copy
import datetime

import pandas as pd
import numpy as np

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep


def read_order_file(fname):

	ls_symbols = set()
	ls_dates = set()

	reader = csv.reader(open(fname, 'rU'), delimiter=',')
	for row in reader:
		ls_symbols.add(row[3])
		ls_dates.add(datetime.datetime(int(row[0]), int(row[1]), int(row[2]), 16, 0, 0))

	return sorted(list(ls_symbols)), sorted(list(ls_dates))




def read_market_data(ls_dates, ls_symbols):

	#ls_keys = ['actual_close']
	ls_keys = ['close']

	ldt_timestamps = du.getNYSEdays(min(ls_dates), max(ls_dates) + datetime.timedelta(days=1), datetime.timedelta(hours=16))
	#dataobj = da.DataAccess('Yahoo')
	dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	
	ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
		d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)

	df_close = d_data['close']
	df_close = df_close.reindex(index=ls_dates,columns=ls_symbols)
	return df_close




def create_trade_matrix(fname, df_close, ls_symbols, ls_dates):

	df_trade = pd.DataFrame(index=ls_dates, columns=ls_symbols)
	df_trade = df_trade.fillna(0.0)

	reader = csv.reader(open(fname, 'rU'), delimiter=',')
	for row in reader:
		timestamp = datetime.datetime(int(row[0]), int(row[1]), int(row[2]), 16, 0, 0)
		symbol = row[3]
		if row[4].lower() == 'buy':
			amount = int(row[5])
		else:
			amount = -1.0 * int(row[5])
		df_trade[symbol].ix[timestamp] += amount

	return df_trade




def create_cash_series(df_trade, df_close, cash_now):

	ts_cash_delta  = pd.TimeSeries(0.0, index=df_trade.index)

	for timestamp in df_trade.index:
		for symbol in df_trade.columns:
			sym_price = df_close[symbol].ix[timestamp]
			sym_amount = df_trade[symbol].ix[timestamp]
			if sym_amount != 0:
				cash_delta  = -1 * sym_price * sym_amount
				ts_cash_delta[timestamp] += cash_delta

	ts_cash = pd.TimeSeries(0.0, index=df_trade.index)

	for timestamp in ts_cash.index:
		cash_now += ts_cash_delta[timestamp]
		ts_cash[timestamp] = cash_now
			
	return ts_cash
	



def create_fund_series(df_trade, df_close, ts_cash):

	
	# trade to holdings
	df_holding = pd.DataFrame(index=df_trade.index, columns=df_trade.columns)
	df_holding = df_holding.fillna(0.0) 

	for symbol in df_trade.columns:
		holding = 0.0
		for timestamp in df_trade.index:
			df_holding[symbol].ix[timestamp] = holding + df_trade[symbol].ix[timestamp]
			holding = df_holding[symbol].ix[timestamp]

	df_close['_CASH'] = 1.0
	print df_close
	
	df_holding['_CASH'] = ts_cash
	print df_holding
	
	ts_fund = pd.TimeSeries(0.0, index=df_trade.index)

	for timestamp in df_close.index:
#		print timestamp,
#		print df_close[:].ix[timestamp]
#		print df_holding[:].ix[timestamp]
		ts_fund[timestamp] = np.dot(df_close[:].ix[timestamp], df_holding[:].ix[timestamp])

	return ts_fund


def write_output_file(fname, ts_fund):

	writer = csv.writer(open(fname, 'wb'), delimiter=',')
	for timestamp in ts_fund.index:
		writer.writerow((timestamp.year, timestamp.month, timestamp.day, ts_fund[timestamp]))


if __name__ == '__main__':

	cash_start = int(sys.argv[1])
	order_file = sys.argv[2]
	value_file = sys.argv[3]

	ls_symbols, ls_dates = read_order_file(order_file)
	ls_symbols.append('SPY')
	#print ls_symbols
	#print ls_dates

	df_close = read_market_data(ls_dates, ls_symbols)
	print df_close
  
	df_trade = create_trade_matrix(order_file, df_close, ls_symbols, ls_dates)
	print df_trade

	ts_cash = create_cash_series(df_trade, df_close, cash_start)
	print ts_cash

	ts_fund = create_fund_series(df_trade, df_close, ts_cash)
	print ts_fund

	write_output_file(value_file, ts_fund)		
