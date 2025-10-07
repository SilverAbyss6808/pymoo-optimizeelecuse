
import string
import numpy as np

from alive_progress import alive_bar
from excel_read import get_conditions, get_plants  # DELETE THIS WHEN DONE TESTING THIS FILE
from powerplant import PowerPlant

from pymoo.algorithms.soo.nonconvex.ga import GA as gen_alg 
from pymoo.core.callback import Callback
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
    population_size = 200  # will be used later in _evaluate for finding "x" array dimensions. default to 100
    num_gens = 500  # number of generations to run

    # defining the progress bar up here so it's easier to find
    progress_bar = alive_bar(
        total=num_gens, 
        title='Optimizing data. Have a fish while you wait:', 
        bar='fish',
        spinner='classic'
    ) 
    

    # CLASSES !!!
    class CostOptProblem(ElementwiseProblem):
        def __init__(self):
            # xl and xu (upper and lower bounds for x/cost) here
            xl: list[float] = []
            xu: list[float] = []
            self.cost_per_plant: list[str, float, float] = []  # plant name, cost/w, power generated, total mw cost

            for p in plants:  # finding min and max possible outputs for plants, ALL X VALS WILL BE BETWEEN THESE
                xl.append(0)
                xu.append(p.max_output)

            num_constr = len(plants) + 1  # number of constraints = number of plants plus one for demand met
            super().__init__(n_var=len(plants), n_obj=1, xl=np.array(xl), xu=np.array(xu), n_constr=num_constr)


        def _evaluate(self, x, out):
            # reset tracking lists to empty
            self.cost_per_plant = []
            constraint_violations: list[bool] = []

            power_demand: float = conditions[0]  # 13600 mW right now
            plant_costs = [p.plant_cost for p in plants]

            for ind, mw in enumerate(x):
                p = plants[ind]
                mi = p.min_output
                ma = p.max_output

                bt = (mw > ma or mw < mi) and mw != 0
                constraint_violations.append(bt)  # adds cv boolean to end of array (true is 1, false is 0)
                # you want this to be FALSE!!! RAAAHHHHHH

                self.cost_per_plant.append([p.name, round(float(mw)), round(float(mw) * 1000 * p.plant_cost, 2)])  # x1000 because mw

            demand_met = power_demand - x.sum()
            if demand_met < 0: demand_met = 0  # sets to 0 if the demand was successfully met
            constraint_violations.append(demand_met)

            out["F"] = round((x * 1000 * np.array(plant_costs)).sum(), 2)  # total mw generated
            out["G"] = constraint_violations # <= 0 (all values false) is ok, > 0 is not


    class ProgressBarCallback(Callback):  # updates the progress bar every generation
        def notify(self, alg):
            bar()


    alg = gen_alg(
        pop_size=population_size,
        eliminate_duplicates=True
    )

    with progress_bar as bar:
        result = minimize(  # go go gadget cheap electric
            problem=CostOptProblem(),
            algorithm=alg,  # defined directly above this
            termination=get_termination('n_gen', num_gens),
            verbose=False,
            callback=ProgressBarCallback(),
            save_history=True
        )

    # print best solution achieved
    print('Best solution found: \nX = %s\nF = %s\nG = %s' % (result.X, result.F, result.G))

    plant_info = [(p.plant_cost, p.max_output) for p in plants]
    for i, p in enumerate(result.problem.cost_per_plant):
        print(f'{i+1}. {p[0]} ({plant_info[i][0]})\n'
              f'    mW produced:    {p[1]} (max: {plant_info[i][1]})\n'
              f'    Total price:    ${p[2]}')

    # # put entire run history into variable for easier access
    # history = result.history

    # # print each gen's best cost found
    # for run in history:
    #     print(f'Run {run.n_gen} best cost: {run.pop.get("F").min()}')  # show generation's best sum


# TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY.
plants = get_plants('git_ignore\\CE4321_GridOptimizer_v3.xlsx')
conditions = get_conditions('git_ignore\\CE4321_GridOptimizer_v3.xlsx')

optimize('cost', plants, conditions)
