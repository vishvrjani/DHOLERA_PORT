from dholera_port.config.settings import GreenPortConfig

class CarbonOffsetSystem:
    OFFSET_PROJECTS = {
        "Solar Farm - Gujarat": {"price_per_ton": 2200, "location": "Gujarat, India", "type": "Renewable Energy", "certification": "Gold Standard", "co2_reduction_per_year": 50000},
        "Mangrove Reforestation": {"price_per_ton": 2800, "location": "Gujarat Coast", "type": "Nature-Based", "certification": "Verra VCS", "co2_reduction_per_year": 30000},
        "Wind Energy - Kutch": {"price_per_ton": 2400, "location": "Kutch, Gujarat", "type": "Renewable Energy", "certification": "CDM", "co2_reduction_per_year": 75000},
        "Energy Efficiency": {"price_per_ton": 2000, "location": "Industrial Gujarat", "type": "Energy Efficiency", "certification": "ISO 14064", "co2_reduction_per_year": 40000}
    }

    @staticmethod
    def calculate_offset_cost(co2_tons, project_name):
        project = CarbonOffsetSystem.OFFSET_PROJECTS.get(project_name, {"price_per_ton": GreenPortConfig.CARBON_OFFSET_PRICE_PER_TON})
        cost = co2_tons * project["price_per_ton"]
        return {
            "co2_tons": co2_tons,
            "project": project_name,
            "price_per_ton": project["price_per_ton"],
            "total_cost": round(cost),
            "certification": project.get("certification", "Standard"),
            "location": project.get("location", "Gujarat, India")
        }
