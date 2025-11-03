
import display
import string
import numpy as np
import time
import threading

from alive_progress import alive_bar
from powerplant import PowerPlant

from pymoo.algorithms.soo.nonconvex.ga import GA as gen_alg 
from pymoo.core.callback import Callback
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.optimize import minimize
from pymoo.termination import get_termination

# DELETE THIS SECTION WHEN DONE TESTING THIS FILE
from excel_read import get_conditions, get_plants
import matplotlib.pyplot as plt


# only one visible to main to keep things neat
# TODO do with fourish plants first
def optimize(opt_type: string, plants: list[PowerPlant], conditions: list[float]):
    pop_size = 100
    n_gens = 100

    n_runs = 16
    n_threads = 8
    n_batches = int(n_runs/n_threads)

    # progress_bar = alive_bar(
    #     total=int(n_runs * n_gens), 
    #     title='Optimizing data, please wait...',
    #     theme='smooth'
    # )

    results = []
    opt_start = time.time()
    print(f'Starting...')

    match opt_type:
        case 'cost':
            for b in range(n_batches):  # total number of times that each thread has to run in order to hit n_runs, if that makes sense
                # with progress_bar as bar:
                threads = []
                time_start = time.time()

                for i in range(n_threads):
                    t = threading.Thread(target=opt_cost, 
                                            args=(plants, conditions, results, pop_size, n_gens))
                    threads.append(t)

                for i, t in enumerate(threads): 
                    t.start()
                    print(f'Thread {i+1}/{n_threads} in batch {b+1}/{n_batches} running...')  # lets you know what threads are running

                for t in threads: 
                    t.join()
                print(f'Batch {b+1} threads done in {round(time.time() - time_start, 2)}s.')
            
            # comment all above case and uncomment this to show generation graph
            # opt_cost(plants, conditions, results, pop_size, n_gens)

        case _: print('error')
    
    opt_runtime = time.time() - opt_start
    dialog = f'Optimization done in {round(opt_runtime, 2)}s.'  # variable for popup box
    print(dialog)
    if results != []:
        results = np.array(results)
        lowest_cost = min([result.F[0] for result in results])
        best_result = results[np.where([result.F for result in results] == lowest_cost)[0]][0]
        print('all results')
        print([float(result.F[0]) for result in results])
        print(best_result.F[0])
        print_result(best_result)
        dialog += f'\n   F: {best_result.F[0]}\n   Sum of CV: {(best_result.G).sum()}'
    else:
        add = f'No feasible solution found.' 
        print(add)
        dialog += '\n' + add

    display.popup(dialog)


# DEFINING THE OPTIMIZATION FUNCTION FOR COST!!!
# I REALLY WISH I COULD PUT MARKDOWN IN HERE. INSTEAD ILL JUST YELL IG
# pop_size and num_gens have defaults, but they can be changed by the caller if desired for flexibility
def opt_cost(plants: list[PowerPlant], conditions: list[float], result_list, population_size=10, num_gens=10):
    # CLASSES !!!
    class CostOptProblem(ElementwiseProblem):
        def __init__(self, **kwargs):
            # xl and xu (upper and lower bounds for x/cost) here
            xl: list[int] = []
            xu: list[int] = []

            for p in plants:  # finding min and max possible outputs for plants
                # xl being what it is is so that theres a smaller but still attainable chance 
                # to generate a negative number, which translates later to the plant just being off
                # (min - max) just keeps the chance equal for all plants
                xl.append((p.min_output - p.max_output) / 4)
                xu.append(p.max_output - p.min_output)

            # number of constraints = number of plants (16), demand met (1)
            num_constr = len(plants) + 1
            super().__init__(n_var=len(plants), n_obj=1, xl=np.array(xl), xu=np.array(xu), n_constr=num_constr, vtype=int, **kwargs)

        def _evaluate(self, x, out):
            # reset tracking lists to empty
            constraint_violations: list[bool] = []

            power_demand = conditions[0]  # 13600 mW right now
            plant_costs = [p.plant_cost for p in plants]
            notok_counter = 0

            x = normalize_x(x, [p.min_output for p in plants])

            for ind, mw in enumerate(x):
                mi = plants[ind].min_output
                ma = plants[ind].max_output

                # its not graceful but it works
                # ok so bad if:
                #   less than min but not 0 OR greater than max
                #   more than one less than max but not 0
                if (mw < mi and mw != 0) or mw > ma:  # if EITHER between min and zero OR greater than max
                    constraint_violations.append(1)
                # elif mw < ma and mw != 0:  # if less than max but not zero (okay one time)
                #     if notok_counter < 1:
                #         notok_counter += 1
                #         constraint_violations.append(0)
                #     else: constraint_violations.append(1)
                else: constraint_violations.append(0)
                    
            # constraint violations pt 3: was the demand met?
            demand_met = power_demand - x.sum()
            if demand_met < 0: demand_met = 0  # sets to 0 if the demand was successfully met
            constraint_violations.append(demand_met)

            # TODO add/improve constraints
            #   add one to make sure more expensive plants arent chosen if there are cheaper options?
            #   like if theres a 12 cent plant at 0, there shouldnt be a 14 cent at max

            out["F"] = round((x * 1000 * np.array(plant_costs)).sum(), 2)
            out["G"] = constraint_violations # <= 0 (all values false) is ok, > 0 is not

    class ProgressBarCallback(Callback):  # updates the progress bar every generation
        def notify(self, alg):  # it won't let me not have an algorithm variable, even if its not used. lmao
            # bar()
            pass

    prb = CostOptProblem()

    alg = gen_alg(
        pop_size=population_size,
        sampling=IntegerRandomSampling(),
        crossover=SBX(repair=RoundingRepair()),
        # selection=TournamentSelection(pressure=2, func_comp=binary_cv_tourney),
        mutation=PM(prob=1, repair=RoundingRepair()),
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
        seed=int(time.time()),
        verbose=False,
        callback=ProgressBarCallback(),
        save_history=False,  # can change if necessary, i just dont wanna waste resources im not even using lol
        return_least_infeasible=True
    )

    result.X = normalize_x(result.X, [p.min_output for p in plants])

    # avoid nonetypes in the result array
    if sum(result.G) == 0:
        result_list.append(result)
    # result_list.append(result)

    # graph gens on x and F on y. ONLY WORKS WHEN RUNNING ON MAIN THREAD
    # print_generation_graph(result.history)


