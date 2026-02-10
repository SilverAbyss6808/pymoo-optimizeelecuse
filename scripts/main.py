
# main script to execute. can be changed to suit the needs of whatever interface is built.

from get_input import get_test_plants, get_test_conditions
from optimize import optimize


optimize('cost_water_carbon', get_test_plants(), get_test_conditions(), save_best=True)

