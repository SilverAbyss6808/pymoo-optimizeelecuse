
import numpy as np
from opt_helpers import normalize_x, normalize_multidim_x
from powerplant import PowerPlant
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.callback import Callback
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.optimize import minimize
from pymoo.termination import get_termination

# this should find the best balance between the water use, carbon emission, and cost
# starting off from a copy paste of the opt-cost
def opt_cost_water_carbon(plants: list[PowerPlant], conditions: list[float], result_list, 
                          progress_bar, population_size=10, num_gens=10):
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
            sun_percent = conditions[1]
            wind_percent = conditions[2]

            plant_costs = [p.plant_cost for p in plants]
            plant_wateruse = [p.water_use for p in plants]
            plant_carbonfootprint = [p.carbon_footprint for p in plants]

            x = normalize_x(x, [p.min_output for p in plants], [p.max_output for p in plants])
            # x = round_x(x)

            for ind, mw in enumerate(x):
                mi = plants[ind].min_output
                ma = plants[ind].max_output

                # adjust max output for weather-affected plants
                if plants[ind].type == 'Solar' or plants[ind].type == 'Concentrating Solar':
                    ma = ma * sun_percent

                if plants[ind].type == 'Wind':
                    ma = ma * wind_percent

                # same as cost opt
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
            progress_bar()

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
        verbose=False,
        callback=ProgressBarCallback(),
        # save_history=True,
        return_least_infeasible=True,
    )

    result.X = normalize_multidim_x(result.X, [p.min_output for p in plants], [p.max_output for p in plants])

    # avoid nonetypes in the result array
    # if sum(result.G) == 0:  # just so you know, it doesnt like this
    #     result_list.append(result)
    result_list.append(result)

