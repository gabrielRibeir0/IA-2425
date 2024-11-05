class Node:
    def __init__(self, id, priority, population, accessibility):
        self.id = id
        self.priority = priority
        self.population = population
        self.accessibility = accessibility

    def getId(self):
        return self.id