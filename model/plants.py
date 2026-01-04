
class Plant:
    def __init__(self, name, ideal_temp, ideal_humidity, temp_tolerance, humidity_tolerance):
        self.name = name
        self.ideal_temp = ideal_temp # Celsius
        self.ideal_humidity = ideal_humidity # Percent
        self.temp_tolerance = temp_tolerance # +/- range
        self.humidity_tolerance = humidity_tolerance # +/- range

    def __repr__(self):
        return f"{self.name} (Temp: {self.ideal_temp}±{self.temp_tolerance}C, Hum: {self.ideal_humidity}±{self.humidity_tolerance}%)"

# Plant Definitions based on general botanical requirements
# Hydroponic Lettuce: Cool to moderate, high humidity
lettuce = Plant("Hydroponic Lettuce", ideal_temp=20, ideal_humidity=70, temp_tolerance=5, humidity_tolerance=10)

# Tropical Orchids: Warm, very high humidity
orchids = Plant("Tropical Orchids", ideal_temp=28, ideal_humidity=80, temp_tolerance=4, humidity_tolerance=10)

# Desert Succulents: Hot, low humidity
succulents = Plant("Desert Succulents", ideal_temp=30, ideal_humidity=30, temp_tolerance=10, humidity_tolerance=10)

ALL_PLANTS = [lettuce, orchids, succulents]
