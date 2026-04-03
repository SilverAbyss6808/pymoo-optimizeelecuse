# eventually, this will be what reads the input from the ui
# for now, its hardcoded lmfaooooo

from powerplant import PowerPlant
import re


def import_info_from_godot(infile):
    unformatted_file_contents = ''
    with open(infile) as f:
        unformatted_file_contents = f.read()

    # deconstructing the file from godot to make it easier to use
    godot_dict_regex = re.compile(r'{.*?}')  # it should find three of these: plants, conditions, weights
    godot_dicts = re.findall(godot_dict_regex, unformatted_file_contents)

    # get plants from first dict
    godot_dict_item_regex = re.compile(r'(?:(?:"[\w\s.]+")|(?:[\w\s.]+)):(?:\[(?:(?:(?:"[\w\s.]+")|(?:[\w\s.]+)),?)+]|(?:[\w\s.]+))')
    godot_dict_items = re.findall(godot_dict_item_regex, godot_dicts[0])  # finds key:value pairs

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

    # get conditions from second dict
    cond_raw = re.findall(godot_dict_item_regex, godot_dicts[1])

    conditions = []
    for item in cond_raw: 
        conditions.append(float(item.split(':')[1]))

    # get weights from third dict
    wgt_raw = re.findall(godot_dict_item_regex, godot_dicts[2])

    weights = []
    for item in wgt_raw: 
        weights.append(float(item.split(':')[1]))

    return plant_list, conditions, weights


def get_test_plants():
    plants = []

    # id, name, type, plant_cost, min_output, max_output, demand, wholesale_cost, water_use, carbon_footprint
    plants.append(PowerPlant(  1,                  'Springfield Nuclear',             'Nuclear', 0.11, 1700,   2300,   2300, 0.11, 100,  10 ))
    plants.append(PowerPlant(  2,                          'Moria Mines',                'Coal', 0.13,  500,   1700, 920.85, 0.13,  50,   5 ))
    plants.append(PowerPlant(  3,                'Bog of Eternal Stench',         'Natural Gas', 0.12,  150,    400,  400.0, 0.12,  15,   2 ))
    plants.append(PowerPlant(  4,        'Winchester Brothers Wind Farm',                'Wind', 0.08,    0,    800,    800, 0.08,   0,   0 ))
    plants.append(PowerPlant(  5,               'Planet Miranda PV Farm',               'Solar', 0.07,    0,    500,    500, 0.07,   0,   0 ))
    plants.append(PowerPlant(  6,               ' Fortnite Steamy Stack',             'Nuclear',  0.1, 1400,   2100,   2100, 0.10, 110,  11 ))
    plants.append(PowerPlant(  7,                    'Silent Hill Power',                'Coal', 0.12,  450,   1500,   1500, 0.12,  60,   9 ))
    plants.append(PowerPlant(  8,              'Dune Spice Fossil Plant',                'Coal', 0.14,  200,    500,      0, 0.00,  70,   4 ))
    plants.append(PowerPlant(  9,                     'Shelbyville Coal',                'Coal', 0.13,  150,    400, 289.58, 0.13,  55,   6 ))
    plants.append(PowerPlant( 10,                    'Hilltop Gas Plant',      'CC Natural Gas', 0.11,  600,   1200,   1200, 0.11,  17,   3 ))
    plants.append(PowerPlant( 11,                'Liquid Schwartz Power',         'Natural Gas', 0.12,  200,    900,  900.0, 0.12,  13,   1 ))
    plants.append(PowerPlant( 12,                 'Oil Ocean Zone Power',         'Natural Gas', 0.12,  150,    500,  500.0, 0.12,  20,   2 ))
    plants.append(PowerPlant( 13,                 'Alexandria Wind Farm',                'Wind', 0.09,  100,    900,    900, 0.09,   0,   0 ))
    plants.append(PowerPlant( 14,               'Racoon City Geothermal',          'Geothermal',  0.1,  300,   1100,   1100, 0.10,   5, .02 ))
    plants.append(PowerPlant( 15,                  'Catan Biomass Plant',             'Biomass', 0.13,  100,    300, 189.58, 0.13,  95,   5 ))
    plants.append(PowerPlant( 16, 'Death Star Concentrating Solar Plant', 'Concentrating Solar', 0.14,  100,    700,      0, 0.00, 100,   1 ))

    return plants


def get_test_conditions():
    conditions = []

    conditions.append(13600)  # total power demand
    conditions.append(0.5)  # amount of sun (float between 0-1)
    conditions.append(0.5) # amount of wind (float between 0-1)

    return conditions


# lower number = higher weight
def get_test_weights():
    weights = []

    weights.append(0.1)  # cost
    weights.append(0.6)  # water
    weights.append(0.3)  # carbon

    return weights

