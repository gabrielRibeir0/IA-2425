class Node:
    def __init__(self, id, population, priority, timeLimit, needs):
        self.id = id
        self.population = population
        self.priority = priority
        self.timeLimit = timeLimit
        if needs is None: 
            self.needs = {} 
        else: 
            self.needs = needs
        self.current_supplies = {}
        for resource in self.needs:
            self.current_supplies[resource] = 0

    def isUnserviced(self):
        if not self.needs:
            return True

        for resource in self.needs:
            if self.current_supplies[resource] < self.needs[resource]:
                return True
        return False

    def getId(self):
        return self.id

