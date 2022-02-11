from ckan.model import meta, types
from sqlalchemy import Column, UnicodeText

from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base(metadata=meta.metadata)


class SearchTerm(Base):
    __tablename__ = 'search_term'

    id = Column(UnicodeText, primary_key=True, default=types.make_uuid)
    term = Column(UnicodeText)
    entity_type = Column(UnicodeText)


def create_tables():
    SearchTerm.__table__.create()


def tables_exist():
    return SearchTerm.__table__.exists()
