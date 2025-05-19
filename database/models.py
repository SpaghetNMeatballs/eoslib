from typing import Optional, Any
from sqlalchemy import ForeignKey, Float, Integer
from sqlalchemy.types import JSON
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSON}


class Compound(Base):
    __tablename__ = "compound_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]]
    Tcr: Mapped[float] = mapped_column(Float)
    Pcr: Mapped[float] = mapped_column(Float)
    accentric: Mapped[float] = mapped_column(Float)
    CasID: Mapped[int] = mapped_column(Integer, unique=True)

    def __repr__(self) -> str:
        return (
                f"Compound {self.id}, CAS ID = {self.CasID}, Tcr = {self.Tcr}, Pcr = {self.Pcr}, acentric factor = {self.accentric}"
                + (f", name = {self.name}" if self.name else "")
        )


# TO-DO class phase

class Point(Base):
    __tablename__ = "points_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    T: Mapped[float] = mapped_column(Float)
    P: Mapped[float] = mapped_column(Float)
    properties: Mapped[dict[str, Any]]
    # TO-DO phase: enum
    # TO-DO source: id
    compound_id: Mapped[int] = mapped_column(ForeignKey("compound_table.id"))

    def __repr__(self):
        return f"Point {self.id}, T = {self.T}, P = {self.P}, compound_id = {self.compound_id}, properties = {self.properties}"
