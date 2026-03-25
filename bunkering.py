from typing import List, Dict
from dholera_port.config.settings import GreenPortConfig
from dholera_port.services.emissions import EmissionCalculator

class BunkeringSystem:
    FUEL_TYPES = {
        "VLSFO 0.5%": {"name": "VLSFO 0.5% Sulphur", "sulphur_content": "0.5%", "price_per_liter": 65.50, "min_order_liters": 5000},
        "LSMGO": {"name": "Low Sulphur Marine Gas Oil", "sulphur_content": "0.1%", "price_per_liter": 78.25, "min_order_liters": 2000},
        "HFO 3.5%": {"name": "Heavy Fuel Oil 3.5%", "sulphur_content": "3.5%", "price_per_liter": 52.80, "min_order_liters": 10000},
        "MGO": {"name": "Marine Gas Oil", "sulphur_content": "0.1%", "price_per_liter": 82.50, "min_order_liters": 1000},
        "LNG": {"name": "Liquefied Natural Gas", "sulphur_content": "0.0%", "price_per_liter": 45.00, "min_order_liters": 5000}
    }
    SHIP_FUEL_SPECS = {
        "Container Ship": {"primary_fuel": ["VLSFO 0.5%", "LSMGO", "MGO", "LNG"]},
        "Bulk Carrier": {"primary_fuel": ["VLSFO 0.5%", "HFO 3.5%", "LSMGO"]},
        "Oil / LNG Tanker": {"primary_fuel": ["VLSFO 0.5%", "HFO 3.5%", "LNG"]},
        "Cruise Ship": {"primary_fuel": ["LSMGO", "MGO", "LNG"]},
        "Ro-Ro Ship": {"primary_fuel": ["VLSFO 0.5%", "LSMGO", "MGO"]}
    }
    SERVICE_CHARGES = {
        "berth_bunkering": {"base_fee": 15000, "per_liter_fee": 0.50},
        "anchorage_bunkering": {"base_fee": 25000, "per_liter_fee": 0.75},
        "bunker_barge": {"base_fee": 35000, "per_liter_fee": 0.85}
    }
    GST_RATE = 0.18

    @staticmethod
    def get_suitable_fuels(ship_type: str) -> List[str]:
        specs = BunkeringSystem.SHIP_FUEL_SPECS.get(ship_type, {})
        return specs.get("primary_fuel", list(BunkeringSystem.FUEL_TYPES.keys()))

    @staticmethod
    def calculate_bunkering_cost(ship_type: str, fuel_type: str, quantity_liters: float, service_type: str = "berth_bunkering") -> Dict:
        fuel_info = BunkeringSystem.FUEL_TYPES[fuel_type]
        service_info = BunkeringSystem.SERVICE_CHARGES[service_type]
        fuel_cost = quantity_liters * fuel_info["price_per_liter"]
        green_discount = 0
        if fuel_type == "LNG":
            green_discount = fuel_cost * (GreenPortConfig.LNG_DISCOUNT_PERCENT / 100)
        elif fuel_type in ["LSMGO", "MGO"]:
            green_discount = fuel_cost * (GreenPortConfig.LSMGO_DISCOUNT_PERCENT / 100)
        base_service = service_info["base_fee"]
        variable_service = quantity_liters * service_info["per_liter_fee"]
        total_service = base_service + variable_service
        port_authority_fee = fuel_cost * 0.02
        quality_testing = 5000 if quantity_liters > 100000 else 3000
        subtotal = total_service + port_authority_fee + quality_testing
        gst = round(subtotal * BunkeringSystem.GST_RATE)
        emissions = EmissionCalculator.calculate_comprehensive_emissions(fuel_type, quantity_liters)
        grand_total = fuel_cost + subtotal + gst - green_discount
        return {
            "ship_type": ship_type, "fuel_type": fuel_type, "fuel_name": fuel_info["name"],
            "quantity_liters": quantity_liters, "quantity_metric_tons": round(quantity_liters * 0.85 / 1000, 2),
            "service_type": service_type, "fuel_unit_price": fuel_info["price_per_liter"],
            "fuel_cost": round(fuel_cost), "green_discount": round(green_discount),
            "base_service_fee": base_service, "variable_service_fee": round(variable_service),
            "total_service_charges": round(total_service), "port_authority_fee": round(port_authority_fee),
            "quality_testing": quality_testing, "subtotal_services": round(subtotal),
            "gst_on_services": gst, "grand_total": round(grand_total),
            "sulphur_content": fuel_info["sulphur_content"], "emissions": emissions,
            "green_rating": emissions["green_rating"]
        }
