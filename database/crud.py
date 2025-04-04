from db_interface import session
from sqlalchemy.sql.expression import select
from models import Compound, Point


def create_compound(name: str, tcr: float, pcr: float, casid: int):
    new_compound = Compound(name=name, Tcr=tcr, Pcr=pcr, CasID=casid)
    session.add(new_compound)
    session.commit()


def get_compound_by_casid(casid: int):
    result = session.execute(select(Compound).where(Compound.CasID == casid)).all()
    return result


if __name__ == "__main__":
    print(get_compound_by_casid(7727379))
