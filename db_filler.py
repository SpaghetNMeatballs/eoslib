from database.crud import create_compound, get_compound_by_casid, create_point
from database.models import Point
from parsers.nistlib import get_critical_values_for_ID, get_isothermal_data_for_ID
import warnings


def add_by_id(casid: int):
    check = get_compound_by_casid(casid)
    if check:
        warnings.warn("Compound already exists")
        return check
    data = get_critical_values_for_ID(casid)
    if "Tc" not in data.keys() or "Pc" not in data.keys():
        raise Exception("Not enough critical properties present")
    return create_compound(
        name=data["name"],
        tcr=data["Tc"],
        pcr=data["Pc"],
        acentric=data["omega"],
        casid=casid,
    )


def add_isothermal_points(
    casid: int, t: float, plow: float, phigh: float, pstep: float
) -> list[Point]:
    compound = add_by_id(casid)
    data = get_isothermal_data_for_ID(T=t, PLow=plow, PHigh=phigh, PInc=pstep, ID=casid)
    result = []
    for i in range(len(data["Temperature"])):
        props = {}
        for j in data.keys():
            if j == "Temperature":
                t_point = data[j][i]
            elif j == "Pressure":
                p_point = data[j][i]
            else:
                props[j] = data[j][i]
        result.append(create_point(t=t_point, p=p_point, properties=props, casid=compound.CasID))
    return result


if __name__ == "__main__":
    print(add_isothermal_points(casid=124389, t=300, plow=5, phigh=8, pstep=1))
