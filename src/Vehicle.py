from enum import Enum

class VehicleType(Enum):
    CAR = "car"
    TRUCK = "truck"
    BOAT = "boat"
    HELICOPTER = "helicopter"
    
class Status(Enum):
    MOVING = 0
    INZONE = 1
    AVAILABLE = 2
    FINISHED = 3
    
class Vehicle:
    def __init__(self, id, type):
        self.id = id
        self.weight = 0
        self.status = Status.AVAILABLE
        self.type = type
        if self.type == VehicleType.CAR:
            self.maxGas = 60
            self.maxCapacity = 400 #kg
            self.averageSpeed = 90 #km/h
            self.gasConsume = 0.08 #l/km
        elif self.type == VehicleType.TRUCK:
            self.maxGas = 450
            self.maxCapacity = 10000
            self.averageSpeed = 60
            self.gasConsume = 0.4
        elif self.type == VehicleType.BOAT:
            self.maxGas = 140
            self.maxCapacity = 1000
            self.averageSpeed = 40
            self.gasConsume = 0.5
        else:
            self.maxGas = 300
            self.maxCapacity = 500
            self.averageSpeed = 250
            self.gasConsume = 1
        self.gas = self.maxGas
        self.currentLocation = "base"
        self.nextDestination = None
        self.finalDestination = None
        self.travelledDistance = 0
        
    #se calhar fazia sentido a velocidade variar consoante o peso que se leva

    def startTrip(self, finalDestination, nextDestination):
        self.status = Status.MOVING
        self.weight = self.maxCapacity
        self.finalDestination = finalDestination
        self.nextDestination = nextDestination
        self.travelledDistance = 0


    def validate_weight(self, packageweight):
        if self.maxCapacity - self.weight >= packageweight:
            return True

    def max_mileage(self):
        return self.gas/self.gasConsume

    def travel_time(self, distance):      # dá return em minutos
        return (distance/self.averageSpeed)/60

    def can_deliver(self,packageweight,distance,time):
        return self.validate_weight(packageweight) and self.max_mileage()>=distance and self.travel_time(distance)<=time
