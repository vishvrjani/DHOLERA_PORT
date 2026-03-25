import math
import heapq
from collections import defaultdict
from dholera_port.models.exceptions import ValidationException

class ImportDutyCalculator:
    IMPORT_DUTY_RATES = {
        "Crude Oil": {"bcd": 0.0, "social_welfare": 0.10, "gst": 0.05, "cess": 0.01},
        "Petroleum Products": {"bcd": 0.025, "social_welfare": 0.10, "gst": 0.18, "cess": 0.01},
        "LNG (Liquefied Natural Gas)": {"bcd": 0.025, "social_welfare": 0.10, "gst": 0.05, "cess": 0.0},
        "Electronic Equipment": {"bcd": 0.20, "social_welfare": 0.10, "gst": 0.18, "cess": 0.0},
        "General Cargo": {"bcd": 0.10, "social_welfare": 0.10, "gst": 0.18, "cess": 0.0}
    }

    @staticmethod
    def get_origin_countries(cargo_type):
        return ["China", "USA", "UAE", "Singapore", "Germany"]

    @staticmethod
    def calculate_import_duties(cargo_type, assessable_value, origin_country):
        duty_info = ImportDutyCalculator.IMPORT_DUTY_RATES.get(cargo_type, ImportDutyCalculator.IMPORT_DUTY_RATES["General Cargo"])
        bcd = round(assessable_value * duty_info["bcd"])
        social_welfare_surcharge = round(bcd * duty_info["social_welfare"])
        total_customs_duty = bcd + social_welfare_surcharge
        gst_base = assessable_value + total_customs_duty
        igst = round(gst_base * duty_info["gst"])
        cess = round(assessable_value * duty_info.get("cess", 0))
        total_duties_taxes = total_customs_duty + igst + cess
        total_landed_cost = assessable_value + total_duties_taxes
        return {
            "origin_country": origin_country, "assessable_value": assessable_value,
            "bcd": bcd, "bcd_rate": f"{duty_info['bcd']*100:.2f}%",
            "social_welfare_surcharge": social_welfare_surcharge, "total_customs_duty": total_customs_duty,
            "gst_base": gst_base, "igst": igst, "igst_rate": f"{duty_info['gst']*100:.2f}%",
            "cess": cess, "total_duties_taxes": total_duties_taxes,
            "total_landed_cost": total_landed_cost, "effective_duty_rate": f"{(total_duties_taxes/assessable_value)*100:.2f}%"
        }

