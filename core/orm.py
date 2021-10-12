from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, synonym, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()


class BoreholeOrm(Base):
    """The Borehole table

    Attributes
    -----------
    id : str
         The id of the borehole
    length : float
         The length of the borehole
    diameter : float
         The diameter of the borehole

    See Also
    ---------
    IntervalOrm : Relationship one to many with the IntervalOrm table.

    """
    __tablename__ = 'Boreholes'

    id = Column(String(32), primary_key=True)
    date = Column(String(32))
    length = Column(Float(64), default=0.)
    diameter = Column(Float(64), default=0.)
    intervals = relationship('IntervalOrm', collection_class=attribute_mapped_collection('id'),
                             cascade='all, delete-orphan')

    intervals_values = association_proxy('intervals', 'description',
                                         creator=lambda k, v: IntervalOrm(
                                             id=k, description=v['description'],
                                             interval_number=v['interval_number'],
                                             top=v['top'], base=v['base'])
                                         )

    def __repr__(self):
        obj_class = str(self.__class__).strip('"<class>"').strip("' ")
        return f"<{obj_class}>(Name={self.id}, Length={self.length}, " \
               f"Diameter={self.diameter}, Intervals={len(self.intervals)})"


class SampleOrm(Base):
    """The Sample table

    Attributes
    ----------
    id : str
        The name of the sample
    interval_id : str
        The id of the interval that contains the sample
    sample_number : int
        The number the sample in the interval
    description : str
        The name of the main component in the sample
    top_id : int
        The id of the top position of the sample, linked to the position id in the PositionOrm table.
    base_id : int
        The id of the base position of the sample, linked to the position id in the PositionOrm table.

    See Also
    --------
    ComponentOrm : Relationship many to many with the Samples table using the intermediate LinkIntervalComponentOrm table.
    PositionOrm : Relationship many to one with the Intervals table

    """
    __tablename__ = 'Samples'

    id = Column(String(32), primary_key=True)
    type = Column(String(32))
    date = Column(String(32))
    borehole = Column(String(32), ForeignKey('Boreholes.id'))
    interval = Column(Integer, ForeignKey('Intervals.id'))
    sample_number = Column(Integer)
    components = relationship('ComponentOrm', secondary='Linksamplecomponent')
    description = Column(String(32))
    top_id = Column(Integer, ForeignKey('Positions.id'))
    top = relationship('PositionOrm', foreign_keys=[top_id])
    base_id = Column(Integer, ForeignKey('Positions.id'))
    base = relationship('PositionOrm', foreign_keys=[base_id])
    data_id = Column(Integer, ForeignKey('OtherData.id'))
    data = relationship('OtherDataOrm', foreign_keys=[data_id])

    def __repr__(self):
        obj_class = str(self.__class__).strip('"<class>"').strip("' ")
        return f"<{obj_class}>(Id={self.id}, Borehole={self.borehole}, " \
               f"top={self.top}, base={self.base}, Description={self.description}, " \
               f"Components={self.components}, Other data={self.data})"


class IntervalOrm(Base):
    """The Interval table

    Attributes
    ----------
    id : int
        The id of the interval, different for each borehole interval.
    borehole : str
        The name of the borehole from which the interval originated.
    interval_number : integer
        The number the interval in the borehole, starts at 0 for the upper interval of each different borehole.
    description : str
        The name of the main component in the interval.
    top_id : int
        The id of the top position of the interval, link to the position id in the PositionOrm table.
    base_id : int
        The id of the base position of the interval, link to the position id in the PositionOrm table.

    See Also
    --------
    ComponentOrm : Relationship many to many with the Intervals table using the intermediate LinkIntervalComponentOrm table.
    PositionOrm : Relationship many to one with the Intervals table

    """
    __tablename__ = 'Intervals'

    id = Column(Integer, primary_key=True)
    borehole = Column(String(32), ForeignKey('Boreholes.id'))
    interval_number = Column(Integer)
    samples = relationship('SampleOrm', secondary='Linkintervalsample')
    components = relationship('ComponentOrm', secondary='Linkintervalcomponent')
    description = Column(String(32))
    top_id = Column(Integer, ForeignKey('Positions.id'))
    top = relationship('PositionOrm', foreign_keys=[top_id])
    base_id = Column(Integer, ForeignKey('Positions.id'))
    base = relationship('PositionOrm', foreign_keys=[base_id])
    data_id = Column(Integer, ForeignKey('IntervalData.id'))
    data = relationship('IntervalDataOrm', foreign_keys=[data_id])

    def __repr__(self):
        obj_class = str(self.__class__).strip('"<class>"').strip("' ")
        return f"<{obj_class}>(Id={self.id}, Borehole={self.borehole}, " \
               f"top={self.top}, base={self.base}, Description={self.description}, " \
               f"Samples={self.samples}, Components={self.components})"


