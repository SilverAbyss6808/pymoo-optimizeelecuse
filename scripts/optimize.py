
# this is where the actual optimization will happen


import pymoo
import string
from powerplant import PowerPlant
from excel_read import get_conditions, get_plants  # DELETE THIS WHEN DONE TESTING THIS FILE


# only one visible to main to keep things neat
def optimize(opt_type: string, plants: list[PowerPlant], conditions: list[float]):
    try:  # can add more types of optimization later (carbon, water use, etc)
        if opt_type == 'cost':
            opt_cost(plants, conditions)
        else:
            raise Exception(f'Type {opt_type} not recognized or not yet implemented.')
    except Exception as e:
        print(e)


def opt_cost(plants: list[PowerPlant], conditions: list[float]):
    for plant in plants:
        print(str(plant))
    for cond in conditions:
        print(cond)

# TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY.
plants = get_plants('git_ignore\CE4321_GridOptimizer_v3.xlsx')
conditions = get_conditions('git_ignore\CE4321_GridOptimizer_v3.xlsx')

optimize('cost', plants, conditions)
