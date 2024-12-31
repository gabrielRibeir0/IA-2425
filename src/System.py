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
        self.time = 1 # ver depois como se faz a cena do tempo
    
    def run(self):
        routes = []
        unserviced_zones = set(zone.id for zone in self.zones.values()
                               if zone.isUnserviced())

        for vehicle in self.vehicles:
            if not unserviced_zones:
                break

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