import os

class Node:
    def __init__(self, id, priority, population):
        self.id = id
        self.priority = priority
        self.population = population

    def getId(self):
        return self.id

