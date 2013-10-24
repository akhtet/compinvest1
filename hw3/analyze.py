
import pandas as pd
import numpy as np

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import sys
import csv
import datetime as dt


def read_value_data(fname):

	dc_fund = dict()
	
	reader = csv.reader(open(fname, 'rU'), delimiter=',')
	for row in reader:
		timestamp =dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16, 0 , 0)
		dc_fund[timestamp] = float(row[3])

	print 'The final value of the portfolio using the sample file is --', ','.join(row)

	ts_fund = pd.TimeSeries(index=sorted(dc_fund.keys()))
	for key in sorted(dc_fund.keys()):
		ts_fund[key] = dc_fund[key]

	return ts_fund	


def read_bench_data(ls_dates, bench):

	ldt_timestamps = du.getNYSEdays(min(ls_dates), max(ls_dates) + dt.timedelta(days=1), dt.timedelta(hours=16))
	dataobj = da.DataAccess('Yahoo', cachestalltime=0)
	ldf_data = dataobj.get_data(ldt_timestamps, [bench], ['close'])

	d_data = dict(zip(['close'], ldf_data))
	d_data['close'] = d_data['close'].fillna(method='ffill')	
	d_data['close'] = d_data['close'].fillna(method='bfill')	
	d_data['close'] = d_data['close'].fillna(1.0)

	d_close = d_data['close'].reindex(index=ls_dates, columns=[bench])

	ts_bench = pd.TimeSeries(index=sorted(d_close.index))
	for timestamp in d_close.index:
		ts_bench[timestamp] = d_close[bench].ix[timestamp]

	return ts_bench	
	

def analyze_ts(ts_x):

	tsu.returnize0(ts_x)
	print ts_x

	avg_rets = np.average(ts_x)
	std_rets = np.std(ts_x)
	
	return std_rets, avg_rets

if __name__ == '__main__':

	fname = sys.argv[1]
	bench = sys.argv[2]

#	ls_dates = []

	ts_value = read_value_data(fname)
	print ts_value

	ts_bench = read_bench_data(ts_value.index, bench)
	print ts_bench

	stats_value = analyze_ts(ts_value)
	stats_bench = analyze_ts(ts_bench)

	print 'Details of the Performance of the portfolio'

	print 'Data Range : ', min(ts_value.index),'to', max(ts_value.index)

	print 'Sharpe Ratio of Fund :'

	print 'Sharpe Ratio of %s :' % (bench) 
	
	print 'Total Return of Fund :'

	print 'Total Return of %s :' % (bench)

	print 'Standard Deviation of Fund :', stats_value[0]

	print 'Standard Deviation of %s :' % (bench), stats_bench[0]

	print 'Average Daily Return of Fund :', stats_value[1]

	print 'Average Daily Return of %s' % (bench), stats_value[1]


