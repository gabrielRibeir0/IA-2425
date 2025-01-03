from enum import Enum
import os
import json

class VehicleType(Enum):
    CAR = "car"
    TRUCK = "truck"
    BOAT = "boat"
    HELICOPTER = "helicopter"
    
class Vehicle:
    def __init__(self, id, type):
        self.id = id
        self.weight = 0
        self.available = True
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
        
    #se calhar fazia sentido a velocidade variar consoante o peso que se leva


    def validate_weight(self, destination_needs):
        if self.maxCapacity >= destination_needs:
            return True
        return False

    def max_mileage(self):
        return self.gas/self.gasConsume

    def travel_time(self, distance):      # dá return em minutos
        return (distance/self.averageSpeed)/60

    def can_deliver(self,packageweight,distance,time):
        return self.validate_weight(packageweight) and self.max_mileage()>=distance and self.travel_time(distance)<=time
    
def loadVehicles():
    filepath = os.path.join(os.path.dirname(__file__), '..', 'data', 'vehicles.json')

    with open(filepath, 'r') as file:
        loaded_data = json.load(file)

    list = []
    for vehicle in loaded_data["vehicles"]:
        if vehicle['tipo'] == "car":
            type = VehicleType.CAR
        elif vehicle['tipo'] == "truck":
            type = VehicleType.TRUCK
        elif vehicle['tipo'] == "boat":
            type = VehicleType.BOAT
        else:
            type = VehicleType.HELICOPTER
        v = Vehicle(vehicle['id'], type)
        list.append(v)
    return list
