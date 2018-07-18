import Tier_Pull
import Tier_Analysis
import Tier_Metrics
import time

start_time_X = time.clock()

Tier_Pull.main()
Tier_Analysis.main()
Tier_Metrics.main()

print(time.clock() - start_time_X, "seconds")