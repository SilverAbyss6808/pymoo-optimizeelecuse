
# this is where the actual optimization will happen


import string
from powerplant import PowerPlant
from excel_read import get_conditions, get_plants  # DELETE THIS WHEN DONE TESTING THIS FILE
from pymoo.optimize import minimize
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.soo.nonconvex.ga import GA as gen_alg 
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
    population_size = 1000  # define population size
    num_gens = 100  # number of generations to run
    number_of_bits = 200  # this is the number of bits in a bitstring. we're trying to make them all 1, so this is also the optimal sum. cool :thumbsup:
    bitstring_line_break = 50  # number of bits shown per line in the output. improves readability. bigger numbers are better for bigger screens.

    class CostOptProblem(ElementwiseProblem):
        def __init__(self):
            super().__init__(n_var=len(plants), n_obj=1)

        # tells the problem whats a good/feasible solution
        def _evaluate(self, x, out):
            out["F"] = x.sum()  # f is objective function; this should sum costs specifically
            # decision var is amt of power, funct is cost x megawatt
            out["G"] = None  # TODO array of constraints

    # defining the problem here so that I can use it in the sampling. 
    prb = CostOptProblem()

    alg = gen_alg(
        pop_size=population_size,
        eliminate_duplicates=True
    )

    # terminates after a set number of generations. defined towards top.
    trm = get_termination("n_gen", num_gens)

    result = minimize(
        problem=prb,
        algorithm=alg,
        termination= trm,
        verbose=True,
        save_history=True
    )

    # print best sum achieved
    print(f'Best sum {-result.pop.get("F").min()}/{number_of_bits}')

    # put entire run history into variable for easier access
    history = result.history

    # print best bitstring per generation and its sum
    for run in history:
        index = 0
        print(f'Run {run.n_gen}:\n'  # print generation number
            f'       ', end='')
        for bit in run.opt[0].X:
            index = index + 1
            print(f'{int(bit)}', end='')
            if index == bitstring_line_break: 
                print('\n       ', end='')  # adds a line break after 50 bits because otherwise it wraps weird
                index = 0
        print(f'\n'
              f'       Run {run.n_gen} sum: {-run.pop.get("F").min()}/{number_of_bits}\n')  # show generation's best sum


# TESTING AREA. STUFF BELOW HERE WILL BE DELETED EVENTUALLY.
plants = get_plants('git_ignore\CE4321_GridOptimizer_v3.xlsx')
conditions = get_conditions('git_ignore\CE4321_GridOptimizer_v3.xlsx')

for plant in plants:
    print(str(plant))
for cond in conditions:
    print(cond)

# optimize('cost', plants, conditions)
