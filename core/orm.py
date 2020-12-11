from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()


class BoreholeOrm(Base):
    """The Boreholes Info table"""
    __tablename__ = 'Boreholes'
    id = Column(String(32), primary_key=True)
    intervals = relationship(
        'IntervalOrm',
        collection_class=attribute_mapped_collection('id'),
        cascade='all, delete-orphan')
    intervals_values = association_proxy(
        'intervals', 'value',
        creator=lambda k, v: IntervalOrm(id=k, description=v['description'], interval_number=v['interval_number']))


class IntervalOrm(Base):
    """The Interval table"""
    __tablename__ = 'Intervals'
    id = Column(Integer, primary_key=True)
    borehole = Column(String(32), ForeignKey('Boreholes.id', ondelete="CASCADE", onupdate="CASCADE"))
    # Note that this could be a numeric ID as well
    interval_number = Column(Integer)
    components = relationship('ComponentOrm', secondary='Linkintervalcomponent')
    description = Column(String(32))


class ComponentOrm(Base):
    """The Component table"""
    __tablename__ = 'Components'
    id = Column(String(32), primary_key=True)
    intervals = relationship(IntervalOrm, secondary='Linkintervalcomponent')
    description = Column(String(32))


class LinkIntervalComponent(Base):
    __tablename__ = 'Linkintervalcomponent'

    int_id = Column(
        Integer, 
        ForeignKey('Intervals.id'), 
        primary_key=True)

    comp_id = Column(
       Integer, 
       ForeignKey('Components.id'), 
       primary_key=True)
