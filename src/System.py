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
        self.vehicles = [Vehicle.Vehicle(1, Vehicle.VehicleType.CAR), Vehicle.Vehicle(2, Vehicle.VehicleType.TRUCK), Vehicle.Vehicle(3, Vehicle.VehicleType.CAR)]
        self.vehicleRoutes = {}
        self.vehicleSupplyZones = {}
        for vehicle in self.vehicles:
            self.vehicleRoutes[vehicle.id] = []
    
    def run(self, algorithm, criteria):
        apply_dinamic_conditions() #TODO gerar as condições dinamicas

        sorted_zones = [zone.id for zone in self.zones.values() if zone.isUnserviced()]
        if criteria == "Tempo":
            sorted_zones.sort(key=lambda zone_id: self.zones[zone_id].timeLimit)
        elif criteria == "Prioridade":
            sorted_zones.sort(key=lambda zone_id: self.zones[zone_id].priority, reverse=True)

        for destination_zone in sorted_zones:
            if not self.zones[destination_zone].isUnserviced():
                continue

            bestVehicle = None
            bestGasConsume = float('inf')

            for vehicle in self.vehicles:
                if not vehicle.available or not vehicle.validate_weight(self.zones[destination_zone].getWeightNeeds()):
                    continue
                
                route = self.graph.get_route(destination_zone, vehicle.currentLocation, algorithm).reverse() #TODO ver coiso que a julia disse de correr todos para depois comparar
                if route is None:
                    continue
                
                distance = self.graph.calculate_cost(route)
                if vehicle.travel_time(distance) <= self.zones[destination_zone].timeLimit: #TODO juntar as condições aqui
                    if bestVehicle is None or vehicle.gasConsume * distance < bestGasConsume:
                        if bestVehicle is not None:
                            self.vehicleRoutes[bestVehicle.id] = []
                        bestVehicle = vehicle
                        bestGasConsume = vehicle.gasConsume * distance
                        self.vehicleRoutes[bestVehicle.id] = route
            #TODO fiqei aqui
            if bestVehicle is not None:
                bestVehicle.startTrip(zoneId, self.vehiclePlannedRoutes[bestVehicle.id][1])
                self.zones[zoneId].expected_supplies = self.zones[zoneId].needs
                self.vehicleSupplyZones[bestVehicle.id] = {zoneId: self.zones[zoneId].needs}
                self.vehiclePlannedRoutes[bestVehicle.id].pop(0)
                self.unserviced_zones.remove(zoneId)
                self.vehicleActualRoutes[bestVehicle.id].append(bestVehicle.currentLocation)
                remainingWeight = bestVehicle.maxCapacity - self.zones[zoneId].getWeightNeeds()
                self.supplyOtherZones(bestVehicle.id, remainingWeight)


    def reRoute(self, vehicle):
        if(self.graph.checkBlockedEdges(self.vehiclePlannedRoutes[vehicle.id])):
            newRoute = self.procura_aStar(vehicle.destination, vehicle.currentLocation)
            if newRoute is None:
                return False
            blockedZones = list(set(self.vehiclePlannedRoutes[vehicle.id]) - set(newRoute))
            newZones = list(set(newRoute) - set(self.vehiclePlannedRoutes[vehicle.id]))
            for zone in blockedZones:
                self.zones[zone].expected_supplies -= self.vehicleSupplyZones[vehicle.id][zone]
                self.vehicleSupplyZones[vehicle.id][zone] = 0
            self.vehiclePlannedRoutes[vehicle.id] = newRoute
            self.supplyOtherZones(vehicle.id, vehicle.weight - self.zones[vehicle.finalDestination].getWeightNeeds())
        return True


    def supplyOtherZones(self, bestVehicleId, remainingWeight):
        for zone in self.vehiclePlannedRoutes[bestVehicleId]:
            if remainingWeight <= 0:
                break
            if self.zones[zone].isUnserviced():
                quantity = min(remainingWeight, self.zones[zone].getWeightNeeds() - self.zones[zone].expected_supplies)
                if quantity > 0:
                    remainingWeight -= quantity
                    self.zones[zone].expected_supplies += quantity
                    self.vehicleSupplyZones[bestVehicleId][zone] = quantity
                    if not self.zones[zone].isUnserviced():
                        self.unserviced_zones.remove(zone)


    def find_best_next_zone(self, vehicle, current_zone, unserviced_zones):
        best_score = float('-inf')
        best_zone = None

        for zone_id in unserviced_zones:
            zone = self.zones[zone_id]
            if not vehicle.can_access_terrain(zone.terrain_type):
                continue

            travel_time = self.calculate_travel_time(vehicle, current_zone, zone_id)
            if travel_time == float('inf'):
                continue

            # Score based on priority, population, and travel time
            score = (zone.priority * 100 +
                     zone.population / 1000 -
                     travel_time * 10)

            if score > best_score:
                best_score = score
                best_zone = zone_id

        return best_zone

    def saveData(self):
        print("Talvez guardar dados sobre os resultados")