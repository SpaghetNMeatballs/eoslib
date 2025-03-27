from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, String, Float, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, insert


class Base(DeclarativeBase):
    pass


class Compound(Base):
    __tablename__ = "compound_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]]
    Tcr: Mapped[float] = mapped_column(Float)
    Pcr: Mapped[float] = mapped_column(Float)
    CasID: Mapped[int] = mapped_column(Integer, unique=True)

    def __repr__(self) -> str:
        return (
            f"Compound {self.id}, CAS ID = {self.CasID}, Tcr = {self.Tcr}, Pcr = {self.Pcr}"
            + (f" name = {self.name}" if self.name else "")
        )


class Point(Base):
    __tablename__ = "points_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    T: Mapped[float] = mapped_column(Float)
    P: Mapped[float] = mapped_column(Float)
    properties: Mapped[JSONB]
    compound_id: Mapped[int] = mapped_column(ForeignKey("compound_table.id"))

    def __repr__(self):
        return f"Point {self.id}, T = {self.T}, P = {self.P}, compound_id = {self.compound_id}, properties = {self.properties}"
