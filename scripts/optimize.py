
# this is where the actual optimization will happen
# maybe make a copy of this and remove annotations when done. 
#   put the annotated version in git_ignore for reference


import string
import numpy as np
from powerplant import PowerPlant
from excel_read import get_conditions, get_plants  # DELETE THIS WHEN DONE TESTING THIS FILE

from pymoo.algorithms.soo.nonconvex.ga import GA as gen_alg 
from pymoo.core.population import Population
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.termination import get_termination


# only one visible to main to keep things neat
def optimize(opt_type: string, plants: list[PowerPlant], conditions: list[float]):
    try:  # can add more types of optimization later (carbon, water use, etc)
        if opt_type == 'cost':
            # TODO MAKE THIS INTO A NUMPY ARRAY MAYBE ???
            opt_cost(plants, conditions)
        else:
            raise Exception(f'Type {opt_type} not recognized (or not yet implemented).')
    except Exception as e:
        print(e)


# DEFINING THE OPTIMIZATION FUNCTION FOR COST!!!
# I REALLY WISH I COULD PUT MARKDOWN IN HERE. INSTEAD ILL JUST YELL IG
def opt_cost(plants: list[PowerPlant], conditions: list[float]):

    # easy access to important variables!!
    population_size = 100  # will be used later in _evaluate for finding "x" array dimensions
    # TODO what exactly is this? wrap your little baby brain around it
    num_gens = 10  # number of generations to run. small for testing :P

    # this will be a list of costs..? for now at least........???????
    # or maybe a numpy array where only the cost is accessed? is that possible
    initial_population = Population().new()  # TODO how do i initialize a population? like how do i add stuff. theres no append
    for plant in plants:
        # initial_population.new()  # WHY IS "CUMSUM" AN OPTION HERE. WHO THE FUCK MADE THAT.
        pass  # so the file name isn't red and evil
    
    class CostOptProblem(ElementwiseProblem):
        def __init__(self):

            # n_var is number of decision (design?) vars; for now is just amount of power from each plant
            #   - it's what's changed each run (each plant's energy output, so must = number of plants)
            #   - also number of columns in input
            # n_obj is number of objectives; WILL STAY 1 BECAUSE SINGLE OBJECTIVE, objective is cost (minimize)
            # xl and xu (upper and lower bounds for x) will be defined here, eventually. not now though.
            super().__init__(n_var=len(plants), n_obj=1)

        # tells the problem whats a good/feasible solution
        def _evaluate(self, x, out):
            # x definition from docs: 
            # "x is a one-dimensional array of length [n_var] and is called [pop_size] times in each iteration"
            #   - so here it's [100x1] ([16x1]?)
            #   - numpy array !!
            #   - trying to really figure out where x comes from. provided by initial population? my brain hurts
            # f is objective function; this should calculate cost x megawatt.
            out["F"] = x.sum()  # will be something like (x (cost) * decision var (mW)).sum()
            # out["G"] =   # TODO array of constraints---just get it working first

    alg = gen_alg(
        pop_size=population_size,
        sampling=initial_population,  # correct to have sampling here?
        eliminate_duplicates=True
    )

    result = minimize(
        problem=CostOptProblem(),
        algorithm=alg,  # defined directly above this
        termination=get_termination("n_gen", num_gens),
        verbose=True,
        save_history=True
    )

    # this stuff's all just printing. can ignore for now.

    # print best sum achieved
    print(f'Best cost {result.pop.get("F").min()}')

    # put entire run history into variable for easier access
    history = result.history

    # print statement from onemax
    for run in history:
        index = 0
        print(f'Run {run.n_gen}:\n'  # print generation number
            f'       ', end='')
        for bit in run.opt[0].X:
            index = index + 1
            print(f'{int(bit)}', end='')
        print(f'\n'
              f'       Run {run.n_gen} sum: {run.pop.get("F").min()}')  # show generation's best sum


# TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY.
plants = get_plants('git_ignore\CE4321_GridOptimizer_v3.xlsx')
conditions = get_conditions('git_ignore\CE4321_GridOptimizer_v3.xlsx')

for plant in plants:
    print(str(plant))
for cond in conditions:
    print(cond)

# optimize('cost', plants, conditions)
