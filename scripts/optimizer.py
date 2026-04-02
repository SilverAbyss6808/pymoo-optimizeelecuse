
# this is gonna be the main script that executes. no ui, call the exe with command line args

from get_input import get_test_conditions, get_test_weights
from opt_helpers import print_result
from optimize import optimize
from powerplant import PowerPlant
import re
import sys

# ok args example: 
#   [C:\Users\baxte\anaconda3\envs\pymoo-optimizeelecuse\python.exe 
#   c:/gunk/Code/python/pymoo-optimizeelecuse/scripts/optimizer.py] 
#   path/to/infile.txt

# reads all command line args except for name of script (should just be the infile)
infile = sys.argv[1]
# infile = 'test_infile.txt'
unformatted_file_contents = ''
with open(infile) as f:
    unformatted_file_contents = f.read()

# deconstructing the file from godot to make it easier to use
godot_dict_item_regex = re.compile(r'(?:(?:"[\w\s.]+")|(?:[\w\s.]+)):\[(?:(?:(?:"[\w\s.]+")|(?:[\w\s.]+)),?)+]')
godot_dict_items = re.findall(godot_dict_item_regex, unformatted_file_contents)  # finds key:value pairs

keyval_item_regex = re.compile(r'(?:"[\w\s.]+")|(?:[\w\s.]+)')  # finds the individual items inside the things

plant_dict = {}
num_plants = 0
for idx, kv_pair in enumerate(godot_dict_items):
    # take out any double quotes, just for cleanliness
    items = re.findall(keyval_item_regex, kv_pair)
    key = items[0].replace('"', '')

    # find number of plants
    if idx > 0:
        if num_plants != (len(items)-1): print('Dictonary values not of equal length.')
        else: num_plants = len(items)-1
    else: num_plants = len(items)-1

    # add plant attribute to dictionary
    values = []
    for item in items[1:]:
        values.append(item.replace('"', ''))
    plant_dict[key] = values

plant_list = []
for idx in range(0, num_plants):
    attr_list = []
    for key in plant_dict:
        attribute = plant_dict[key]
        attr_list.append(attribute[idx])

    plant_list.append(PowerPlant(
        int(attr_list[0]),  # id: int = -1
        attr_list[1],  # name: string = 'Default'
        attr_list[2],  # type: string = 'NA'
        float(attr_list[3]),  # plant_cost: float = -1
        float(attr_list[4]),  # min_output: float = -1
        float(attr_list[5]),  # max_output: float = -1
        float(attr_list[6]),  # demand: float = -1
        float(attr_list[7]),  # wholesale_cost: float = -1
        float(attr_list[8]),  # water_use: float = -1
        float(attr_list[9])   # carbon_footprint: float = -1
    ))

conditions = get_test_conditions()  # TODO import conditions from file
weights = get_test_weights()  # TODO import weights from file

# adapted from main. pretty prints the result <3
# TODO: write results to file in a godot-readable way
best_option = optimize('cost_water_carbon', plant_list, conditions, weights, 
                  #      n_runs=2, n_threads=2, 
                       pop_size=300, save_best=True
                       )

print(f'Your best option based on the provided weights is:\n'
      f'    Cost:   {best_option[0][0]}\n'
      f'    Water:  {best_option[0][1]}\n'
      f'    Carbon: {best_option[0][2]}\n')

print_result(plant_list, best_option[1], best_option[0], best_option[2])