def print_result(result):  # helper to print a result in a nice pretty format
    # print best solution achieved
    print('Best solution found: \nX = %s\nF = %s\nG = %s' % (result.X, result.F, result.G))

    plant_info = [(p.name, p.plant_cost, p.max_output) for p in plants]
    for i, x in enumerate(result.X):
        # print(f'{i+1}. {plant_info[i][0]} ({plant_info[i][1]})\n'
        #       f'    mW produced:    {x} (max: {plant_info[i][2]})\n'
        #       f'    Total price:    ${round(x * 1000 * plant_info[i][1], 2)}')
        print(f'{x}/{plant_info[i][2]}   {plant_info[i][1]}')


def print_generation_graph(history):  # helper to print cost per generation. REQUIRED TO RUN ON MAIN THREAD
    xvals = [run.n_gen for run in history]
    yvals = [run.pop.get("F").min() for run in history]
    plt.bar(xvals, yvals)
    plt.show()


# tournament selection that picks option with fewest violations FIRST, then goes off min
def binary_cv_tourney(pop, P, **kwargs):  # adapted from https://pymoo.org/operators/selection.html
    # The P input defines the tournaments and competitors
    n_tournaments, n_competitors = P.shape
    # print(f'population:\n'
    #       f'    cv sum:         {pop.get("G").sum()}\n'
    #       f'    F value:        {pop.get("F")[0]}\n'
    #       f'n_tournaments:  {n_tournaments}\n'
    #       f'n_competitors:  {n_competitors}\n')

    # the result this function returns
    S = np.full(n_tournaments, -1, dtype=int)

    # how the winner should be chosen
    for i in range(n_tournaments):
        a, b = P[i]  
        if (pop[a].G).sum() < (pop[b].G).sum():  # fewer violations on a
            S[i] = a
        elif (pop[a].G).sum() > (pop[b].G).sum():  # fewer violations on b
            S[i] = b
        else:  # if same num of violations on each
            if pop[a].F < pop[b].F: 
                S[i] = a
            else: 
                S[i] = b

    return S


# normalize X
def normalize_x(x, plant_mins):
    normalized_x = []
    for ind, add_val in enumerate(x): 
        if add_val < 0: normalized_x.append(0)
        else:           normalized_x.append(int(add_val + plant_mins[ind]))
    return np.array(normalized_x)


# TODO make it so bar() can alert a progress bar from a different function. is that possible?
# OR: progress bar in popup. something to consider. chew on. turn over in your brain


# =================== TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY. ===================
plants = get_plants('git_ignore\\CE4321_GridOptimizer_v3.xlsx')
conditions = get_conditions('git_ignore\\CE4321_GridOptimizer_v3.xlsx')

optimal_costs = optimize('cost', plants, conditions)
# disp.display_graph('cost', optimal_costs, plants)

