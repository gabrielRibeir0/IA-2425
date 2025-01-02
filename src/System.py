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
    
    def run(self):
        routes = []
        unserviced_zones = list(zone.id for zone in self.zones.values()
                               if zone.isUnserviced())
        unserviced_zones.sort(key=lambda z: self.zones[z].priority)
        toBeServicedZones = []
        turno = 0

        while unserviced_zones:
            turno += 1
            for zoneId in unserviced_zones:
                #veiculos que estao a mover continuam a avançar
                #veiculos que chegaram a uma zona verifica se o caminho que têm ainda está disponivel
                #encontram o novo melhor caminho, zonas do outro caminho que nao sao usadas sao adicionadas a lista de zonas a serem servidas
                #se o caminho que têm ainda está disponivel, continuam

                #cada veiculo disponivel vai tentar ir a zona que ja nao esteja a tentar ser servida
                #comparar gasto de combustivel e distancia percorrida
                #o melhor começa a ir a zona e adiciona zonas do caminho a lista que vai ser servida
                for vehicle in self.vehicles:
                    current_route = []
                    current_zone = min(unserviced_zones,
                                    key=lambda z: self.zones[z].priority)

                    while (vehicle.current_capacity > 0 and
                        vehicle.current_fuel > 0 and
                        unserviced_zones):

                        next_zone = self.find_best_next_zone(vehicle, current_zone, unserviced_zones)
                        if not next_zone:
                            break

                        path = self.a_star_search(current_zone, next_zone, vehicle)
                        current_route.extend(path[1:])  # Exclude current zone to avoid duplicates

                        # Update vehicle resources and zone supplies
                        delivery = min(vehicle.current_capacity,
                                    self.zones[next_zone].needs -
                                    self.zones[next_zone].current_supplies)

                        vehicle.current_capacity -= delivery
                        self.zones[next_zone].current_supplies += delivery

                        if self.zones[next_zone].current_supplies >= self.zones[next_zone].needs:
                            unserviced_zones.remove(next_zone)

                        current_zone = next_zone

                    if current_route:
                        routes.append((vehicle, current_route))

        print("\nOptimized Distribution Routes:")
        for vehicle, route in routes:
            print(f"\nVehicle Type: {vehicle.type.value}")
            print(f"Route: {' -> '.join(route)}")

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