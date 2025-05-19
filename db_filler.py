from database.crud import create_compound, get_compound_by_casid, create_point
from database.models import Point
from parsers.nistlib import get_critical_values_for_ID, get_isothermal_data_for_ID, get_isobaric_data_for_id
import warnings


def add_by_id(casid: int):
    check = get_compound_by_casid(casid)
    if check:
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


def add_isobaric_points(
        casid: int, p: float, tlow: float, thigh: float, tstep: float
) -> list[Point]:
    compound = add_by_id(casid)
    data = get_isobaric_data_for_id(p=p, tlow=tlow, thigh=thigh, tstep=tstep, id=casid)
    result = []
    for i in range(len(data["Pressure"])):
        props = {}
        for j in data.keys():
            if j == "Pressure":
                p_point = data[j][i]
            elif j == "Temperature":
                t_point = data[j][i]
            else:
                props[j] = data[j][i]
        result.append(create_point(t=t_point, p=p_point, properties=props,casid=casid))
    return result


if __name__ == "__main__":
    print(add_isobaric_points(casid=7732185, p=75, tlow=275, thigh=300, tstep=5))
