
import os


# be aware that this overwrites prev file contents
def write_results_for_godot(best_option):
    out_string = '{'  # cant format as python dict or godot wont read it right

    # best_options[0] is F --> total cost, total water, total carbon (ex. F = [867000. 762500.  29090.])
    out_string += ( f'"total_cost":{best_option[0][0]},'
                    f'"water_usage":{best_option[0][1]},'
                    f'"carbon_emissions":{best_option[0][2]},')

    # best_options[1] is X --> power output of each plant (ex. X = [1700 2400 5000 4500    0])
    for p_id, mw_gen in enumerate(best_option[1]):
        out_string += f'{p_id}:{mw_gen},'

    # best_options[2] is G --> constraint violations ()
    out_string += f'"constraint_violations":['
    for i, cv in enumerate(best_option[2]):
        out_string += f'{cv}'
        if i+1 < len(best_option[2]): out_string += ','
        else: out_string += '],'  # close brackets after last value

    # include path to png and gif so the game can find them to display
    out_string += f'"png_path":"{os.path.abspath('gifs/pareto.png')}",'
    out_string += f'"gif_path":"{os.path.abspath('gifs/pareto.gif')}"'

    # end dict
    out_string += '}'

    # creates outfile if it doesnt exist, overwrites if it does
    with open("outfile.txt", "w") as f:
        f.write(out_string)

