from .db_interface import session
from sqlalchemy.sql.expression import select, delete
from .models import Compound, Point


def create_compound(name: str, tcr: float, pcr: float, casid: int):
    new_compound = Compound(name=name, Tcr=tcr, Pcr=pcr, CasID=casid)
    session.add(new_compound)
    session.commit()
    return new_compound


def create_point(t: float, p: float, properties: dict, casid: int):
    compound = get_compound_by_casid(casid)
    new_point = Point(T=t, P=p, properties=properties, compound_id=compound.id)
    session.add(new_point)
    session.commit()
    return new_point


def get_compound_by_casid(casid: int):
    result = session.execute(select(Compound).where(Compound.CasID == casid)).all()
    if result:
        return result[0][0]
    return None


def get_point_by_params(casid: int, t: float, p: float):
    compound = get_compound_by_casid(casid)
    if not compound:
        return None
    point = session.execute(
        select(Point).where(
            Point.T == t and Point.P == p and Point.compound_id == compound.id
        )
    ).all()
    if point:
        return point[0]
    return None


def get_all_points_by_compound(casid):
    compound = get_compound_by_casid(casid)
    if not compound:
        return None
    points = session.execute(select(Point).where(Point.compound_id == compound.id))
    if points:
        return points
    return None


def update_compound_by_casid(casid: int):
    pass


def update_point_by_params(casid: int, t: float, p: float):
    pass


def remove_point_by_params(casid: int, t: float, p: float):
    if get_point_by_params(casid, t, p) is None:
        return False
    compound = get_compound_by_casid(casid)
    session.execute(
        delete(Point).where(
            Point.T == t and Point.P == p and Point.compound_id == compound.id
        )
    )
    session.commit()
    return True


def remove_points_by_casid(casid: int):
    compound = get_compound_by_casid(casid)
    session.execute(delete(Point).where(Point.compound_id == compound.id))
    session.commit()
    return True


def remove_compound_by_casid(casid: int):
    if get_compound_by_casid(casid) is None:
        return False
    session.execute(delete(Compound).where(Compound.CasID == casid))
    session.commit()
    return True


if __name__ == "__main__":
    #create_point(140, 1, {"Cv": 33.438}, 630080)
    remove_points_by_casid(630080)
