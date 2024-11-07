class Package:
    def __init__(self,id,location,destination,weight): #delivery time limit?
        self.id = id
        self.location = location
        self.destination = destination
        self.weight = weight

        def getId(self):
            return self.id

        def getLocation(self):
            return self.location

        def getDestination(self):
            return self.destination

        def getWeight(self):
            return self.weight