class InternationalRoutingSystem:
    DHOLERA_PORT_NAME = "Dholera Smart Port, India"
    # Expanded list of major international ports for realistic routing
    INTERNATIONAL_PORTS = {
        # Dholera Port (Origin for Exports)
        "Dholera Smart Port, India": {"lat": 22.2497, "lon": 72.1783, "country": "India", "region": "South Asia"},
        
        # Middle East
        "Dubai (Jebel Ali), UAE": {"lat": 25.0118, "lon": 55.1177, "country": "UAE", "region": "Middle East"},
        "Abu Dhabi, UAE": {"lat": 24.5247, "lon": 54.4343, "country": "UAE", "region": "Middle East"},
        "Jeddah, Saudi Arabia": {"lat": 21.5433, "lon": 39.1728, "country": "Saudi Arabia", "region": "Middle East"},

        # East Asia
        "Singapore Port, Singapore": {"lat": 1.2644, "lon": 103.8224, "country": "Singapore", "region": "East Asia"},
        "Shanghai, China": {"lat": 31.2304, "lon": 121.4737, "country": "China", "region": "East Asia"},
        "Shenzhen, China": {"lat": 22.5431, "lon": 114.0579, "country": "China", "region": "East Asia"},
        "Ningbo-Zhoushan, China": {"lat": 29.8683, "lon": 121.5440, "country": "China", "region": "East Asia"},
        "Busan, South Korea": {"lat": 35.1796, "lon": 129.0756, "country": "South Korea", "region": "East Asia"},
        "Tokyo (Yokohama), Japan": {"lat": 35.4437, "lon": 139.6380, "country": "Japan", "region": "East Asia"},
        "Osaka, Japan": {"lat": 34.6777, "lon": 135.5015, "country": "Japan", "region": "East Asia"},

        # Europe
        "Rotterdam, Netherlands": {"lat": 51.9225, "lon": 4.4792, "country": "Netherlands", "region": "Europe"},
        "Hamburg, Germany": {"lat": 53.5511, "lon": 9.9937, "country": "Germany", "region": "Europe"},
        "Antwerp, Belgium": {"lat": 51.2194, "lon": 4.4025, "country": "Belgium", "region": "Europe"},
        "London (Felixstowe), UK": {"lat": 51.9606, "lon": 1.3511, "country": "UK", "region": "Europe"},

        # Americas
        "Los Angeles, USA": {"lat": 33.7175, "lon": -118.2692, "country": "USA", "region": "Americas"},
        "New York (New Jersey), USA": {"lat": 40.6895, "lon": -74.0445, "country": "USA", "region": "Americas"},
        "Houston, USA": {"lat": 29.7604, "lon": -95.3698, "country": "USA", "region": "Americas"},
        "Vancouver, Canada": {"lat": 49.2827, "lon": -123.1207, "country": "Canada", "region": "Americas"},
        "Santos, Brazil": {"lat": -23.9608, "lon": -46.3333, "country": "Brazil", "region": "Americas"},

        # Africa
        "Mombasa, Kenya": {"lat": -4.0435, "lon": 39.6682, "country": "Kenya", "region": "Africa"},
        "Durban, South Africa": {"lat": -29.8587, "lon": 31.0218, "country": "South Africa", "region": "Africa"},
        "Lagos, Nigeria": {"lat": 6.5244, "lon": 3.3792, "country": "Nigeria", "region": "Africa"},

        # Oceania
        "Sydney, Australia": {"lat": -33.8688, "lon": 151.2093, "country": "Australia", "region": "Oceania"},
        "Melbourne, Australia": {"lat": -37.8136, "lon": 144.9631, "country": "Australia", "region": "Oceania"},
        "Brisbane, Australia": {"lat": -27.4698, "lon": 153.0251, "country": "Australia", "region": "Oceania"},
    }

    # Region-based multipliers for more realistic sea route calculations
    SEA_ROUTE_MULTIPLIER = {
        "South Asia": 1.20,
        "Middle East": 1.25,
        "East Asia": 1.30,
        "Europe": 1.35,
        "Americas": 1.45,
        "Africa": 1.30,
        "Oceania": 1.40,
        "Unknown": 1.3  # Fallback
    }

    # Graph of major sea lanes for Dijkstra's algorithm
    PORT_GRAPH_CONNECTIONS = {
        # Core Hubs
        "Dholera Smart Port, India": ["Dubai (Jebel Ali), UAE", "Singapore Port, Singapore", "Mombasa, Kenya"],
        "Dubai (Jebel Ali), UAE": ["Rotterdam, Netherlands", "Singapore Port, Singapore", "Jeddah, Saudi Arabia"],
        "Singapore Port, Singapore": ["Shanghai, China", "Rotterdam, Netherlands", "Sydney, Australia"],
        "Shanghai, China": ["Los Angeles, USA", "Tokyo (Yokohama), Japan"],
        "Rotterdam, Netherlands": ["New York (New Jersey), USA", "Santos, Brazil", "Hamburg, Germany", "Antwerp, Belgium", "London (Felixstowe), UK"],
        "Los Angeles, USA": ["Tokyo (Yokohama), Japan", "Sydney, Australia", "New York (New Jersey), USA", "Vancouver, Canada"],
        "New York (New Jersey), USA": ["Rotterdam, Netherlands", "Houston, USA"],
        "Mombasa, Kenya": ["Dubai (Jebel Ali), UAE", "Durban, South Africa"],
        "Santos, Brazil": ["Rotterdam, Netherlands", "Lagos, Nigeria"],
        "Sydney, Australia": ["Singapore Port, Singapore", "Los Angeles, USA", "Melbourne, Australia", "Brisbane, Australia"],
        "Tokyo (Yokohama), Japan": ["Shanghai, China", "Los Angeles, USA", "Osaka, Japan"],
        
        # Regional Connections (Spokes)
        "Abu Dhabi, UAE": ["Dubai (Jebel Ali), UAE"],
        "Jeddah, Saudi Arabia": ["Dubai (Jebel Ali), UAE"],
        "Shenzhen, China": ["Shanghai, China"],
        "Ningbo-Zhoushan, China": ["Shanghai, China"],
        "Busan, South Korea": ["Shanghai, China"],
        "Osaka, Japan": ["Tokyo (Yokohama), Japan"],
        "Hamburg, Germany": ["Rotterdam, Netherlands"],
        "Antwerp, Belgium": ["Rotterdam, Netherlands"],
        "London (Felixstowe), UK": ["Rotterdam, Netherlands"],
        "Houston, USA": ["New York (New Jersey), USA"],
        "Vancouver, Canada": ["Los Angeles, USA"],
        "Durban, South Africa": ["Mombasa, Kenya"],
        "Lagos, Nigeria": ["Santos, Brazil"],
        "Melbourne, Australia": ["Sydney, Australia"],
        "Brisbane, Australia": ["Sydney, Australia"],
    }

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371
        lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
        delta_lat, delta_lon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    @staticmethod
    def find_shortest_path_dijkstra(start_port, end_port):
        """Finds the shortest path between two ports using Dijkstra's algorithm."""
        graph = defaultdict(list)
        for port, connections in InternationalRoutingSystem.PORT_GRAPH_CONNECTIONS.items():
            for connection in connections:
                port1_info = InternationalRoutingSystem.INTERNATIONAL_PORTS[port]
                port2_info = InternationalRoutingSystem.INTERNATIONAL_PORTS[connection]
                distance = InternationalRoutingSystem.haversine_distance(port1_info['lat'], port1_info['lon'], port2_info['lat'], port2_info['lon'])
                graph[port].append((connection, distance))
                graph[connection].append((port, distance))

        distances = {port: float('inf') for port in InternationalRoutingSystem.INTERNATIONAL_PORTS}
        distances[start_port] = 0
        previous_ports = {port: None for port in InternationalRoutingSystem.INTERNATIONAL_PORTS}
        
        pq = [(0, start_port)]

        while pq:
            current_distance, current_port = heapq.heappop(pq)

            if current_distance > distances[current_port]:
                continue

            if current_port not in graph: continue

            for neighbor, weight in graph[current_port]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_ports[neighbor] = current_port
                    heapq.heappush(pq, (distance, neighbor))
        
        path, current = [], end_port
        while current is not None:
            path.insert(0, current)
            current = previous_ports[current]
            
        if path[0] == start_port:
            return path, distances[end_port]
        return None, 0

    @staticmethod
    def calculate_route_cost(origin_port, destination_port, cargo_type, quantity, origin_country, is_export=True):
        import_duties = {} # Define to avoid "local variable referenced before assignment" if is_export=True
        path, raw_distance = InternationalRoutingSystem.find_shortest_path_dijkstra(origin_port, destination_port)
        if path:
            # Get destination region to apply a more realistic sea route factor
            destination_info = InternationalRoutingSystem.INTERNATIONAL_PORTS.get(destination_port, {})
            destination_region = destination_info.get("region", "Unknown")
            multiplier = InternationalRoutingSystem.SEA_ROUTE_MULTIPLIER.get(destination_region, 1.3)
            distance_km = raw_distance * multiplier # Sea route factor based on region
            freight_rates = {"Petroleum Products": 45, "General Cargo": 42, "Electronic Equipment": 75}
            base_rate = freight_rates.get(cargo_type, 50)
            freight_cost = base_rate * distance_km * quantity
            port_handling = freight_cost * (0.15 if is_export else 0.18)
            customs_charges = freight_cost * (0.08 if is_export else 0.05)
            inspection_fee = 5000 if is_export else 7000
            regional_surcharge = freight_cost * 0.08
            insurance = freight_cost * 0.05
            subtotal = freight_cost + port_handling + customs_charges + inspection_fee + regional_surcharge + insurance
            
            if not is_export:
                cif_value = (assessable_value := freight_cost * 1.25)
                import_duties = ImportDutyCalculator.calculate_import_duties(cargo_type, round(cif_value), origin_country)
                grand_total = subtotal + import_duties.get("total_duties_taxes", 0)
            else:
                gst = round(subtotal * 0.18)
                grand_total = subtotal + gst
            return {
                "origin_port": origin_port, "destination_port": destination_port, "origin_country": origin_country,
                "route_path": " -> ".join(path), "distance_km": round(distance_km, 2), "cargo_type": cargo_type,
                "quantity": quantity, "freight_cost": round(freight_cost),
                "port_handling": round(port_handling), "customs_charges": round(customs_charges),
                "inspection_fee": inspection_fee, "regional_surcharge": round(regional_surcharge),
                "insurance": round(insurance), "subtotal": round(subtotal),
                "import_duties": import_duties, "gst": round(subtotal * 0.18) if is_export else 0,
                "grand_total": round(grand_total), "is_export": is_export
            }
        else: # Fallback to direct calculation if Dijkstra fails
            raise ValidationException(f"No viable sea route found from {origin_port} to {destination_port}")
