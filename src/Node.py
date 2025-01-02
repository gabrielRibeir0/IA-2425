class Node:
    def __init__(self, id, population, priority, timeLimit, needs):
        self.id = id
        self.population = population
        self.priority = priority
        self.timeLimit = timeLimit
        if needs is None: 
            self.needs = 0
        else: 
            self.needs = needs
        self.current_supplies = 0
        self.expected_supplies = 0

    def isUnserviced(self):
        if self.current_supplies < self.needs and self.expected_supplies < self.needs:
            return True
        return False

    def getId(self):
        return self.id

    def getWeightNeeds(self):
        return self.needs