class ComponentOrm(Base):
    """The Component table

    Attributes
    ----------
    id : str
        The id of the component.
    description : str
        The name of the component.

    See Also
    --------
    IntervalOrm : Relationship one to many with the IntervalOrm table.

    """
    __tablename__ = 'Components'

    id = Column(Integer, primary_key=True)
    intervals = relationship('IntervalOrm', secondary='Linkintervalcomponent')
    description = Column(String(32))

    def __repr__(self):
        obj_class = str(self.__class__).strip('"<class>"').strip("' ")
        return f"<{obj_class}>(Id={self.id}, Description={self.description})"


# not yet ready
class LinkIntervalSampleOrm(Base):
    """The junction table between sample and interval

    Attributes
    ----------
    id : int
        The id of the interval, different for each borehole interval.
    description : str
         The name of the sample.

    """
    __tablename__ = 'Linkintervalsample'

    intv_id = Column(Integer, ForeignKey('Intervals.id'), primary_key=True)
    samp_id = Column(Integer, ForeignKey('Samples.id'), primary_key=True)
    # extra_data = Column(String(256))
    sample = relationship('SampleOrm', backref=backref("sample_assoc"))
    interval = relationship('IntervalOrm', backref=backref("interval_assoc_1"))


class LinkIntervalComponentOrm(Base):
    """The junction table between component and interval

    Attributes
    ----------
    id : int
        The id of the interval, different for each borehole interval.
    description : str
         The name of the component.

    """
    __tablename__ = 'Linkintervalcomponent'

    intv_id = Column(Integer, ForeignKey('Intervals.id'), primary_key=True)
    comp_id = Column(Integer, ForeignKey('Components.id'), primary_key=True)
    extra_data = Column(String(256))
    component = relationship('ComponentOrm', backref=backref("component_assoc"))
    interval = relationship('IntervalOrm', backref=backref("interval_assoc_2"))


# not yet ready
class LinkSampleComponentOrm(Base):
    """The junction table between component and sample

    Attributes
    ----------

    """
    __tablename__ = 'Linksamplecomponent'

    samp_id = Column(Integer, ForeignKey('Samples.id'), primary_key=True)
    comp_id = Column(Integer, ForeignKey('Components.id'), primary_key=True)
    extra_data = Column(String(256))
    component = relationship('ComponentOrm', backref=backref("component_assoc_2"))
    interval = relationship('SampleOrm', backref=backref("sample_assoc_2"))


class PositionOrm(Base):
    """The Position table

    Attributes
    ----------
    id : int
        The id of the interval, different for each borehole interval.
    upper : float
           The upper value of the position.
    middle : float
            The middle value of the position.
    lower : float
           The lower value of the position.
    x : float
        The X coordinate.
    y : float
        The Y coordinate.
    z : float
        The Y coordinate, synonym of the middle attribute.

    """
    __tablename__ = 'Positions'

    id = Column(Integer, primary_key=True)
    upper = Column(Float(32))
    middle = Column(Float(32))
    lower = Column(Float(32))
    x = Column(Float(64), default=0.)
    y = Column(Float(64), default=0.)
    z = synonym('middle')


class OtherDataOrm(Base):
    """The additional Data table

    Attributes
    """
    __tablename__ = 'OtherData'

    id = Column(Integer, primary_key=True)
    key = Column(String(32))
    value = Column(Float(64))
    units = Column(String(32))

    def __repr__(self):
        obj_class = str(self.__class__).strip('"<class>"').strip("' ")
        return f"<{obj_class}>(Id={self.id})"


class IntervalDataOrm(Base):
    """The IntervalData table

    Attributes
    """
    __tablename__ = 'IntervalData'

    id = Column(Integer, primary_key=True)
    interval = Column(Integer, ForeignKey('Intervals.id'))
    key = Column(String(32))
    value = Column(Float(64))
    units = Column(String(32))

    def __repr__(self):
        obj_class = str(self.__class__).strip('"<class>"').strip("' ")
        return f"<{obj_class}>(Id={self.id})"
