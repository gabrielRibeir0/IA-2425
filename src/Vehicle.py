class Vehicle:
    def __init__(self, id, type,gas,location): #volume da capacidade??
        self.id = id
        self.weight = 0
        self.gas = gas # combustivel disponivel
        self.location = location
        self.availability = True
        self.type = type
        if self.type == "Car":
            self.maxGas = 60
            self.maxcapacity = 400 #kg
            self.averageSpeed = 90 #km/h
            self.gasConsume = 0.08 #l/km
        elif self.type == "Truck":
            self.maxGas = 350
            self.maxcapacity = 15000
            self.averageSpeed = 60
            self.gasConsume = 0.4
        elif self.type == "Boat":
            self.maxGas = 120
            self.maxcapacity = 1000
            self.averageSpeed = 25
            self.gasConsume = 0.5
        else:  # self.vehicleType == "Plane"
            self.maxGas = 300
            self.maxcapacity = 5
            self.averageSpeed = 250
            self.gasConsume = 1

    #se calhar fazia sentido a velocidade variar consoante o peso que se leva


    def validate_weight(self,packageweight):
        if self.maxcapacity - self.weight >= packageweight:
            return True

    def max_mileage(self):
        return self.gas/self.gasConsume

    def travel_time(self, distance):      # dá return em minutos
        return (distance/self.averageSpeed)/60

    def can_deliver(self,packageweight,distance,time):
        return self.validate_weight(packageweight) and self.max_mileage()>=distance and self.travel_time(distance)<=time
