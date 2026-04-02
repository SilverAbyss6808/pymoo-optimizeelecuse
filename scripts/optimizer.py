
# this is gonna be the main script that executes. no ui, call the exe with command line args

from get_input import import_plants_from_godot, get_test_conditions, get_test_weights
from opt_helpers import print_result
from optimize import optimize
import sys


# reads all command line args except for name of script (should just be the infile)
# infile = sys.argv[1]
infile = 'test_infile.txt'

plants = import_plants_from_godot(infile)
conditions = get_test_conditions()  # TODO import conditions from file
weights = get_test_weights()  # TODO import weights from file

# adapted from main. pretty prints the result <3
# TODO: write results to file in a godot-readable way
best_option = optimize('cost_water_carbon', plants, conditions, weights, 
                  #      n_runs=2, n_threads=2, 
                       pop_size=300, save_best=True
                       )

print(f'Your best option based on the provided weights is:\n'
      f'    Cost:   {best_option[0][0]}\n'
      f'    Water:  {best_option[0][1]}\n'
      f'    Carbon: {best_option[0][2]}\n')

print_result(plants, best_option[1], best_option[0], best_option[2])

# TODO transfer from here down to write_output.py when done testing

# for reference:
#   best_options[0] is F --> total cost, total water, total carbon (ex. F = [867000. 762500.  29090.])
#   best_options[1] is X --> power output of each plant (ex. X = [1700 2400 5000 4500    0])
#   best_options[2] is G --> constraint violations ()
out_string = ''  # cant format as dict or godot wont read it right

out_string += f'"F":{best_option[0]}'  # format with commas, without dots

# creates outfile if it doesnt exist, overwrites if it does
with open("outfile.txt", "w") as f:
    f.write(out_string)

print('Results written to outfile.txt.')

