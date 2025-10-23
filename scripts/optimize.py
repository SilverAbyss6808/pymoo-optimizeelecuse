
import string
import numpy as np
import threading
import time

from alive_progress import alive_bar
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

# DELETE THIS SECTION WHEN DONE TESTING THIS FILE
from excel_read import get_conditions, get_plants
from display import display_graph


# TODO parallellize. set up multithreading
# only one visible to main to keep things neat
def optimize(opt_type: string, plants: list[PowerPlant], conditions: list[float], n_runs=16, n_threads=8):
    results = []
    n_batches = int(n_runs/n_threads)
    opt_start = time.time()

    match opt_type:
        case 'cost':
            for b in range(n_batches):  # total number of times that each thread has to run in order to hit n_runs, if that makes sense
                threads = []
                time_start = time.time()
                for i in range(n_threads):
                    t = threading.Thread(target=opt_cost, args=(plants, conditions, results))
                    threads.append(t)

                for i, t in enumerate(threads): 
                    t.start()
                    print(f'Thread {i+1}/{n_threads} in batch {b+1}/{n_batches} running...')  # lets you know what threads are running

                for t in threads: 
                    t.join()
                print(f'Batch {b+1} threads done in {round(time.time() - time_start, 2)}s.')

        case _: print('error')
    
    opt_runtime = time.time() - opt_start
    print(f'Optimization done in {round(opt_runtime, 2)}s.')
    if results != []:
        results = np.array(results)
        lowest_cost = min([result.F[0] for result in results])
        best_result = results[np.where([result.F for result in results] == lowest_cost)[0]][0]
        print('all results')
        print([float(result.F[0]) for result in results])
        print(best_result)
        print_result(best_result)
    else: print(f'No feasible solution found.')



# DEFINING THE OPTIMIZATION FUNCTION FOR COST!!!
# I REALLY WISH I COULD PUT MARKDOWN IN HERE. INSTEAD ILL JUST YELL IG
def opt_cost(plants: list[PowerPlant], conditions: list[float], result_list, population_size=100, num_gens=500):

    # defining the progress bar up here so it's easier to 
    # it really doesnt like running multithreaded. so its off for now
    progress_bar = alive_bar(
        total=num_gens, 
        title='Optimizing data, please wait...',
        theme='smooth'
    ) 
    

    # CLASSES !!!
    class CostOptProblem(ElementwiseProblem):
        def __init__(self, **kwargs):
            # xl and xu (upper and lower bounds for x/cost) here
            xl: list[int] = []
            xu: list[int] = []

            for p in plants:  # finding min and max possible outputs for plants, ALL X VALS WILL BE BETWEEN THESE
                xl.append(0)
                xu.append(p.max_output)

            # number of constraints = number of plants (16), demand met (1)
            num_constr = len(plants) + 1
            super().__init__(n_var=len(plants), n_obj=1, xl=np.array(xl), xu=np.array(xu), n_constr=num_constr, vtype=int, **kwargs)


        def _evaluate(self, x, out):
            # reset tracking lists to empty
            constraint_violations: list[bool] = []

            power_demand = conditions[0]  # 13600 mW right now
            plant_costs = [p.plant_cost for p in plants]
            notok_counter = 0

            for ind, mw in enumerate(x):
                ma = plants[ind].max_output

                # constraint violations pt 1: mw generated <= max
                # constraint violations pt 2: no more than one plant is not running at max or 0
                notok = mw < ma and mw != 0
                if notok and notok_counter < 1: 
                    notok_counter += 1
                    constraint_violations.append(0)
                else: constraint_violations.append(notok)

            # constraint violations pt 3: was the demand met?
            demand_met = power_demand - x.sum()
            if demand_met < 0: demand_met = 0  # sets to 0 if the demand was successfully met
            constraint_violations.append(demand_met)

            # TODO add/improve constraints
            #   add one to make sure more expensive plants arent chosen if there are cheaper options?
            #   like if theres a 12 cent plant at 0, there shouldnt be a 14 cent at max

            out["F"] = round((x * 1000 * np.array(plant_costs)).sum(), 2)  # total cost of w from plants (NOT MW)
            out["G"] = constraint_violations # <= 0 (all values false) is ok, > 0 is not


    class ProgressBarCallback(Callback):  # updates the progress bar every generation
        def notify(self, alg):  # it won't let me not have an algorithm variable, even if its not used. lmao
            # bar()
            pass


    prb = CostOptProblem()


    alg = gen_alg(
        pop_size=population_size,
        sampling=IntegerRandomSampling(),
        crossover=SBX(repair=RoundingRepair()),  # these two are the default crossover/mutation types,
        mutation=PM(repair=RoundingRepair()),    # just added rounding repair so x stays integers
        eliminate_duplicates=True
    )


    # terminations okay for now
    trm = get_termination(
        'n_gen',
        num_gens
    )


    # with progress_bar as bar:
    result = minimize(  # go go gadget cheap electric
        problem=prb,
        algorithm=alg,
        termination=trm,
        verbose=False,
        callback=ProgressBarCallback(),
        save_history=False,  # can change if necessary, i just dont wanna waste resources im not even using lol
        return_least_infeasible=True
    )


    # avoid nonetypes in the result array
    if sum(result.G) == 0:
        result_list.append(result)


def print_result(result):  # helper to print a result
    # print best solution achieved
    print('Best solution found: \nX = %s\nF = %s\nG = %s' % (result.X, result.F, result.G))

    plant_info = [(p.name, p.plant_cost, p.max_output) for p in plants]
    for i, x in enumerate(result.X):
        # print(f'{i+1}. {plant_info[i][0]} ({plant_info[i][1]})\n'
        #       f'    mW produced:    {x} (max: {plant_info[i][2]})\n'
        #       f'    Total price:    ${round(x * 1000 * plant_info[i][1], 2)}')
        print(f'{x}/{plant_info[i][2]}   {plant_info[i][1]}')


# TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY.
plants = get_plants('git_ignore\\CE4321_GridOptimizer_v3.xlsx')
conditions = get_conditions('git_ignore\\CE4321_GridOptimizer_v3.xlsx')

optimal_costs = optimize('cost', plants, conditions)
# display_graph('cost', optimal_costs, plants)

