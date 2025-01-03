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
            self.needs = 0
        else:
            self.needs = needs #TODO ver questao de haver varios tipos de necessidades
        self.current_supplies = 0

    def isUnserviced(self):
        if self.id == "base":
            return False

        if self.current_supplies < self.needs:
            return True
        return False

    def getId(self):
        return self.id

    def getWeightNeeds(self):
        return self.needs