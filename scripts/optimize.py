
import string
import numpy as np

from alive_progress import alive_bar
from excel_read import get_conditions, get_plants  # DELETE THIS WHEN DONE TESTING THIS FILE
from powerplant import PowerPlant

from pymoo.algorithms.soo.nonconvex.ga import GA as gen_alg 
from pymoo.core.callback import Callback
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.optimize import minimize
from pymoo.termination import get_termination


# only one visible to main to keep things neat
def optimize(opt_type: string, plants: list[PowerPlant], conditions: list[float]):
    try:  # can add more types of optimization later (carbon, water use, etc)
        if opt_type == 'cost':
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
    num_gens = 1000  # number of generations to run

    # defining the progress bar up here so it's easier to find
    progress_bar = alive_bar(
        total=num_gens, 
        title='Optimizing data, please wait...',
        theme='smooth'
        # title='Optimizing data. Have a fish while you wait:', 
        # bar='fish',
        # spinner='classic'
    ) 
    

    # CLASSES !!!
    class CostOptProblem(ElementwiseProblem):
        def __init__(self):
            # xl and xu (upper and lower bounds for x/cost) here
            xl: list[int] = []
            xu: list[int] = []
            self.cost_per_plant: list[str, float, float] = []  # plant name, cost/w, power generated, total mw cost

            for p in plants:  # finding min and max possible outputs for plants, ALL X VALS WILL BE BETWEEN THESE
                xl.append(0)
                xu.append(p.max_output)

            # number of constraints = number of plants (17), demand met (1), more than one not max or 0 (1)
            num_constr = len(plants) + 1
            super().__init__(n_var=len(plants), n_obj=1, xl=np.array(xl), xu=np.array(xu), n_constr=num_constr, vtype=int)


        def _evaluate(self, x, out):
            # reset tracking lists to empty
            self.cost_per_plant = []
            constraint_violations: list[bool] = []

            power_demand: float = conditions[0]  # 13600 mW right now
            plant_costs = [p.plant_cost for p in plants]
            notok_counter = 0

            for ind, mw in enumerate(x):
                p = plants[ind]
                ma = p.max_output

                # constraint violations pt 1: mw generated <= max
                # you want these to be FALSE !!!
                # constraint violations pt 2: no more than one plant is not running at max or 0
                # this SHOULD make it so plants dont split
                # i think it works? it just somehow cant find a good answer in a full minute of running
                notok = mw < ma and mw != 0
                if notok and notok_counter < 1: 
                    constraint_violations.append(False)
                    notok_counter += 1
                else: constraint_violations.append(notok)

                self.cost_per_plant.append([p.name, round(mw), round(mw * 1000 * p.plant_cost, 2)])  # x1000 because mw
            
            # constraint violations pt 3: was the demand met?
            demand_met = power_demand - x.sum()
            if demand_met < 0: demand_met = 0  # sets to 0 if the demand was successfully met
            constraint_violations.append(demand_met)

            out["F"] = round((x * 1000 * np.array(plant_costs)).sum(), 2)  # total cost of w from plants (NOT MW)
            out["G"] = constraint_violations # <= 0 (all values false) is ok, > 0 is not


    class ProgressBarCallback(Callback):  # updates the progress bar every generation
        def notify(self, alg):  # it won't let me not have an algorithm variable, even if its not used. lmao
            bar()


    alg = gen_alg(
        pop_size=population_size,
        sampling=IntegerRandomSampling(),
        crossover=SBX(repair=RoundingRepair()),  # these two are the default crossover/mutation types,
        mutation=PM(repair=RoundingRepair()),    # just added rounding repair so x stays integers
        eliminate_duplicates=True
    )

    with progress_bar as bar:
        result = minimize(  # go go gadget cheap electric
            problem=CostOptProblem(),
            algorithm=alg,  # defined directly above this
            termination=get_termination('n_gen', num_gens),
            verbose=False,
            callback=ProgressBarCallback(),
            save_history=True,
            return_least_infeasible=True
        )

    # print best solution achieved
    print('Best solution found: \nX = %s\nF = %s\nG = %s' % (result.X, result.F, result.G))

    plant_info = [(p.plant_cost, p.max_output) for p in plants]
    for i, p in enumerate(result.problem.cost_per_plant):
        print(f'{i+1}. {p[0]} ({plant_info[i][0]})\n'
              f'    mW produced:    {p[1]} (max: {plant_info[i][1]})\n'
              f'    Total price:    ${p[2]}')
        # print(f'{p[1]}/{plant_info[i][1]}   {p[0]}')


    # # put entire run history into variable for easier access
    # history = result.history

    # # print each gen's best cost found
    # for run in history:
    #     print(f'Run {run.n_gen} best cost: {run.pop.get("F").min()}')  # show generation's best sum


# TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY.
plants = get_plants('git_ignore\\CE4321_GridOptimizer_v3.xlsx')
conditions = get_conditions('git_ignore\\CE4321_GridOptimizer_v3.xlsx')

optimize('cost', plants, conditions)
