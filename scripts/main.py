
# main script to execute. can be changed to suit the needs of whatever interface is built.

from get_input import get_test_plants, get_test_conditions
from powerplant import PowerPlant
# from excel_read import get_plants, get_conditions
# from optimize import optimize  # why tf is this running like i called it if its not commented out
from display import display_graph


plants: list[PowerPlant] = get_test_plants()
conditions: list[float] = get_test_conditions()

for p in plants: print(p)
for c in conditions: print(c)

# best_ans: list[int] = optimize('cost', plants, conditions)
# display_graph('cost', best_ans, plants)

