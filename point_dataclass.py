class Point:
    def __init__(self, prop_dict):
        keys = list(prop_dict.keys())
        if "temperature" in keys:
            self.t = prop_dict["temperature"]
        if "pressure" in keys:
            self.t = prop_dict["pressure"]
        if "volume" in keys:
            self.v = prop_dict["volume"]
        if "z" in keys:
            self.t = prop_dict["z"]
        if "density" in keys:
            self.t = prop_dict["density"]
