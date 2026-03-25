from dholera_port.config.settings import GreenPortConfig

class PortBilling:
    PORT_CHARGES = {
        "Container Ship": {"port_dues": 500000, "berth_day": 200000, "pilot": 300000, "tug": 200000},
        "Bulk Carrier": {"port_dues": 400000, "berth_day": 150000, "pilot": 250000, "tug": 150000},
        "Oil / LNG Tanker": {"port_dues": 600000, "berth_day": 300000, "pilot": 400000, "tug": 300000},
        "Cruise Ship": {"port_dues": 700000, "berth_day": 350000, "pilot": 500000, "tug": 300000},
        "Ro-Ro Ship": {"port_dues": 350000, "berth_day": 120000, "pilot": 200000, "tug": 120000}
    }
    CARGO_HANDLING_RATES = {
        "Petroleum Products": 285, "Gems & Jewellery": 500, "Pharmaceuticals": 350,
        "Machinery": 55, "Chemicals": 280, "Textiles": 180, "Agricultural Products": 200,
        "Crude Oil": 275, "Gold & Precious Metals": 550, "Diamonds (Uncut)": 600,
        "Electronic Equipment": 320, "Mobile Phones": 350, "Computer Hardware": 340,
        "Machinery & Equipment": 220, "Industrial Machinery": 240,
        "Coal": 150, "LNG (Liquefied Natural Gas)": 290,
        "Chemicals & Fertilizers": 240, "Pharmaceuticals (APIs)": 380,
        "Medical Equipment": 340, "Plastics & Polymers": 210,
        "Vegetable Oils": 190, "Pulses & Lentils": 170, "Fresh Fruits": 250,
        "Steel & Iron": 180, "Copper & Aluminum": 200,
        "Textiles & Fabrics": 180, "Cotton (Raw)": 160,
        "Automobiles": 500, "Auto Parts": 280,
        "Containers (Mixed Cargo)": 4000, "Bulk Cargo": 165, "General Cargo": 165,
    }
    GST_RATE = 0.18

    @staticmethod
    def calculate_total_bill(ship_type, days, green_certification="None"):
        charges = PortBilling.PORT_CHARGES[ship_type]
        port_dues = charges["port_dues"]
        berth_hire = charges["berth_day"] * days
        pilotage = charges["pilot"]
        tug_charges = charges["tug"]
        subtotal = port_dues + berth_hire + pilotage + tug_charges
        green_discount_rate = GreenPortConfig.get_green_certification_discount(green_certification)
        green_discount = round(subtotal * green_discount_rate)
        subtotal_after_discount = subtotal - green_discount
        gst = round(subtotal_after_discount * PortBilling.GST_RATE)
        grand_total = subtotal_after_discount + gst
        return {
            "port_dues": port_dues, "berth_hire": berth_hire, "pilotage": pilotage,
            "tug_charges": tug_charges, "subtotal": subtotal, "green_certification": green_certification,
            "green_discount": green_discount, "green_discount_rate": f"{green_discount_rate*100:.0f}%",
            "subtotal_after_discount": subtotal_after_discount, "gst": gst, "grand_total": grand_total, "days": days
        }

    @staticmethod
    def calculate_cargo_handling(cargo_type, quantity):
        rate = PortBilling.CARGO_HANDLING_RATES.get(cargo_type, 200)
        handling = rate * quantity
        gst = round(handling * PortBilling.GST_RATE)
        total = handling + gst
        unit = "container(s)" if cargo_type == "Containers (Mixed Cargo)" else "ton(s)"
        return {"handling": handling, "gst": gst, "total": total, "rate": rate, "quantity": quantity, "unit": unit, "cargo_type": cargo_type}
