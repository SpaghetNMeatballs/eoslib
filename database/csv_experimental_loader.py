import csv
import datetime
from utils.point_dataclass import Point


def load_csv(file_name: str, phase="liquid"):
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
    keys = [i.split('(')[0].lower() for i in read_result[0]]
    read_result = read_result[1:]
    for i in range(len(read_result)):
        if read_result[i][-1] != phase:
            continue
        point_dict = {keys[j]: read_result[i][j] for j in range(len(keys))}
        point = Point(point_dict)
        result.append([float(j) for j in read_result[i][:-1]])
        result[-1][-1] /= 1000
    return result


def write_csv(inp: dict, name="unnamed-data"):
    width = len(list(inp.keys()))
    height = len(list(inp.values())[0])
    inp_values = list(inp.values())
    for i in range(1, len(inp_values)):
        assert len(inp_values[i]) == height, "Missing point found"
    with open(
        f"{name}-{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.csv",
        "w",
        newline="",
    ) as csvfile:
        spamwriter = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        spamwriter.writerow(list(inp.keys()))
        for i in range(height):
            spamwriter.writerow([inp_values[j][i] for j in range(width)])


if __name__ == "__main__":
    load_csv("C7732185-21-03-2025-13-46-40.csv")
