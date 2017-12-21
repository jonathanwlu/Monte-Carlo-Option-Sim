import unittest
import bs


class TestBS(unittest.TestCase):
    def test_option_price(self):
        self.assertTrue(bs.bs_option_price('C', 101, 90, .32, 0, 50) - 12.6055063102446 < 10e-8)
        self.assertTrue(bs.bs_option_price('call', 101, 90, .32, 0, 50) - 12.6055063102446 < 10e-8)
        self.assertTrue(bs.bs_option_price('P', 101, 90, .32, 0, 50) - 1.6055063102446 < 10e-8)
        self.assertTrue(bs.bs_option_price('put ', 101, 90, .32, 0, 50) - 1.6055063102446 < 10e-8)

    def test_option_delta(self):
        self.assertTrue(bs.bs_option_delta('C', 101, 90, .32, 0, 50) * 100 - 81.0636785229828 < 10e-8)
        self.assertTrue(bs.bs_option_delta('P', 101, 90, .32, 0, 50) * 100 - -18.9363214770173 < 10e-8)

    def test_option_gamma(self):
        self.assertTrue(bs.bs_option_gamma('C', 101, 90, .32, 0, 50) * 100 - 1.88105455349028 < 10e-8)
        self.assertTrue(bs.bs_option_gamma('P', 101, 90, .32, 0, 50) * 100 - 1.88105455349028 < 10e-8)

    def test_option_vega(self):
        self.assertTrue(bs.bs_option_vega('C', 101, 90, .32, 0, 50) * 100 - 12.1832619048599 < 10e-8)
        self.assertTrue(bs.bs_option_vega('P', 101, 90, .32, 0, 50) * 100 - 12.1832619048599 < 10e-8)

    def test_option_rho(self):
        self.assertTrue(bs.bs_option_rho('C', 101, 90, .32, 0, 50) * 100 - 13.7438113091206 < 10e-8)
        self.assertTrue(bs.bs_option_rho('P', 101, 90, .32, 0, 50) * 100 - -4.11333154802223 < 10e-8)

    def test_option_implied_vol(self):
        self.assertTrue(bs.bs_option_implied_vol('C', 101, 90, .32, 0, 50, 12.5353) - 0.31420288351383 < 10e-8)
        self.assertTrue(bs.bs_option_implied_vol('P', 101, 90, .32, 0, 50, .535) - 0.218304232561594 < 10e-8)


if __name__ == '__main__':
    unittest.main()
