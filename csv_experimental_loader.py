import csv


class Point:
    def __init__(self, prop_dict):
        keys = prop_dict.keys()
        if "t" in keys:
            self.t = prop_dict["t"]
        if "p" in keys:
            self.t = prop_dict["p"]
        if "z" in keys:
            self.t = prop_dict["z"]
        if "rho" in keys:
            self.t = prop_dict["rho"]


def load_csv(file_name: str, phase):
    result = []
    read_result = []
    try:
        with open(file_name, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                read_result.append(row)
    except FileNotFoundError:
        return None
    except PermissionError:
        return None
    except Exception as e:
        return None
    keys = read_result[0]
    read_result = read_result[1:]
    for i in range(len(read_result)):
        if read_result[i][-1] != phase:
            continue
        point_dict = {keys[j]: read_result[i][j] for j in range(len(keys))}
        point = Point(point_dict)
        result.append([float(j) for j in read_result[i][:-1]])
        result[-1][-1] /= 1000
    return result


if __name__ == "__main__":
    load_csv("methane_experimental.csv")
