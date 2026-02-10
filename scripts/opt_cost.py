
import numpy as np
from opt_helpers import binary_cv_tourney, normalize_x
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

# DEFINING THE OPTIMIZATION FUNCTION FOR COST!!!
# I REALLY WISH I COULD PUT MARKDOWN IN HERE. INSTEAD ILL JUST YELL IG
# pop_size and num_gens have (bad) defaults, but they can be changed by the caller if desired for flexibility
def opt_cost(plants: list[PowerPlant], conditions: list[float], result_list, progress_bar, population_size=10, num_gens=10):
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

            for p in plants:
                # using 4 in place of everything to the right of the operators gives pretty damn 
                # good answers already. just so you know.
                xl.append((p.min_output - p.max_output) / 4)
                xu.append((p.max_output - p.min_output) * 4)

            # number of constraints = number of plants (16), demand met (1)
            num_constr = len(plants) + 1
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

                # bad if:
                #   1. less than min but not 0 OR greater than max
                #   2. more than one less than max but not 0
                if (mw < mi and mw != 0) or mw > ma:  # if EITHER between min and zero OR greater than max
                    constraint_violations.append(1)
                else: constraint_violations.append(0)
                    
            # constraint violations pt 3: was the demand met?
            demand_met = power_demand - x.sum()
            if demand_met < 0: demand_met = 0  # sets to 0 if the demand was successfully met
            constraint_violations.append(demand_met)

            # function ends here
            out["F"] = round((x * 1000 * np.array(plant_costs)).sum(), 2)
            out["G"] = constraint_violations # <= 0 (all values false) is ok, > 0 is not

    class ProgressBarCallback(Callback):  # updates the progress bar every generation
        def notify(self, alg):  # it won't let me not have an algorithm variable, even if its not used. lmao
            progress_bar()
    
    prb = CostOptProblem()

    alg = gen_alg(
        pop_size=population_size,
        sampling=IntegerRandomSampling(),
        crossover=SBX(repair=RoundingRepair()),
        selection=TournamentSelection(pressure=2, func_comp=binary_cv_tourney),
        mutation=PM(prob=1, repair=RoundingRepair()),
        eliminate_duplicates=True
    )

    trm = get_termination(
        'n_gen',
        num_gens
    )

    result = minimize(  # go go gadget cheap electric
        problem=prb,
        algorithm=alg,
        termination=trm,
        # seed=int(time.time()),
        verbose=False,
        callback=ProgressBarCallback(),
        # TODO: make it so wanting the graph turns this on
        # save_history=True,  # can change if necessary, i just dont wanna waste resources im not even using lol
        return_least_infeasible=True
    )

    result.X = normalize_x(result.X, [p.min_output for p in plants], [p.max_output for p in plants])

    # avoid nonetypes in the result array
    # if sum(result.G) == 0:
    #     result_list.append(result)
    result_list.append(result)

    # graph gens on x and F on y. ONLY WORKS WHEN RUNNING ON MAIN THREAD
    # display_graph('gen_vs_res', history=result.history)
