""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship
from .meta import Base

from .extension_types.sqltypes import JSONType


class ExclusionConstraint(Base):
    """ This is definition of exclusion constraints class """
    __tablename__ = 'exclusionconstraints'
    id = Column(Integer, primary_key=True)
    first_configurationkey_id = Column(Integer, ForeignKey('configurationkeys.id'))
    first_operator_id = Column(Integer, ForeignKey('operators.id'))
    first_value_a = Column(JSONType())
    first_value_b = Column(JSONType())

    second_configurationkey_id = Column(Integer, ForeignKey('configurationkeys.id'))
    second_operator_id = Column(Integer, ForeignKey('operators.id'))
    second_value_a = Column(JSONType())
    second_value_b = Column(JSONType())

    first_configurationkey = relationship("ConfigurationKey", foreign_keys=[first_configurationkey_id])
    first_operator = relationship("Operator", foreign_keys=[first_operator_id])
    second_configurationkey = relationship("ConfigurationKey", foreign_keys=[second_configurationkey_id])
    second_operator = relationship("Operator", foreign_keys=[second_operator_id])

    def as_dict(self):
        """ transfer data to dictionary """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}  # col.name means data from column
