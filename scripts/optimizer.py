
# this is gonna be the main script that executes. no ui, call the exe with command line args

from get_input import import_info_from_godot
from opt_helpers import print_result
from optimize import optimize
import os
import sys
from write_output import write_results_for_godot


# reads all command line args except for name of script (should just be the infile)
infile = sys.argv[1]
# infile = 'test_infile.txt'

plants, conditions, weights = import_info_from_godot(infile)
# conditions = get_test_conditions()  # TODO import conditions from file
# weights = get_test_weights()  # TODO import weights from file

# THE OPTIMIZATION
best_option = optimize('cost_water_carbon', plants, conditions, weights, pop_size=100, save_best=True, overwrite_png_gif=True)

# adapted from main. pretty prints the result to the terminal for reference <3
print_result(plants, best_option[1], best_option[0], best_option[2])

write_results_for_godot(best_option)  # writes godot-formatted dict of results to outfile.txt
print(f'Results written to {os.path.abspath('outfile.txt')}.')

