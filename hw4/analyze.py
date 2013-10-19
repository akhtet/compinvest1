
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

	#ldt_timestamps = du.getNYSEdays(min(ls_dates), max(ls_dates) + dt.timedelta(days=1), dt.timedelta(hours=16))
	ldt_timestamps = du.getNYSEdays(min(ls_dates), max(ls_dates), dt.timedelta(hours=16))
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

	ts_y = copy.deepcopy(ts_x)
	tsu.returnize0(ts_y)
	print ts_y

	avg_rets = np.average(ts_y)
	std_rets = np.std(ts_y)

	total_rets = ts_x[-1] / ts_x[0] 

	k = np.sqrt(252)
	sharpe = k * avg_rets / std_rets
	
	return std_rets, avg_rets, total_rets, sharpe


if __name__ == '__main__':

	fname = sys.argv[1]
	bench = sys.argv[2]

	ts_value = read_value_data(fname)
#	print ts_value

	ts_bench = read_bench_data(ts_value.index, bench)
#	print ts_bench

	stats_value = analyze_ts(ts_value)
	stats_bench = analyze_ts(ts_bench)

	print 'Details of the Performance of the portfolio'

	print 'Data Range : ', min(ts_value.index),'to', max(ts_value.index)

	print 'Sharpe Ratio of Fund :', stats_value[3]

	print 'Sharpe Ratio of %s :' % (bench), stats_bench[3]
	
	print 'Total Return of Fund :', stats_value[2]

	print 'Total Return of %s :' % (bench), stats_bench[2]

	print 'Standard Deviation of Fund :', stats_value[0]

	print 'Standard Deviation of %s :' % (bench), stats_bench[0]

	print 'Average Daily Return of Fund :', stats_value[1]

	print 'Average Daily Return of %s :' % (bench), stats_bench[1]

	tsu.returnize0(ts_value)
	tsu.returnize0(ts_bench)

	plt.clf()
	fig = plt.figure()
	fig.add_subplot(111)
	plt.plot(ts_value.index, ts_value, alpha=0.4)
	plt.plot(ts_bench.index, ts_bench, alpha=0.4)
	plt.legend(['Fund', 'Bench'])
	fig.autofmt_xdate(rotation=45)
	plt.savefig('fund_vs_bench.pdf', format='pdf')
