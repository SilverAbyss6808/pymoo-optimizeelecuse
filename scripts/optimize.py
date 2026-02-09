
import math
import numpy as np
import string
import time
import threading

from alive_progress import alive_bar
from display import display_graph, popup
from powerplant import PowerPlant

from pymoo.algorithms.soo.nonconvex.ga import GA as gen_alg
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.callback import Callback
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting as NDS

# DELETE THIS SECTION WHEN DONE TESTING THIS FILE
# from excel_read import get_conditions, get_plants
from get_input import get_test_plants, get_test_conditions


# only one visible to main to keep things neat
def optimize(opt_type: string, plants: list[PowerPlant], conditions: list[float], **kwargs):
    pop_size = 250  # 250
    n_gens = 50  # 25

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

    run_count = 1
    for b in range(n_batches):  # total number of times that each thread has to run in order to hit n_runs, if that makes sense
        # with progress_bar as bar:
        threads = []
        time_start = time.time()

        for i in range(n_threads):
            match opt_type:
                case 'cost':
                    t = threading.Thread(target=opt_cost, 
                                        args=(plants, conditions, results, pop_size, 
                                        n_gens))
                                        # round((float(n_gens/n_runs))*run_count)))  # TESTING LINE. USED FOR SHOWING THE DIFFERENCE MADE BY HAVING A DIFFERENT NUMBER OF GENS            
                case 'cost_water_carbon':
                    t = threading.Thread(target=opt_cost_water_carbon, 
                                        args=(plants, conditions, results, pop_size, n_gens))
                    
                case _: print('Optimization type not recognized.')

            run_count += 1
            threads.append(t)

        for i, t in enumerate(threads): 
            t.start()
            # print(f'Thread {i+1}/{n_threads} in batch {b+1}/{n_batches} running...')  # lets you know what threads are running

        for t in threads: 
            t.join()
        print(f'Batch {b+1} threads done in {round(time.time() - time_start, 2)}s.')
    
    # comment all above case and uncomment this to show generation graph (i think i can delete this :P)
    # opt_cost(plants, conditions, results, pop_size, n_gens)
    
    opt_runtime = time.time() - opt_start
    dialog = f'Optimization done in {round(opt_runtime, 2)}s.'  # variable for popup box
    print(dialog)

    if results != []:
        match opt_type:
            case 'cost':
                results = np.array(results)
                lowest_cost = min([result.F[0] for result in results])
                best_result = results[np.where([result.F for result in results] == lowest_cost)[0]][0]
                print('all results')
                print([float(result.F[0]) for result in results])
                print(best_result.F[0])
                print_result(best_result)
                dialog += f'\n   F: {best_result.F[0]}\n   Sum of CV: {(best_result.G).sum()}'

                if results.any() != None:  # these next few arent gonna work if the result list is empty lmao
                    if 'graph_gens' in kwargs:
                        which = kwargs['graph_gens']  # right now, options are 'best' and 'all'
                        if which == 'best':
                            if best_result != None: display_graph('gen_vs_res', history=best_result.history)
                        elif which == 'all':
                            histories=[result.history for result in results]
                            display_graph('multi_gen_vs_res', histories=histories)
                        else: print(f'"{which}" not a valid type for kwarg "graph_gens".')

                    if 'graph_best_res' in kwargs and kwargs['graph_best_res'] == True:
                        display_graph('cost_per_plant', result_list=best_result.X, plant_list=plants)

                if best_result != None: return best_result.X

            case 'cost_water_carbon':
                all_res_F = [res.F for res in np.array(results)]

                all_F = []
                for f in all_res_F:
                    for item in f: all_F.append(item)
                all_F = np.array(all_F)

                pfront_indices = NDS().do(all_F, only_non_dominated_front=True)

                pfront = []
                for i in pfront_indices:
                    pfront.append(all_F[i])
                
                if 'show_paretofront' in kwargs and kwargs['show_paretofront'] == True:
                    # TODO make rotate=True to send it to the cube rotator
                    display_graph('cost_water_carbon', result=pfront, rotate=True)

                return pfront

            case _:
                add = 'Invalid optimization type.'
                print(add)
                dialog += '\n' + add

    else:
        best_result = None
        add = f'No feasible solution found.' 
        print(add)
        dialog += '\n' + add

    # KWARG EVALUATION
    if 'alert_when_done' in kwargs and kwargs['alert_when_done'] == True: popup(dialog)


