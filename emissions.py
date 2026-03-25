class EmissionCalculator:
    FUEL_EMISSIONS = {
        "HFO 3.5%": 3.114, "VLSFO 0.5%": 3.021, "LSMGO": 2.750,
        "MGO": 2.650, "LNG": 2.100
    }
    SOX_EMISSIONS = {
        "HFO 3.5%": 0.054, "VLSFO 0.5%": 0.015, "LSMGO": 0.003,
        "MGO": 0.003, "LNG": 0.0001
    }
    NOX_EMISSIONS = {
        "HFO 3.5%": 0.087, "VLSFO 0.5%": 0.085, "LSMGO": 0.057,
        "MGO": 0.055, "LNG": 0.012
    }
    PM_EMISSIONS = {
        "HFO 3.5%": 0.008, "VLSFO 0.5%": 0.002, "LSMGO": 0.0008,
        "MGO": 0.0007, "LNG": 0.0001
    }

    @staticmethod
    def calculate_co2(fuel_type, quantity_liters):
        factor = EmissionCalculator.FUEL_EMISSIONS.get(fuel_type, 3.0)
        return round((quantity_liters * factor) / 1000, 2)

    @staticmethod
    def calculate_comprehensive_emissions(fuel_type, quantity_liters):
        return {
            "fuel_type": fuel_type,
            "quantity_liters": quantity_liters,
            "co2_tons": EmissionCalculator.calculate_co2(fuel_type, quantity_liters),
            "sox_kg": round(quantity_liters * EmissionCalculator.SOX_EMISSIONS.get(fuel_type, 0.05), 2),
            "nox_kg": round(quantity_liters * EmissionCalculator.NOX_EMISSIONS.get(fuel_type, 0.08), 2),
            "pm_kg": round(quantity_liters * EmissionCalculator.PM_EMISSIONS.get(fuel_type, 0.005), 2),
            "green_rating": EmissionCalculator.get_green_rating(fuel_type)
        }

    @staticmethod
    def get_green_rating(fuel_type):
        ratings = {
            "LNG": "⭐⭐⭐⭐⭐ Excellent",
            "MGO": "⭐⭐⭐⭐ Very Good",
            "LSMGO": "⭐⭐⭐⭐ Very Good",
            "VLSFO 0.5%": "⭐⭐⭐ Good",
            "HFO 3.5%": "⭐⭐ Fair"
        }
        return ratings.get(fuel_type, "⭐⭐⭐ Good")
