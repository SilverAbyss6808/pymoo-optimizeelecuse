
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
    num_gens = 300  # number of generations to run. small for testing :P
    
    class CostOptProblem(ElementwiseProblem):
        def __init__(self):

            # n_var is number of decision (design?) vars; for now is just amount of power from each plant
            #   - it's what's changed each run (each plant's energy output, so must = number of plants)
            #   - also number of columns in input
            # n_obj is number of objectives; WILL STAY 1 BECAUSE SINGLE OBJECTIVE, objective is cost (minimize)
            # note that x should be mw NOT COST

            # make list of plants accessible outside function
            # just to kinda save time. can be accessed like result.pop.get('plant_cost_per_mw') <-- ok maybe not
            # self.plant_cost_per_mw: list[float] = []

            # xl and xu (upper and lower bounds for x/cost) here
            xl: list[float] = []
            xu: list[float] = []

            self.cost_per_plant: list[str, float, float] = []  # plant name, power generated, total cost from plant

            for p in plants:  # finding min and max possible outputs for plants, ALL X VALS WILL BE BETWEEN THESE
                # xl.append(p.min_output)
                xl.append(p.min_output)
                xu.append(p.max_output)
                # add each plant's mw cost to list. note that wholesale cost isn't used
                # self.plant_cost_per_mw.append(p.plant_cost) 

            super().__init__(n_var=len(plants), n_obj=1, xl=np.array(xl), xu=np.array(xu), n_constr=1)

        # tells the problem what's a good/feasible solution
        def _evaluate(self, x, out):
            # x definition from docs: 
            # "x is a one-dimensional array of length [n_var] and is called [pop_size] times in each iteration"
            #   - so here it's length 16
            #   - numpy array ??
            # x is array of random mw between xl and xu
            # f is objective function; this should calculate cost per (times) megawatt.

            self.cost_per_plant = []  # reset to empty
            power_demand: float = conditions[0]  # 13600 mW right now

            constraint_violations: list[bool] = []

            for ind, mw in enumerate(x):
                p = plants[ind]
                mi = p.min_output
                ma = p.max_output

                bt = mw < mi or mw > ma  # checks if the amount of power generated is within plant's bounds
                constraint_violations.append(bt)  # adds cv boolean to end of array

                self.cost_per_plant.append([p.name, round(float(mw), 2), round(float(mw) * 1000 * p.plant_cost, 2)])  # x1000 because mw

            demand_met = power_demand - x.sum()
            if demand_met < 0: demand_met = 0  # sets to 0 if the demand was successfully met

            # print(cost_per_plant)

            out["F"] = round(x.sum(), 2)  # total mw generated
            out["G"] = sum(constraint_violations) + demand_met # <= 0 is ok, > 0 is not

    alg = gen_alg(
        pop_size=population_size,
        eliminate_duplicates=True
    )

    result = minimize(
        problem=CostOptProblem(),
        algorithm=alg,  # defined directly above this
        termination=get_termination('n_gen', num_gens),
        verbose=True,
        save_history=True
    )

    # print best solution achieved
    print('Best solution found: \nX = %s\nF = %s\nG = %s' % (result.X, result.F, result.G))

    for i, p in enumerate(result.problem.cost_per_plant):
        print(f'{i+1}. {p[0]}\n'
              f'    mW produced:    {p[1]}\n'
              f'    Total price:    ${p[2]}')

    # put entire run history into variable for easier access
    # history = result.history

    # print each gen's best cost found
    # for run in history:
    #     print(f'Run {run.n_gen} best cost: {run.pop.get("F").min()}')  # show generation's best sum


# TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY.
plants = get_plants('git_ignore\\CE4321_GridOptimizer_v3.xlsx')
conditions = get_conditions('git_ignore\\CE4321_GridOptimizer_v3.xlsx')

optimize('cost', plants, conditions)
