
# be aware that this overwrites prev file contents
def write_results_for_godot(results):
    out_string = ''

    # creates outfile if it doesnt exist, overwrites if it does
    with open("outfile.txt", "w") as f:
        f.write(out_string)

