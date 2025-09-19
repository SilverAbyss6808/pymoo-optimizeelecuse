
# main script to execute. can be changed to suit the needs of whatever interface is built.

from PowerPlant import PowerPlant
from excel_read import get_plants, get_conditions

excel_path = 'CE4321_GridOptimizer_v3.xlsx'

plants: list[PowerPlant] = get_plants(excel_path)
conditions: list[float] = get_conditions(excel_path)

