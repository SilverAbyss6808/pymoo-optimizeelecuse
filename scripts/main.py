
from get_input import get_test_plants, get_test_conditions
from optimize import optimize

# === main script. change as needed to emulate taking inputs. ===

opt_type = ''
plants = []
conditions = []
kwargs = []
weights = []
result_list = []

# choose optimization type
print(f'Optimizing for cost, water, and carbon.')

# input plants
print(f'Using plants from get_test_plants().')
plants = get_test_plants()

# input conditions
print(f'Using conditions from get_test_conditions().')
conditions = get_test_conditions()

# input weights: cost - water - carbon, in that order
print(f'Input weights: (using defaults)')  # SMALLER VALUES ARE HIGHER PRIORITY
weights = [0.1, 0.6, 0.3]  # must add to 1
print(f'Using weights {weights[0]} (cost), {weights[1]} (water), {weights[2]} (carbon).')

# optimization: returns a single best option based on weighting (or just best, in case of opt_type='cost')
best_option = optimize('cost_water_carbon', plants, conditions, weights, 
                       n_runs=2, n_threads=2, pop_size=300, save_best=True)

print(f'Your best option based on the provided weights is:\n'
      
      f'    Cost:   {best_option[0]}\n'
      f'    Water:  {best_option[1]}\n'
      f'    Carbon: {best_option[2]}\n')

