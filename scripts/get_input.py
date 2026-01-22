# eventually, this will be what reads the input from the ui
# for now, its hardcoded lmfaooooo

from powerplant import PowerPlant


def get_test_plants():
    plants = []

    # id, name, type, plant_cost, min_output, max_output, demand, wholesale_cost, water_use, carbon_footprint
    plants.append(PowerPlant(1, 'Springfield Nuclear', 'Nuclear', 0.11, 1700, 2300, 2300, 0.11, 0.5, 0.5))
    plants.append(PowerPlant(2,'Moria Mines', 'Coal', 0.13, 500, 1700, 920.85, 0.13, 0.5, 0.5))
    plants.append(PowerPlant(3,'Bog of Eternal Stench', 'Natural Gas', 0.12, 150, 400, 400.0, 0.12, 0.5, 0.5))
    plants.append(PowerPlant(4,'Winchester Brothers Wind Farm', 'Wind', 0.08, 0, 800.0, 800, 0.08, 0.5, 0.5))
    plants.append(PowerPlant(5,'Planet Miranda PV Farm', 'Solar ', 0.07, 0, 500, 500, 0.07, 0.5, 0.5))
    plants.append(PowerPlant(6,'Fortnite Steamy Stack', 'Nuclear ', 0.1, 1400, 2100, 2100, 0.1, 0.5, 0.5))
    plants.append(PowerPlant(7,'Silent Hill Power', 'Coal', 0.12, 450, 1500, 1500, 0.12, 0.5, 0.5))
    plants.append(PowerPlant(8,'Dune Spice Fossil Plant', 'Coal', 0.14, 200, 500, 0, 0.0, 0.5, 0.5))
    plants.append(PowerPlant(9,'Shelbyville Coal', 'Coal', 0.13, 150, 400, 289.58, 0.13, 0.5, 0.5))
    plants.append(PowerPlant(10,'Hilltop Gas Plant', 'CC Natural Gas', 0.11, 600, 1200, 1200, 0.11, 0.5, 0.5))
    plants.append(PowerPlant(11,'Liquid Schwartz Power', 'Natural Gas', 0.12, 200, 900, 900.0, 0.12, 0.5, 0.5))
    plants.append(PowerPlant(12,'Oil Ocean Zone Power', 'Natural Gas', 0.12, 150, 500, 500.0, 0.12, 0.5, 0.5))
    plants.append(PowerPlant(13,'Alexandria Wind Farm', 'Wind', 0.09, 100.0, 900.0, 900, 0.09, 0.5, 0.5))
    plants.append(PowerPlant(14,'Racoon City Geothermal', 'Geothermal', 0.1, 300, 1100, 1100, 0.1, 0.5, 0.5))
    plants.append(PowerPlant(15,'Catan Biomass Plant', 'Biomass', 0.13, 100, 300, 189.58, 0.13, 0.5, 0.5))
    plants.append(PowerPlant(16,'Death Star Concentrating Solar Plant', 'Concentrating Solar', 0.14, 100, 700, 0, 0.0, 0.5, 0.5))

    return plants


def get_test_conditions():
    conditions = []

    conditions.append(13600)  # total power demand
    conditions.append(0.5)  # amount of sun (float between 0-1)
    conditions.append(0.5) # amount of wind (float between 0-1)

    return conditions

