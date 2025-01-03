from Graph import Graph
import Vehicle

algorithms = {"CONDITIONS":"", "A*": "", "Greedy": "", "DFS": "", "BFS": ""}

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
    
    def run(self, criteria):
        text = self.graph.apply_dinamic_conditions()
        algorithms["CONDITIONS"] = text

        sorted_zones = [zone.id for zone in self.zones.values() if zone.isUnserviced()]
        if criteria == "Tempo":
            sorted_zones.sort(key=lambda zone_id: self.zones[zone_id].timeLimit)
        elif criteria == "Prioridade":
            sorted_zones.sort(key=lambda zone_id: self.zones[zone_id].priority, reverse=True)

        for algorithm in algorithms:
            if algorithm == "CONDITIONS":
                continue
            self.startSearch(sorted_zones, algorithm)
            self.reset()

        return algorithms
    

    def startSearch(self, sorted_zones, algorithm):
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
                (numberServicedZones, totalWeightSupplied) = self.supplyOtherZones(vehicle.id, vehicle.maxCapacity - self.zones[destination_zone].getWeightNeeds(), True)
                if self.graph.travel_time(route, vehicle.averageSpeed, totalWeightSupplied + self.zones[destination_zone].getWeightNeeds()) <= self.zones[destination_zone].timeLimit and gas_consumed <= vehicle.maxGas:
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
                (numberServicedZones, totalWeightSupplied) = self.supplyOtherZones(bestVehicle.id, remainingWeight)
                bestVehicle.carryingWeight = totalWeightSupplied + self.zones[destination_zone].getWeightNeeds()
        
        result = self.getResults()
        algorithms[algorithm] = result
        

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
    
    def reset(self):
        for vehicle in self.vehicles:
            vehicle.available = True
            vehicle.carryingWeight = 0
            self.vehicleRoutes[vehicle.id] = []
            self.vehicleSupplyZones[vehicle.id] = {}
        for zone in self.zones.values():
            zone.reset()
    

    def getResults(self):
        result_text = ""
        
        for v in self.vehicles:
            if self.vehicleRoutes[v.id]:
                result_text += f"Veículo {str(v.id)} ({str(v.type.name)}):\n"
                result_text += f"  Rota: {str(self.vehicleRoutes[v.id])}\n"
                
                custo = self.graph.calculate_cost(self.vehicleRoutes[v.id])
                result_text += f"  Custo: {str(custo)}km e gasto de {str(v.gasConsume * custo)}l de combustível\n"
                result_text += f"  Entregou suprimentos em: {str(self.vehicleSupplyZones[v.id])}\n\n"
        
        return result_text