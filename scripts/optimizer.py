
# this is gonna be the main script that executes. no ui, call the exe with command line args

import optimize
import sys

# ok args example: 
#   [C:\Users\baxte\anaconda3\envs\pymoo-optimizeelecuse\python.exe 
#   c:/gunk/Code/python/pymoo-optimizeelecuse/scripts/optimizer.py] 
#   plant_list condition_list weight_list

# first arg is list of plants: any number, formatted like 
#   [PowerPlant(id, name, type, plant_cost, min_output, max_output, demand, wholesale_cost, water_use, carbon_footprint), ...]
# second is list of conditions: [power, sun, wind]
# third is list of weights: [cost, water, carbon]

# reads all command line args except for name of file
args = sys.argv[1:]

print(args)

