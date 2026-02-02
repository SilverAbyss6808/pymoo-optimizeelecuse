
# a power plant class. thats p much it

import string

class PowerPlant:
    id: int = -1
    name: string = 'Default'
    type: string = 'NA'
    plant_cost: float = -1
    min_output: float = -1
    max_output: float = -1
    demand: float = -1
    wholesale_cost: float = -1
    water_use: float = -1
    carbon_footprint: float = -1

    def __init__(self, id, name, type, plant_cost, min_output, max_output, demand, wholesale_cost, water_use, carbon_footprint):
        self.id = id
        self.name = name
        self.type = type
        self.plant_cost = round(plant_cost, 2)
        self.min_output = round(min_output, 2)
        self.max_output = round(max_output, 2)
        self.demand = round(demand, 2)
        self.wholesale_cost = round(wholesale_cost, 2)
        self.water_use = round(water_use, 2)
        self.carbon_footprint = round(carbon_footprint, 2)


    def __str__(self):
        return(f'Plant ID:                  {self.id}\n'
               f'Plant Name:                {self.name}\n'
               f'Plant Type:                {self.type}\n'
               f'Plant-Level Cost per kWh:  {self.plant_cost}\n'
               f'Min Output:                {self.min_output}\n'
               f'Max Output:                {self.max_output}\n'
               f'Demand on Plant:           {self.demand}\n'
               f'Wholesale Cost per kWh:    {self.wholesale_cost}\n'
               f'Water Use per kWh:         {self.water_use}\n'
               f'Carbon Footprint per kWh:  {self.carbon_footprint}\n')