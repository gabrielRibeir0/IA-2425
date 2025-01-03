class Node:
    def __init__(self, id, population, priority, timeLimit, needs): #TODO ver questao de poder haver reabastecimento em algumas zonas
        self.id = id
        self.population = population
        self.priority = priority #TODO ver questao prioridade, gravidade e poopulacao
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