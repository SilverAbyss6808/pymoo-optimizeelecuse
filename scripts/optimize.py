
# this is where the actual optimization will happen
# maybe make a copy of this and remove annotations when done. 
#   put the annotated version in git_ignore for reference


import string
import numpy as np
from powerplant import PowerPlant
from excel_read import get_conditions, get_plants  # DELETE THIS WHEN DONE TESTING THIS FILE

from pymoo.algorithms.soo.nonconvex.ga import GA as gen_alg 
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
    population_size = 100  # will be used later in _evaluate for finding "x" array dimensions. default to 100
    # population size is like amount of people, n_var (i think) is like number of genes in a body
    num_gens = 100  # number of generations to run. small for testing :P
    
    class CostOptProblem(ElementwiseProblem):
        def __init__(self):

            # n_var is number of decision (design?) vars; for now is just amount of power from each plant
            #   - it's what's changed each run (each plant's energy output, so must = number of plants)
            #   - also number of columns in input
            # n_obj is number of objectives; WILL STAY 1 BECAUSE SINGLE OBJECTIVE, objective is cost (minimize)

            # xl and xu (upper and lower bounds for x/cost) here
            xl: list[float] = []
            xu: list[float] = []

            for p in plants:  # finding min and max possible costs for plants
                xl.append(round(p.plant_cost * p.min_output, 2))  # can't just put 0 because some plants NEED to output a little
                xu.append(round(p.plant_cost * p.max_output, 2))

            super().__init__(n_var=len(plants), n_obj=1, xl=np.array(xl), xu=np.array(xu))  # add n_constr=3 later

        # tells the problem whats a good/feasible solution
        def _evaluate(self, x, out):
            # x definition from docs: 
            # "x is a one-dimensional array of length [n_var] and is called [pop_size] times in each iteration"
            #   - so here it's length 16
            #   - numpy array ??
            # x is array of random costs between xl and xu
            # f is objective function; this should calculate cost per (times) megawatt.

            total_mw: float = 0

            for ind, cost in enumerate(x):  # i know this is a lot. bear with me
                p = plants[ind]
                c = p.plant_cost
                mw = cost/c
                mi = p.min_output
                ma = p.max_output
                bt = mw >= mi and mw <= ma
                if bt == False: print(f'Warning: amount of mW produced by {p.name} lies out of bounds.')
                total_mw += mw
                # print(f'plant mW: {round(mw, 2)}, min: {mi}, max: {ma}, between? {bt}')  # just for testing

            # print(f'Cost for {round(total_mw, 2)} mW is {round(x.sum(), 2)}')
            out["F"] = np.round(x.sum(), 2)  # will be something like (x (cost) * decision var (mW))
            # out["G"] =   # TODO array of constraints---just get it working first

    alg = gen_alg(
        pop_size=population_size,
        eliminate_duplicates=True
    )

    result = minimize(
        problem=CostOptProblem(),
        algorithm=alg,  # defined directly above this
        termination=get_termination("n_gen", num_gens),
        save_history=True
    )

    # print best cost achieved
    print(f'Best cost {result.pop.get("F").min()}')

    # put entire run history into variable for easier access
    history = result.history

    # print each gen's best cost found
    # for run in history:
    #     print(f'Run {run.n_gen} best cost: {run.pop.get("F").min()}')  # show generation's best sum


# TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY.
plants = get_plants('git_ignore\\CE4321_GridOptimizer_v3.xlsx')
conditions = get_conditions('git_ignore\\CE4321_GridOptimizer_v3.xlsx')

optimize('cost', plants, conditions)