# DEFINING THE OPTIMIZATION FUNCTION FOR COST!!!
# I REALLY WISH I COULD PUT MARKDOWN IN HERE. INSTEAD ILL JUST YELL IG
# pop_size and num_gens have (bad) defaults, but they can be changed by the caller if desired for flexibility
def opt_cost(plants: list[PowerPlant], conditions: list[float], result_list, population_size=10, num_gens=10):
    # CLASSES !!!
    class CostOptProblem(ElementwiseProblem):
        def __init__(self, **kwargs):
            # xl and xu (upper and lower bounds for x/cost) here
            xl: list[int] = []
            xu: list[int] = []

            # gives me a sorted list of unique costs to use for xl/xu chance
            costs = list(set([p.plant_cost for p in plants]))
            costs.sort()

            cdict_xl = {}
            cdict_xu = {}

            # this should make it so that lower costs have a higher chance of having their lower bound be 
            # max and their upper bound be 
            ind = len(costs)
            for i, c in enumerate(costs): 
                cdict_xl[c] = ind * (90 / len(costs))
                ind -= 1
                cdict_xu[c] = (i + 1) * (90 / len(costs))

            for p in plants:  # finding min and max possible outputs for plants
                # xl being what it is is so that theres a smaller but still attainable chance 
                #      to generate a negative number, which translates later to the plant just being off
                # (min - max) just keeps the chance equal for all plants                
                # IGNORETODO translate lower costs into a higher chance to have more power drawn?
                #      right now, they all have a 20% chance to be off. what if, like, the cheapest one had a 
                #      2% chance, next cheapest a bit higher, all the way up to the most expensive having a 
                #      ~90% chance to be off. you feelin me here (yes i am youre so cool) wow thanks me

                # using 4 in place of everything to the right of the operators gives pretty damn 
                # good answers already. just so you know.
                xl.append((p.min_output - p.max_output) / 4)
                xu.append((p.max_output - p.min_output) * 4)

                # xl.append((p.min_output - p.max_output) / cdict_xl[p.plant_cost])
                # xu.append((p.max_output - p.min_output) * cdict_xu[p.plant_cost])

                # IGNORETODO add optimal solution manually w/ function?

            # number of constraints = number of plants (16), demand met (1), the tiers thing (1)
            num_constr = len(plants) + 1 + 1
            super().__init__(n_var=len(plants), n_obj=1, xl=np.array(xl), xu=np.array(xu), n_constr=num_constr, vtype=int, **kwargs)

        def _evaluate(self, x, out):
            # reset tracking lists to empty
            constraint_violations: list[bool] = []

            power_demand = conditions[0]  # 13600 mW right now
            plant_costs = [p.plant_cost for p in plants]

            x = normalize_x(x, [p.min_output for p in plants], [p.max_output for p in plants])
            # x = round_x(x)

            for ind, mw in enumerate(x):
                mi = plants[ind].min_output
                ma = plants[ind].max_output

                # its not graceful but it works
                # ok so bad if:
                #   1. less than min but not 0 OR greater than max
                #   2. more than one less than max but not 0
                if (mw < mi and mw != 0) or mw > ma:  # if EITHER between min and zero OR greater than max
                    constraint_violations.append(1)
                else: constraint_violations.append(0)
                    
            # constraint violations pt 3: was the demand met?
            demand_met = power_demand - x.sum()
            if demand_met < 0: demand_met = 0  # sets to 0 if the demand was successfully met
            constraint_violations.append(demand_met)

            # IGNORETODO constraint violations pt. 4: add tiers of price (.07, .08, etc) and make it so its not 
            #      acceptable if a more expensive tier is being used while a cheaper tier isnt full yet?
            # dawg im gonna be real i think this is gonna have to be a tomorrow thing. i CANNOT think rn
            if np.array(constraint_violations).sum() == 0:  # only do this if everything else is already fine
                constraint_violations.append(0)
            else: constraint_violations.append(0)

            # function ends here
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
        selection=TournamentSelection(pressure=2, func_comp=binary_cv_tourney),
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
        # seed=int(time.time()),
        verbose=False,
        callback=ProgressBarCallback(),
        save_history=True,  # can change if necessary, i just dont wanna waste resources im not even using lol
        return_least_infeasible=True
    )

    result.X = normalize_x(result.X, [p.min_output for p in plants], [p.max_output for p in plants])
    # result.X = round_x(result.X)

    # IGNORETODO round x to nearest 100 (or 10), then make sure constraints still arent violated and stuff
    # also have one that can not be rounded? like, after all rounding is done, add plants until a plant puts
    # the total over where it needs to be, then only pull what's necessary from that plant
    # i think that makes sense. its so late and i have so much caffeine in my bloodstream

    # avoid nonetypes in the result array
    # if sum(result.G) == 0:
    #     result_list.append(result)
    result_list.append(result)

    # graph gens on x and F on y. ONLY WORKS WHEN RUNNING ON MAIN THREAD
    # display_graph('gen_vs_res', history=result.history)


