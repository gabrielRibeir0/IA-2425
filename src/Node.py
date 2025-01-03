import math

class Node:
    def __init__(self, id, population, severity, timeLimit, needs):
        self.id = id
        if id == "base":
            self.priority = 0
        else:
            normalized_population = math.log10(population + 1) / 7.0
            weighted_severity = severity ** 2
            self.priority = (weighted_severity * 0.6) + (normalized_population * 0.4)

        if timeLimit is None:
            self.timeLimit = float('inf')
        else:
            self.timeLimit = timeLimit
        if needs is None:
            self.needs = {}
        else:
            self.needs = needs
        self.current_supplies = {}
        for need in self.needs:
            self.current_supplies[need] = 0

    def isUnserviced(self):
        if self.id == "base":
            return False

        return any(self.current_supplies[need] < self.needs[need] for need in self.needs)
    
    def supply(self, quantity, all_needs=True, supply=""):
        if all_needs:
            for need in self.needs:
                self.current_supplies[need] += self.needs[need]
        else:
            self.current_supplies[supply] += quantity

    def getId(self):
        return self.id

    def getWeightNeeds(self):
        return sum(self.needs.values())
    
    def getMissingNeeds(self):
        for need in self.needs:
            if self.current_supplies[need] < self.needs[need]:
                quantity = self.needs[need] - self.current_supplies[need]
                yield (need, quantity)


    def reset(self):
        for need in self.needs:
            self.current_supplies[need] = 0