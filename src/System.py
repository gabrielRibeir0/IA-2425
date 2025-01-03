from Graph import Graph
import Vehicle
import os

class System:
    def __init__(self):
        self.graph = Graph()
        self.graph.loadGraph()
        self.zones = {}
        for zone in self.graph.nodes:
            self.zones[zone.id] = zone
        self.vehicles = Vehicle.loadVehicles()
        self.vehicleRoutes = {}
        self.vehicleSupplyZones = {}
        for vehicle in self.vehicles:
            self.vehicleRoutes[vehicle.id] = []
    
    def run(self, algorithm, criteria):
        #apply_dinamic_conditions() #TODO gerar as condições dinamicas

        sorted_zones = [zone.id for zone in self.zones.values() if zone.isUnserviced()]
        if criteria == "Tempo":
            sorted_zones.sort(key=lambda zone_id: self.zones[zone_id].timeLimit)
        elif criteria == "Prioridade":
            sorted_zones.sort(key=lambda zone_id: self.zones[zone_id].priority, reverse=True)

        for destination_zone in sorted_zones:
            if not self.zones[destination_zone].isUnserviced():
                continue

            bestVehicle = None
            bestRatio = (float('-inf'), float('-inf'), float('-inf')) # ratioZonesGas, totalWeightSupplied, numberServicedZones
            bestRoute = []

            for vehicle in self.vehicles:
                if not vehicle.available or not vehicle.validate_weight(self.zones[destination_zone].getWeightNeeds()):
                    continue
                
                result = self.graph.get_route(destination_zone, "base", vehicle, algorithm) #TODO ver coiso que a julia disse de correr todos para depois comparar
                if result is None:
                    continue
                (route, distance) = result
                route.reverse()
                gas_consumed = vehicle.gasConsume * distance
                if self.graph.travel_time(route, vehicle.averageSpeed) <= self.zones[destination_zone].timeLimit and gas_consumed <= vehicle.maxGas:
                    (numberServicedZones, totalWeightSupplied) = self.supplyOtherZones(vehicle.id, vehicle.maxCapacity - self.zones[destination_zone].getWeightNeeds(), True)
                    ratioZonesGas = numberServicedZones / gas_consumed
                    if ratioZonesGas > bestRatio[0]:
                        bestVehicle = vehicle
                        bestRatio = (ratioZonesGas, totalWeightSupplied, numberServicedZones)
                        bestRoute = route
                    elif ratioZonesGas == bestRatio[0]:
                        if totalWeightSupplied > bestRatio[1]:
                            bestVehicle = vehicle
                            bestRatio = (ratioZonesGas, totalWeightSupplied, numberServicedZones)
                            bestRoute = route
                        elif gas_consumed == bestRatio[1]:
                            if numberServicedZones > bestRatio[2]:
                                bestVehicle = vehicle
                                bestRatio = (ratioZonesGas, totalWeightSupplied, numberServicedZones)
                                bestRoute = route
            
            if bestVehicle is not None:
                bestVehicle.available = False
                self.zones[destination_zone].supply(self.zones[destination_zone].getWeightNeeds())
                self.vehicleRoutes[bestVehicle.id] = bestRoute
                self.vehicleSupplyZones[bestVehicle.id] = {destination_zone: self.zones[destination_zone].needs}
                remainingWeight = bestVehicle.maxCapacity - self.zones[destination_zone].getWeightNeeds()
                self.supplyOtherZones(bestVehicle.id, remainingWeight)
        
        for v in self.vehicles:
            if self.vehicleRoutes[v.id]:
                print("Veículo " + str(v.id) + " (" + str(v.type.name) + ") :")
                print("Rota: " + str(self.vehicleRoutes[v.id]))
                print("Entregou suprimentos em: " + str(self.vehicleSupplyZones[v.id]) + "\n")


    def supplyOtherZones(self, bestVehicleId, remainingWeight, test=False):
        numberServicedZones = 0
        totalWeightSupplied = 0
        for zone in self.vehicleRoutes[bestVehicleId]:
            if remainingWeight <= 0:
                break
            if self.zones[zone].isUnserviced():
                missingNeeds = self.zones[zone].getMissingNeeds()
                for need, quantity in missingNeeds:
                    q = min(quantity, remainingWeight)
                    if q > 0:
                        if not test:
                            self.zones[zone].current_supplies[need] += q
                            if zone in self.vehicleSupplyZones[bestVehicleId]:
                                self.vehicleSupplyZones[bestVehicleId][zone][need] = q
                            else:
                                self.vehicleSupplyZones[bestVehicleId][zone] = {need: q}
                        remainingWeight -= q
                        totalWeightSupplied += q
                        if not self.zones[zone].isUnserviced():
                            numberServicedZones += 1
                    if remainingWeight <= 0:
                        break
        return (numberServicedZones, totalWeightSupplied)