# this should find the best balance between the water use, carbon emission, and cost
# starting off from a copy paste of the opt-cost
def opt_cost_water_carbon(plants: list[PowerPlant], conditions: list[float], result_list, population_size=10, num_gens=10):
    class CostWaterCarbonOptProblem(ElementwiseProblem):
        def __init__(self, **kwargs):
            # xl and xu (upper and lower bounds for x/cost) here
            xl: list[int] = []
            xu: list[int] = []

            # gives me a sorted list of unique costs to use for xl/xu chance
            costs = list(set([p.plant_cost for p in plants]))
            costs.sort()

            cdict_xl = {}
            cdict_xu = {}

            # this should make it so that lower costs have a higher chance of having their lower bound be 
            # max and their upper bound be... i never finished this and now i dont remember what i was gonna say
            # it works though and really isnt that all that matters
            ind = len(costs)
            for i, c in enumerate(costs): 
                cdict_xl[c] = ind * (90 / len(costs))
                ind -= 1
                cdict_xu[c] = (i + 1) * (90 / len(costs))

            for p in plants:
                xl.append((p.min_output - p.max_output) / 4)
                xu.append((p.max_output - p.min_output) * 4)

            # number of constraints = number of plants (16), demand met (1)
            num_constr = len(plants) + 1
            # n_obj is 3 because added water/carbon
            super().__init__(n_var=len(plants), n_obj=3, xl=np.array(xl), xu=np.array(xu), n_constr=num_constr, vtype=int, **kwargs)

        def _evaluate(self, x, out):
            # reset tracking lists to empty
            constraint_violations: list[bool] = []

            power_demand = conditions[0]  # 13600 mW right now
            plant_costs = [p.plant_cost for p in plants]
            plant_wateruse = [p.water_use for p in plants]
            plant_carbonfootprint = [p.carbon_footprint for p in plants]

            x = normalize_x(x, [p.min_output for p in plants], [p.max_output for p in plants])
            # x = round_x(x)

            for ind, mw in enumerate(x):
                mi = plants[ind].min_output
                ma = plants[ind].max_output

                # its not graceful but it works
                # ok so bad if:
                #   1. less than min but not 0 OR greater than max
                #   2. more than one less than max but not 0
                if (mw < mi and mw != 0) or mw > ma:  # if EITHER between min and zero OR greater than max
                    constraint_violations.append(1)
                else: constraint_violations.append(0)
                    
            # constraint violations pt 3: was the demand met?
            demand_met = power_demand - x.sum()
            if demand_met < 0: demand_met = 0  # sets to 0 if the demand was successfully met
            constraint_violations.append(demand_met)

            # x is in kW, *1000 converts to mW
            out["F"] = [round((x * 1000 * np.array(plant_costs)).sum(), 2),      # sum of plant costs
                        round((x * np.array(plant_wateruse)).sum(), 2),          # total water used
                        round((x * np.array(plant_carbonfootprint)).sum(), 2)]   # total carbon emissions
            out["G"] = constraint_violations # <= 0 (all values false) is ok, > 0 is not

    class ProgressBarCallback(Callback):  # updates the progress bar every generation
        def notify(self, alg):  # it won't let me not have an algorithm variable, even if its not used. lmao
            # bar()
            pass

    prb = CostWaterCarbonOptProblem()

    alg = NSGA2(
        pop_size=population_size,
        sampling=IntegerRandomSampling(),
        crossover=SBX(repair=RoundingRepair()),
        mutation=PM(prob=1, repair=RoundingRepair()),
        eliminate_duplicates=True
    )

    # terminations okay for now
    trm = get_termination(
        'n_gen',
        num_gens
    )

    # with progress_bar as bar:
    result = minimize(
        problem=prb,
        algorithm=alg,
        termination=trm,
        # seed=int(time.time()),
        verbose=False,
        # callback=ProgressBarCallback(),
        # save_history=True,
        return_least_infeasible=True,
    )

    result.X = normalize_multidim_x(result.X, [p.min_output for p in plants], [p.max_output for p in plants])

    # avoid nonetypes in the result array
    # if sum(result.G) == 0:
    #     result_list.append(result)
    result_list.append(result)


