
import numpy as np

def print_result(plants, result):  # helper to print a result in a nice pretty format
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

