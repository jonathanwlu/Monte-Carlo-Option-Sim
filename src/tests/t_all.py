from plot import iv_strike_plot
from plot import iv_time_plot

start_price = 98
times = 500

length = 100
center_strike = 100
strike_range = 30
num_strike = 6

center_length = 100
length_range = 30
num_lengths = 6
vol = .25
strike = 100


def test_isp():
    iv_strike_plot.plot(length, start_price, times, center_strike, strike_range, num_strike, filename='strike_test_norm', dist='normal')
    iv_strike_plot.plot(length, start_price, times, center_strike, strike_range, num_strike, filename='strike_test_unif', dist='uniform')
    iv_strike_plot.plot(length, start_price, times, center_strike, strike_range, num_strike, filename='strike_test_bs', dist='bootstrap', bs_data='spec\\stkPx.csv')
    iv_strike_plot.plot(length, start_price, times, center_strike, strike_range, num_strike, filename='strike_test_db', dist='double-bell', delta=2)
    iv_strike_plot.plot(length, start_price, times, center_strike, strike_range, num_strike, filename='strike_test_skew', dist='skewnorm', skew_a=3)
    iv_strike_plot.plot(length, start_price, times, center_strike, strike_range, num_strike, filename='strike_test_jump', dist='normal', jumps="[{'dte': 50, 'dist': 'normal', 'mean': 0, 'sd': .6, 'delta': 0, 'skew_a': 0}]")


def test_itp():
    iv_time_plot.plot(center_length, length_range, num_lengths, vol, start_price, times, strike, filename='time_test_norm', dist='normal')
    iv_time_plot.plot(center_length, length_range, num_lengths, vol, start_price, times, strike, filename='time_test_unif', dist='uniform')
    iv_time_plot.plot(center_length, length_range, num_lengths, vol, start_price, times, strike, filename='time_test_bs', dist='bootstrap', bs_data='spec\\stkPx.csv')
    iv_time_plot.plot(center_length, length_range, num_lengths, vol, start_price, times, strike, filename='time_test_db', dist='double-bell', delta=2)
    iv_time_plot.plot(center_length, length_range, num_lengths, vol, start_price, times, strike, filename='time_test_skew', dist='skewnorm', skew_a=3)
    iv_time_plot.plot(center_length, length_range, num_lengths, vol, start_price, times, strike, filename='time_test_jump', dist='normal', jumps="[{'dte': 50, 'dist': 'normal', 'mean': 0, 'sd': .6, 'delta': 0, 'skew_a': 0}]")

if __name__ == '__main__':
    test_isp()
    test_itp()
