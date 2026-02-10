
# main script to execute. can be changed to suit the needs of whatever interface is built.

from get_input import get_test_plants, get_test_conditions
from powerplant import PowerPlant
from optimize import optimize


plants: list[PowerPlant] = get_test_plants()
conditions: list[float] = get_test_conditions()


optimize('cost_water_carbon', plants, conditions, save_best=True)

