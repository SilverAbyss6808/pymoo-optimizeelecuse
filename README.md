# General Information

The purpose of this repository is to optimize a list of power plants based on how much power is currently required by the grid and how much sun/wind there is (for things like solar/wind plants that will have their output capabilities change with the weather). The plants can be optimized for lowest monetary cost, water usage, carbon footprint, or any combination of the three.


This repository can be used both as a package included in another repository or as a standalone executable. It was created to be called from a Godot game, which will explain some of the stranger formatting mentioned below.

# How to Use
### As part of another script:
1. Install required packages with ```pip install -r requirements.txt```.
2. Import ```optimize``` at the top of your file with ```from optimize import optimize```.


To use the optimization function, simply call it with ```optimize(<opt_type>, <power_plants>, <conditions>, <weights>, <keyword_arguments>)```. It will return a ```list``` of three ```list```s (F: most optimal cost, water use, and carbon emissions, respectively; X: best cost distribution; G: constraint violations) if you should want them, but you can also just ignore them and let the optimizer display them for you.

### As a standalone executable (no Python environment required!):
Note that this is intended primarily for use with the Godot game engine.


In a terminal window, run the command ```path\to\pymoo-optimizeelecuse\dist\optimizer\optimizer.exe path\to\yourinputfile.plant```, where the paths are changed to their locations on your machine (can be relative or absolute), and the ```.plant``` input file is a text file formatted as a Godot dictionary. There should be three total dicts: one for plants, one for conditions, and one for weightings. See ```test_infile.plant``` for an example of how to format the file. There can be any number of plants, but there must be only three items in both the "conditions" and "weightings" dictionaries. See previous section for notes on what types should be included and what they mean.


The executable returns three things: 
1. A rotating, three-dimensional GIF of the Pareto front returned by the optimization. The program's most optimal plant found is indicated with a **red star**, and other high tradeoff points are indicated by **green circles**. The GIF will be located in the "gifs" folder, which is created in the same folder as the executable.
2. A static PNG showing the same information as above. It will also be located in the "gifs" folder.
3. An ```outfile.plant``` file containing a Godot-formatted dictionary of the optimization's results, plus the absolute paths on your machine of the locations of the two above items. Located in the same directory as the executable.

# Required Arguments
* ```opt_type```: String. Can be either ```'cost'``` to optimize for just overall cost or ```'cost_water_carbon'``` to optimize for those three.
* ```power_plants```: List of PowerPlant objects. *Leave blank for default test data.*
* ```conditions```: List of values following the pattern ```(<total_power_demand>, <sun_percentage>, <wind_percentage>)```. *Leave blank for default test data.*
  * ```total_power```: Integer. Total amount of power needed by the grid.
  * ```sun_percentage```: Float between 0-1. Amount of sun as a percentage at the given time.
  * ```wind_percentage```: Float between 0-1. Amount of wind as a percentage at the given time.
* ```weights```: List of floats following the pattern ```(<cost_weight>, <water_weight>, <carbon_weight>)```. MUST ADD TO 1.0. Note that lower values indicate higher weighting; a weighting of 0.1 will be optimized for more than a weighting of 0.9. For example, a weighting of (0, 0.7, 0.3) will optimize for the lowest cost, then the lowest carbon emissions, then lowest water use.
* ```keyword_arguments```: Completely optional. Extra options for handling output, specifying how long the optimization runs, etc. See "All Keyword Arguments" section for more detail on how they're used.

# Keyword Arguments
Keyword arguments are *generally* unique to the optimization type. Universal kwargs will be listed at the bottom. *Note that this is not an exhausitve list.*

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

# FAQ
### Does this repository need to be run in a specific Python environment?
If it's running as part of another script, yes. You'll need to install the required packages with ```pip install -r requirements.txt```. If you're just running the executable, though, you don't need Python installed at all!


#
```
      |\      _,,,---,,_
ZZZzz /,`.-'`'    -.  ;-;;,_
     |,4-  ) )-,_. ,\ (  `'-'
    '---''(_/--'  `-'\_)
```
