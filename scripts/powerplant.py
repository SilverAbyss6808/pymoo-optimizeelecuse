
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

    def __init__(self, id, name, type, plant_cost, min_output, max_output, demand, wholesale_cost):
        self.id = id
        self.name = name
        self.type = type
        self.plant_cost = plant_cost
        self.min_output = min_output
        self.max_output = max_output
        self.demand = demand
        self.wholesale_cost = wholesale_cost

    def __str__(self):
        return(f'Plant ID:                  {self.id}\n'
               f'Plant Name:                {self.name}\n'
               f'Plant Type:                {self.type}\n'
               f'Plant-Level Cost per kWh:  {self.plant_cost}\n'
               f'Min Output:                {self.min_output}\n'
               f'Max Output:                {self.max_output}\n'
               f'Demand on Plant:           {self.demand}\n'
               f'Wholesale Cost per kWh:    {self.wholesale_cost}\n')