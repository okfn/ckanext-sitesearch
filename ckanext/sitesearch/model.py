import datetime

from ckan.model import meta
from ckan.model.types import UuidType
from sqlalchemy import Column, UnicodeText, DateTime

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base(metadata=meta.metadata)


class SearchTerm(Base):
    __tablename__ = 'search_term'

    id = Column(UuidType, primary_key=True, default=UuidType.default)
    term = Column(UnicodeText)
    entity_type = Column(UnicodeText)
    user_id = Column(UuidType)
    search_time = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<{self.entity_type} search: {self.term}>"


def create_tables():
    SearchTerm.__table__.create()


def tables_exist():
    return SearchTerm.__table__.exists()
