from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Base = declarative_base()


context_model = Table(
    "context",
    metadata,
    # Main fields
    Column("id", Integer, primary_key=True),
    Column("url", String, nullable=False),
    Column("context", String, nullable=False),
    Column("short_context", String, nullable=False),
)


class ContextModel(Base):
    __tablename__ = "context"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    context = Column(String)
    short_context = Column(String)