def print_result(result):  # helper to print a result in a nice pretty format
    # print best solution achieved
    print('Best solution found: \nX = %s\nF = %s\nG = %s' % (result.X, result.F, result.G))

    plant_info = [(p.name, p.plant_cost, p.max_output) for p in plants]
    for i, x in enumerate(result.X):
        # print(f'{i+1}. {plant_info[i][0]} ({plant_info[i][1]})\n'
        #       f'    mW produced:    {x} (max: {plant_info[i][2]})\n'
        #       f'    Total price:    ${round(x * 1000 * plant_info[i][1], 2)}')
        print(f'{x}/{plant_info[i][2]}   {plant_info[i][1]}')


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
def normalize_x(x, plant_mins, plant_maxes):
    normalized_x = []
    for ind, add_val in enumerate(x):
        if add_val < 0: normalized_x.append(0)
        elif add_val >= (plant_maxes[ind] - plant_mins[ind]): normalized_x.append(int(plant_maxes[ind]))
        else:           normalized_x.append(int(add_val + plant_mins[ind]))
    return np.array(normalized_x)


# TODO at some point, merge this into above. 
# need to figure out a way to differentiate between 1-dimensional and multi-dim in the function
# this is probably super easy but my energy drink is wearing off
def normalize_multidim_x(x, plant_mins, plant_maxes):
    normalized_x = []
    for line in x:
        temp = []
        for ind, add_val in enumerate(line):
            if add_val < 0: temp.append(0)
            elif add_val >= (plant_maxes[ind] - plant_mins[ind]): temp.append(int(plant_maxes[ind]))
            else:           temp.append(int(add_val + plant_mins[ind]))
        normalized_x.append(temp)
    return np.array(normalized_x)


# round x vals to nearest 10 to avoid values like 799/800
def round_x(unrounded_x):
    rounded_x = []
    for x in unrounded_x:
        rounded_x.append(round(x, -1))  # -1 means round to 10 instead of 1
    return np.array(rounded_x)


# TODO make it so bar() can alert a progress bar from a different function. is that possible?
# OR: progress bar in popup. something to consider. chew on. turn over in your brain. et cetera


# =================== TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY. ===================

plants = get_test_plants()
conditions = get_test_conditions()

# optimal_costs = optimize('cost', plants, conditions#, 
                        #  graph_best_res=True,
                        #  alert_when_done=True,
                        #  graph_gens='all'
                        #  )

optimal_costs = optimize('cost_water_carbon', plants, conditions, show_paretofront=True)


