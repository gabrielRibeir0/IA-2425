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
        self.packages = []
        self.vehicles = []
        self.unserviced_zones = list(zone.id for zone in self.zones.values()
                                if zone.isUnserviced())
        self.unserviced_zones.sort(key=lambda z: self.zones[z].priority)
        self.vehiclePlannedRoutes = {}
        self.vehicleActualRoutes = {}
        for vehicle in self.vehicles:
            self.vehicleActualRoutes[vehicle.id] = []
            self.vehiclePlannedRoutes[vehicle.id] = []
    
    def run(self):
        #vehicle.sort(key=lambda x: x.type)

        turno = 0

        while self.unserviced_zones:
            turno += 1
            #mexer os veiculos que ja se mexeram
            for vehicle in self.vehicles:
                if vehicle.status == Vehicle.Status.MOVING:
                        if vehicle.travelledDistance + vehicle.averageSpeed >= self.graph.get_arc_cost(vehicle.currentLocation, vehicle.nextDestination):
                            vehicle.currentLocation = vehicle.nextDestination
                            vehicle.status = Vehicle.Status.INZONE
                            vehicle.travelledDistance = 0
                        else:
                            vehicle.travelledDistance += vehicle.averageSpeed
                elif Vehicle.Status.INZONE:
                    self.vehicleActualRoutes[vehicle.id].append(vehicle.currentLocation)
                    newRoute = self.a_star_search(vehicle.currentLocation, vehicle.destination, vehicle)
                    if newRoute != self.vehiclePlannedRoutes[vehicle.id]:
                        blockedZones = list(set(self.vehiclePlannedRoutes[vehicle.id]) - set(newRoute))
                        newZones = list(set(newRoute) - set(self.vehiclePlannedRoutes[vehicle.id]))

                        self.vehiclePlannedRoutes[vehicle.id] = newRoute
                    vehicle.status = Vehicle.Status.MOVING 

            #por veiculos parados na base a mexer
            for zoneId in self.unserviced_zones:
                bestVehicle = None
                bestGasConsume = float('inf')
                for vehicle in self.vehicles:
                    if vehicle.status == Vehicle.Status.AVAILABLE and vehicle.maxCapacity >= self.zones[zoneId].getTotalWeightNeeds():
                        thisRoute = self.graph.a_star_search(zoneId, vehicle.currentLocation, vehicle).reverse()
                        if thisRoute is not None:
                            distance = self.graph.calculate_cost(self.vehiclePlannedRoutes[vehicle.id])
                            if bestVehicle is None or vehicle.gasConsume * distance < bestGasConsume:
                                self.vehiclePlannedRoutes[bestVehicle.id] = []
                                bestVehicle = vehicle
                                bestGasConsume = vehicle.gasConsume * distance
                                self.vehiclePlannedRoutes[bestVehicle.id].extend(thisRoute[1:])
                if bestVehicle is not None:
                    bestVehicle.startTrip(zoneId, self.vehiclePlannedRoutes[bestVehicle.id][1])
                    self.zones[zoneId].expected_supplies = self.zones[zoneId].needs
                    self.vehiclePlannedRoutes[bestVehicle.id].pop(0)
                    self.unserviced_zones.remove(zoneId)
                    self.vehicleActualRoutes[bestVehicle.id].append(bestVehicle.currentLocation)
                    remainingWeight = bestVehicle.maxCapacity - self.zones[zoneId].getWeightNeeds()
                    self.supplyOtherZones(bestVehicle.id, remainingWeight)

    def supplyOtherZones(self, bestVehicleId, remainingWeight):
        for zone in self.vehiclePlannedRoutes[bestVehicleId]:
            if remainingWeight <= 0:
                break
            if self.zones[zone].isUnserviced():
                quantity = min(remainingWeight, self.zones[zone].getTotalWeightNeeds() - self.zones[zone].expected_supplies)
                remainingWeight -= quantity
                self.zones[zone].expected_supplies += quantity
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