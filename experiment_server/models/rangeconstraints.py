""" This is a database-schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey
)

from .meta import Base
from .extension_types.sqltypes import JSONType

class RangeConstraint(Base):
    """
    This is definition of a RangeConstraints class
    RangeConstraint defines what kind of Configurations are allowed to be created in ExperimentGroup.
    """
    __tablename__ = 'rangeconstraints'
    id = Column(Integer, primary_key=True)
    configurationkey_id = Column(Integer, ForeignKey('configurationkeys.id'))
    operator_id = Column(Integer, ForeignKey('operators.id'))
    value = Column(JSONType())

    def as_dict(self):
        """ transfer data to dictionary """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
