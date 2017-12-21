from timeit import Timer
import bs


price = Timer("bs.bs_option_price('C', 101, 90, .32, 0, 50)", globals=globals())
delta = Timer("bs.bs_option_delta('C', 101, 90, .32, 0, 50)", globals=globals())
gamma = Timer("bs.bs_option_gamma('C', 101, 90, .32, 0, 50)", globals=globals())
vega = Timer("bs.bs_option_vega('C', 101, 90, .32, 0, 50)", globals=globals())
rho = Timer("bs.bs_option_rho('C', 101, 90, .32, 0, 50)", globals=globals())
implied_vol = Timer("bs.bs_option_implied_vol('C', 101, 90, .32, 0, 50, 12.7)", globals=globals())

print('bs_option_price average: ' + str(price.timeit(number=1000) / 1e6) + '.s')
print('bs_option_delta average: ' + str(delta.timeit(number=1000) / 1e6) + '.s')
print('bs_option_gamma average: ' + str(gamma.timeit(number=1000) / 1e6) + '.s')
print('bs_option_vega average: ' + str(vega.timeit(number=1000) / 1e6) + '.s')
print('bs_option_rho average: ' + str(rho.timeit(number=1000) / 1e6) + '.s')
print('bs_option_implied_vol average: ' + str(implied_vol.timeit(number=1000) / 1e6) + '.s')

print('custom test result: ' + str(price.timeit(number=480000) + implied_vol.timeit(number=480000)) + 's')
