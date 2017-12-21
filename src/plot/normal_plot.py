import numpy as np
import scipy.stats
import matplotlib.pyplot as plt

sample = np.random.normal(size=10000)
plt.hist(sample, bins=100, histtype='stepfilled')
print("mean " + str(np.mean(sample)))
print("sd " + str(np.std(sample)))
print("skew " + str(scipy.stats.skew(sample)))
plt.show()
