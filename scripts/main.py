
# main script to execute. can be changed to suit the needs of whatever interface is built.


from powerplant import PowerPlant
from excel_read import get_plants, get_conditions
from optimize import optimize


excel_path = 'git_ignore\CE4321_GridOptimizer_v3.xlsx'


plants: list[PowerPlant] = get_plants(excel_path)
conditions: list[float] = get_conditions(excel_path)


optimize('cost', plants, conditions)

