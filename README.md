# Setup
1. ~~Install required packages with ```pip install -r requirements.txt```.~~
   Download most recent release (currently v0.1.0) from the releases section of this page.
2. In your project terminal, run ```pip install PATHTOFOLDER\pymoo-optimizeelecuse\dist\poeu_scripts-0.1.0-py3-none-any.whl```
3. Import ```optimize``` at the top of your file with ```from optimize import optimize```.

# How to Use
To use the optimization function, simply call it with ```optimize(<opt_type>, <power_plants>, <conditions>, <weights>, <keyword_arguments>)```. It will return a ```list``` of three ```list```s (F: most optimal cost, water use, and carbon emissions, respectively; X: best cost distribution; G: constraint violations) if you should want them, but you can also just ignore them and let the optimizer display them for you.
* ```opt_type```: String. Can be either ```'cost'``` to optimize for just overall cost or ```'cost_water_carbon'``` to optimize for those three.
* ```power_plants```: List of PowerPlant objects. *Leave blank for default test data.*
* ```conditions```: List of values following the pattern ```(<total_power>, <sun_percentage>, <wind_percentage>)```. *Leave blank for default test data.*
  * ```total_power```: Integer. Total amount of power needed by the grid.
  * ```sun_percentage```: Float between 0-1. Amount of sun as a percentage at the given time.
  * ```wind_percentage```: Float between 0-1. Amount of wind as a percentage at the given time.
* ```weights```: List of three integers between 0-1. MUST add to 1. Follows the pattern ```(<cost_weight>, <water_weight>, <carbon_weight>)```.
  * Note here: Lower values are considered to be weighted more heavily than higher ones. For example, considering a list with values ```(0.1, 0.6, 0.3)```, the function will optimize most for cost and least for water usage.
* ```keyword_arguments```: Completely optional. Extra options for handling output, specifying how long the optimization runs, etc. See "All Keyword Arguments" section for more detail on how they're used.

## All Keyword Arguments
Keyword arguments are *generally* unique to the optimization type. Universal kwargs will be listed at the bottom.

### opt_type = 'cost':
* ```graph_best_res```: ```True``` | (default) ```False```. Whether or not a MatPlotLib window opens at the end with a graph of the single best result.

### opt_type = 'cost_water_carbon':
* ```show_best```: ```True``` | (default) ```False```. Whether or not the Pareto front is shown in a MatPlotLib window.
* ```save_best```: ```True``` | (default) ```False```. Whether or not the Pareto front is saved. If true, will be saved both as a PNG and as a rotating GIF.

### Universal kwargs:
* ```alert_when_done```: ```True``` | (default) ```False```. Windows only. Displays a popup window when the optimization is complete.
* ```pop_size```: Integer. Default 250. Controls the size of the initial population.
* ```num_gens```: Integer. Default 50. How many generations the optimization runs over.
* ```n_runs```: Integer. Default 16. How many different times the optimization runs. The best result(s) are returned.
* ```n_threads```: Integer. Default 8. Number of threads used.  **Should be a factor of ```n_runs```.**

### Other kwargs:
* opt_helpers.print_result()
  * ```long```: ```True``` | (default) ```False```. Shows more detailed information about each plant's contributions and cost in the terminal.


#
```
      |\      _,,,---,,_
ZZZzz /,`.-'`'    -.  ;-;;,_
     |,4-  ) )-,_. ,\ (  `'-'
    '---''(_/--'  `-'\_)
```
