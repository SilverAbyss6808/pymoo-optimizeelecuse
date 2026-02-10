
import numpy as np
import string
import time
import threading

from display import display_graph, popup
from opt_cost import opt_cost
from opt_costwatercarbon import opt_cost_water_carbon
from opt_helpers import print_result
from powerplant import PowerPlant
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting as NDS

# DELETE THIS SECTION WHEN DONE TESTING THIS FILE
from get_input import get_test_plants, get_test_conditions


# only one visible to main to keep things neat
def optimize(opt_type: string, plants: list[PowerPlant], conditions: list[float], **kwargs):
    pop_size = 250  # 250
    n_gens = 50  # 25

    n_runs = 16
    n_threads = 8
    n_batches = int(n_runs/n_threads)

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
                print_result(plants, best_result)
                dialog += f'\n   F: {best_result.F[0]}\n   Sum of CV: {(best_result.G).sum()}'

                if results.any() != None:  # these next few arent gonna work if the result list is empty lmao
                    if 'graph_gens' in kwargs:  # this ones not gonna be available to users
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


# =================== TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY. ===================

plants = get_test_plants()
conditions = get_test_conditions()

# optimal_costs = optimize('cost', plants, conditions#, 
                        #  graph_best_res=True,
                        #  alert_when_done=True,
                        #  graph_gens='all'
                        #  )

optimal_costs = optimize('cost', plants, conditions)


