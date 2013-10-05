#!/usr/bin/env python

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import sys

def simulate(dt_start, dt_end, ls_symbols, lf_port_alloc):

	global d_data, na_price

	# We need closing prices so the timestamp should be hours=16.
	dt_timeofday = dt.timedelta(hours=16)

	# Get a list of trading days between the start and the end.
	ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

	# Reading the data, now d_data is a dictionary with the keys above.
	# Timestamps and symbols are the ones that were specified before.
	ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
	d_data = dict(zip(ls_keys, ldf_data))

	for s_key in ls_keys:
		d_data[s_key] = d_data[s_key].fillna(method='ffill')	
		d_data[s_key] = d_data[s_key].fillna(method='bfill')
		d_data[s_key] = d_data[s_key].fillna(1.0)

	# Getting the numpy ndarray of close prices.
	na_price = d_data['close'].values

	if debug:
		print "na_price"
		print na_price
		raw_input("NEXT:")

	# Normalizing the prices to start at 1 and see relative returns
	na_normalized_price = na_price / na_price[0, :]
	
	if debug:
		print "na_normalized_price"
		print na_normalized_price
		raw_input("NEXT:")

	na_each_fund = na_normalized_price  * lf_port_alloc
	
	if debug:
		print "na_each_fund"
		print na_each_fund
		raw_input("NEXT:")
		
	na_total_fund = np.sum(na_each_fund, dtype=float, axis=1)
	
	if debug:
		print "na_total_fund"
		print na_total_fund
		raw_input("NEXT:")


	na_daily_rets = na_total_fund.copy()
	tsu.returnize0(na_daily_rets)
	
	if debug:
		print "na_daily_rets"
		print na_daily_rets
		raw_input("NEXT:")
	
	n_avg_rets = np.average(na_daily_rets)

	n_std_rets = np.std(na_daily_rets)

	n_cum_ret = na_total_fund[-1]

	n_sharpe = k * n_avg_rets / n_std_rets
	
	if debug:
		print "n_std_rets:", n_std_rets
		print "n_avg_rets:", n_avg_rets
		print "n_sharpe:", n_sharpe
		print "n_cum_ret:", n_cum_ret 

	return n_std_rets, n_avg_rets, n_sharpe, n_cum_ret


if __name__ == '__main__':

	if raw_input("Debug Mode? (Y/N) :") == 'Y':
		debug = True
	else:
		debug = False


	# Creating an object of the dataaccess class with Yahoo as the source.
	c_dataobj = da.DataAccess('Yahoo')
	#c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

	# List of symbols, Start and End date of the charts

	"""
	ls_symbols = ["C", "GS", "IBM", "HNZ"]
	dt_start = dt.datetime(2011, 1, 1)
	dt_end = dt.datetime(2011, 12, 31)
	"""
	ls_symbols = ["BRCM", "TXN", "AMD", "ADI"]
	dt_start = dt.datetime(2010, 1, 1)
	dt_end = dt.datetime(2010, 12, 31)

	"""
	ls_symbols = ["AAPL", "GLD", "GOOG", "XOM"]
	dt_start = dt.datetime(2011, 1, 1)
	dt_end = dt.datetime(2011, 12, 31)
	"""
	"""	
	ls_symbols = ['AXP', 'HPQ', 'IBM', 'HNZ']
	dt_start = dt.datetime(2010, 1, 1)
	dt_end = dt.datetime(2010, 12, 31)
	"""

	# Get input parameters
	"""
	ls_symbols = []
	for i in range(1, 5):
		symbol = raw_input("Enter stock symbol %d :" % (i))
		ls_symbols.append(symbol.strip())
	
	print ls_symbols

	start_date = raw_input('Enter start-date (YYYY-MM-DD):')
	parts = start_date.strip().split('-')
	dt_start = dt.datetime(int(parts[0]), int(parts[1]), int(parts[2]))

	end_date = raw_input('Enter end-date (YYYY-MM-DD):')
	parts = end_date.strip().split('-')
	dt_start = dt.datetime(int(parts[0]), int(parts[1]), int(parts[2]))
	
	print 'Start Date: ', dt_start
	print 'End Date:', dt_end
	"""

	# Keys to be read from the data, it is good to read everything in one go.
	ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

	k = np.sqrt(252)
	
	best_sharpe = None
	sim_count = 0

	increments = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

	
	for p1 in increments:
		for p2 in increments:
			for p3 in increments:
				for p4 in increments:
					if p1 + p2 + p3 + p4 == 1:
						
						ls_port_alloc = [ p1, p2, p3, p4 ]
						
						vol, daily_ret, sharpe, cum_ret = simulate(dt_start, dt_end, ls_symbols, ls_port_alloc )
						if best_sharpe is None or best_sharpe < sharpe:
							best_sharpe = sharpe
							best_port_alloc = ls_port_alloc
							best_vol = vol
							best_daily_ret = daily_ret
							best_cum_ret = cum_ret

						sim_count = sim_count + 1
						print sim_count, ls_port_alloc, sharpe, best_sharpe
						sys.stdout.flush()

	print 'Start Date: ', dt_start
	print 'End Date:', dt_end
	print 'Symbols', ls_symbols
	print 'Optimal Allocations:', best_port_alloc
	print 'Sharpe Ratio:', best_sharpe
	print 'Volatility (stdev of daily returns):', best_vol
	print 'Average Daily Return:', best_daily_ret
	print 'Cumulative Return:', best_cum_ret
