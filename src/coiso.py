from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple
import heapq
from collections import defaultdict

class VehicleType(Enum):
    DRONE = "drone"
    HELICOPTER = "helicopter"
    BOAT = "boat"
    TRUCK = "truck"


class WeatherCondition(Enum):
    CLEAR = "clear"
    STORM = "storm"
    HEAVY_RAIN = "heavy_rain"
    FLOOD = "flood"


@dataclass
class Vehicle:
    type: VehicleType
    max_capacity: float  # in kg
    current_capacity: float
    fuel_capacity: float
    current_fuel: float
    speed: float  # base speed in km/h

    def can_access_terrain(self, terrain_type: str) -> bool:
        terrain_accessibility = {
            VehicleType.DRONE: {"air", "urban", "forest", "mountain"},
            VehicleType.HELICOPTER: {"air", "urban", "forest", "mountain"},
            VehicleType.BOAT: {"water"},
            VehicleType.TRUCK: {"urban", "road"}
        }
        return terrain_type in terrain_accessibility[self.type]


@dataclass
class Zone:
    id: str
    position: Tuple[float, float]
    population: int
    priority: int  # 1-10, 10 being highest priority
    terrain_type: str
    needs: float  # required supplies in kg
    time_window: Tuple[int, int]  # (start_time, end_time) in hours
    current_supplies: float = 0


class DistributionSystem:
    def __init__(self):
        self.zones: Dict[str, Zone] = {}
        self.vehicles: List[Vehicle] = []
        self.graph: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.weather_conditions: Dict[str, WeatherCondition] = {}
        self.current_time: int = 0

    def add_zone(self, zone: Zone):
        self.zones[zone.id] = zone

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)

    def add_route(self, zone1_id: str, zone2_id: str, distance: float):
        self.graph[zone1_id][zone2_id] = distance
        self.graph[zone2_id][zone1_id] = distance

    def update_weather(self, zone_id: str, condition: WeatherCondition):
        self.weather_conditions[zone_id] = condition

    def calculate_travel_time(self, vehicle: Vehicle, from_zone: str, to_zone: str) -> float:
        if from_zone not in self.graph or to_zone not in self.graph[from_zone]:
            return float('inf')

        base_distance = self.graph[from_zone][to_zone]
        weather_modifier = self._get_weather_modifier(to_zone)
        return base_distance / (vehicle.speed * weather_modifier)

    def _get_weather_modifier(self, zone_id: str) -> float:
        weather = self.weather_conditions.get(zone_id, WeatherCondition.CLEAR)
        modifiers = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.STORM: 0.4,
            WeatherCondition.HEAVY_RAIN: 0.6,
            WeatherCondition.FLOOD: 0.3
        }
        return modifiers[weather]

    def a_star_search(self, start_zone: str, goal_zone: str, vehicle: Vehicle) -> List[str]:
        def heuristic(zone1_id: str, zone2_id: str) -> float:
            z1 = self.zones[zone1_id]
            z2 = self.zones[zone2_id]
            # Simple Euclidean distance heuristic
            return ((z1.position[0] - z2.position[0]) ** 2 +
                    (z1.position[1] - z2.position[1]) ** 2) ** 0.5

        frontier = [(0, start_zone)]
        came_from = {start_zone: None}
        cost_so_far = {start_zone: 0}

        while frontier:
            current_cost, current = heapq.heappop(frontier)

            if current == goal_zone:
                break

            for next_zone in self.graph[current]:
                travel_time = self.calculate_travel_time(vehicle, current, next_zone)
                new_cost = cost_so_far[current] + travel_time

                if (next_zone not in cost_so_far or new_cost < cost_so_far[next_zone]):
                    cost_so_far[next_zone] = new_cost
                    priority = new_cost + heuristic(next_zone, goal_zone)
                    heapq.heappush(frontier, (priority, next_zone))
                    came_from[next_zone] = current

        # Reconstruct path
        path = []
        current = goal_zone
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        path.reverse()
        return path

    def optimize_distribution(self) -> List[Tuple[Vehicle, List[str]]]:
        routes = []
        unserviced_zones = set(zone.id for zone in self.zones.values()
                               if zone.current_supplies < zone.needs)

        for vehicle in self.vehicles:
            if not unserviced_zones:
                break

            current_route = []
            current_zone = min(unserviced_zones,
                               key=lambda z: self.zones[z].priority)

            while (vehicle.current_capacity > 0 and
                   vehicle.current_fuel > 0 and
                   unserviced_zones):

                next_zone = self._find_best_next_zone(vehicle, current_zone, unserviced_zones)
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

        return routes

    def _find_best_next_zone(self, vehicle: Vehicle, current_zone: str,
                             unserviced_zones: Set[str]) -> str:
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


# Example usage
def create_sample_scenario():
    system = DistributionSystem()

    # Add zones
    zones = [
        Zone("Z1", (0, 0), 1000, 8, "urban", 500, (0, 24)),
        Zone("Z2", (10, 10), 800, 6, "forest", 300, (0, 12)),
        Zone("Z3", (20, 20), 1500, 9, "mountain", 800, (0, 8)),
        Zone("Z4", (30, 30), 500, 4, "road", 200, (0, 48))
    ]
    for zone in zones:
        system.add_zone(zone)

    # Add routes
    system.add_route("Z1", "Z2", 14.14)  # √200
    system.add_route("Z2", "Z3", 14.14)
    system.add_route("Z3", "Z4", 14.14)
    system.add_route("Z1", "Z4", 42.42)

    # Add vehicles
    vehicles = [
        Vehicle(VehicleType.HELICOPTER, 1000, 1000, 500, 500, 200),
        Vehicle(VehicleType.TRUCK, 2000, 2000, 800, 800, 80),
        Vehicle(VehicleType.DRONE, 50, 50, 200, 200, 100)
    ]
    for vehicle in vehicles:
        system.add_vehicle(vehicle)

    # Set weather conditions
    system.update_weather("Z2", WeatherCondition.HEAVY_RAIN)
    system.update_weather("Z3", WeatherCondition.STORM)

    return system


def main():
    system = create_sample_scenario()
    routes = system.optimize_distribution()

    print("\nOptimized Distribution Routes:")
    for vehicle, route in routes:
        print(f"\nVehicle Type: {vehicle.type.value}")
        print(f"Route: {' -> '.join(route)}")


if __name__ == "__main__":
    main()