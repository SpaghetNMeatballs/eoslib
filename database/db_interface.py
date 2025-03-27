from sqlalchemy import create_engine
from .models import Base

engine = create_engine("postgresql://postgres:postgres@localhost:5432", echo=True)
Base.metadata.create_all(engine)
