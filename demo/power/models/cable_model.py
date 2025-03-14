from decimal import Decimal
from typing import Any

from sqlalchemy import BigInteger, Boolean, Enum, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.declarative import declared_attr
from .base import Model
from .power_enums import (
    CableEndEnum,
    CableLengthUnitEnum,
    CableTypeEnum,
    LinkStatusEnum,
    TerminationTypeEnum
)


class CableModel(Model):
    __tablename__ = "cables"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tenant_id: Mapped[str] = mapped_column()

    label: Mapped[str | None]
    description: Mapped[str | None]
    color: Mapped[str] = mapped_column(default="000000", server_default="000000")
    length: Mapped[Decimal] = mapped_column(Numeric(2, 6))

    status: Mapped[LinkStatusEnum] = mapped_column(
        Enum(
            LinkStatusEnum,
            name="cables_link_statuses",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        default=LinkStatusEnum.STATUS_CONNECTED,
        server_default="connected",
    )
    type: Mapped[CableTypeEnum] = mapped_column(
        Enum(
            CableTypeEnum,
            name="cables_types",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        default=CableTypeEnum.TYPE_POWER,
        server_default="power",
    )
    length_unit: Mapped[CableLengthUnitEnum] = mapped_column(
        Enum(
            CableLengthUnitEnum,
            name="cables_length_units",
            values_callable=lambda obj: [item.value for item in obj],
        ),
        default=CableLengthUnitEnum.UNIT_METER,
        server_default="m",
    )
    _abs_length: Mapped[Decimal] = mapped_column(Numeric(2, 6))
    
    terminations = relationship(
        "CableTermination",
        back_populates="cable",
        cascade="all, delete-orphan"
    )


class CablePath(Model):
    """
    A CablePath instance represents the physical path from a set of origin nodes to a set of destination nodes,
    including all intermediate elements.

    `path` contains the ordered set of nodes, arranged in lists of (type, ID) tuples. (Each cable in the path can
    terminate to one or more objects.)  For example, consider the following
    topology:

                     A                              B                              C
        Interface 1 --- Front Port 1 | Rear Port 1 --- Rear Port 2 | Front Port 3 --- Interface 2
                        Front Port 2                                 Front Port 4

    This path would be expressed as:

    CablePath(
        path = [
?  ?      [Powerpanel/PowerFeed],
            [Cable A],
            [Optional PowerPort PDU],
            [Optional PowerOulet PDU],
            [Cable B],
            [PowerPort on device],
        ]
    )

    `is_active` is set to True only if every Cable within the path has a status of "connected". `is_complete` is True
    if the instance represents a complete end-to-end path from origin(s) to destination(s). `is_split` is True if the
    path diverges across multiple cables.

    `_nodes` retains a flattened list of all nodes within the path to enable simple filtering.
    """
    __tablename__ = "cable_paths"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    path: Mapped[list[Any] | None] = mapped_column(JSONB, default=list())
    is_active: Mapped[bool] = mapped_column(
        default=False, server_default="false"
    )
    is_split: Mapped[bool] = mapped_column(
        default=False, server_default="false"
    )
    is_complete: Mapped[bool] = mapped_column(
        default=False, server_default="false"
    )

    # TODO list of endpoint in path
    # _nodes:Mapped[list] self._nodes = list(itertools.chain(*self.path))

    @property
    def path_objects(self):
        """
        Cache and return the complete path as lists of objects, derived from their annotation within the path.
        """
        if not hasattr(self, '_path_objects'):
            self._path_objects = self._get_path()
        return self._path_objects

    @property
    def origins(self):
        """
        Return the list of originating objects.
        """
        return self.path_objects[0]

    @property
    def destinations(self):
        """
        Return the list of destination objects, if the path is complete.
        """
        if not self.is_complete:
            return []
        return self.path_objects[-1]

    @property
    def segment_count(self):
        return int(len(self.path) / 3)


class CabledPathEndpoint():
    """
    An abstract model inherited by any CabledObjectModel subclass which represents the end of a CablePath; specifically,
    these include ConsolePort, ConsoleServerPort, PowerPort, PowerOutlet, Interface, and PowerFeed.

    `_path` references the CablePath originating from this instance, if any. It is set or cleared by the receivers in
    dcim.signals in response to changes in the cable path, and complements the `origin` GenericForeignKey field on the
    CablePath model. `_path` should not be accessed directly; rather, use the `path` property.

    `connected_endpoints()` is a convenience method for returning the destination of the associated CablePath, if any.
    """
    __abstract__ = True
    
    @declared_attr
    def _path_id(cls):
        return mapped_column(ForeignKey(
            'cable_paths.id', ondelete="SET NULL"
            ), nullable=True)

    def trace(self):
        origin = self
        path = []

        # Construct the complete path (including e.g. bridged interfaces)
        while origin is not None:

            if origin._path is None:
                break

            path.extend(origin._path.path_objects)

            # If the path ends at a non-connected pass-through port, pad out the link and far-end terminations
            if len(path) % 3 == 1:
                path.extend(([], []))
            # If the path ends at a site or provider network, inject a null "link" to render an attachment
            elif len(path) % 3 == 2:
                path.insert(-1, [])

            # Check for a bridged relationship to continue the trace
            destinations = origin._path.destinations
            if len(destinations) == 1:
                origin = getattr(destinations[0], 'bridge', None)
            else:
                origin = None

        # Return the path as a list of three-tuples (A termination(s), cable(s), B termination(s))
        return list(zip(*[iter(path)] * 3))

    @property
    def path(self):
        return self._path

    # @cached_property
    def connected_endpoints(self):
        """
        Caching accessor for the attached CablePath's destination (if any)
        """
        return self._path.destinations if self._path else []
    
    
class TerminationType(Model):
    __tablename__ = "termination_type"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[TerminationTypeEnum] = mapped_column(
        Enum(
            TerminationTypeEnum,
            name="terminations_types",
            values_callable=lambda obj: [item.value for item in obj],
        )
    )


class CabledObjectMixin:
    __abstract__ = True
    
    @declared_attr
    def cable(cls):
        return mapped_column(ForeignKey("cables.id", ondelete="SET NULL"))
    
    @declared_attr
    def cable_end(cls): 
        return mapped_column(Enum(
            CableEndEnum,
            name="cables_ends",
            values_callable=lambda obj: [item.value for item in obj],
        ), nullable=True)
        
    @declared_attr
    def mark_connected(cls):
        return mapped_column(Boolean, default=False, server_default='false')
    
    # @declared_attr
    # def cable_terminations(cls):
    #     return relationship(
    #         "CableTermination",
    #         primaryjoin="and_(PowerPortModel.id == CableTermination.termination_id, CableTermination.termination_type_id == TerminationType.id)",
    #         # remote_side=[CableTermination.termination_type_id],
    #         backref="power_port",            
    #         viewonly=True
    #     )


class CableTermination(Model):
    __tablename__ = "cable_termination"
    __table_args__ = (
        UniqueConstraint(
            'termination_id',
            'termination_type_id',
            name='cable_unique_termination'
        ),
    )
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cable_id: Mapped[int] = mapped_column(
        ForeignKey("cables.id", ondelete="CASCADE")
    )
    cable_end: Mapped[CableEndEnum] = mapped_column(Enum(
            CableEndEnum,
            name="cables_ends",
            values_callable=lambda obj: [item.value for item in obj],
            ),
        nullable=True
        )
    termination_id: Mapped[int] = mapped_column(ForeignKey("power_ports.id"))
    termination_type_id: Mapped[int] = mapped_column(ForeignKey('termination_type.id'))
    
    cable: Mapped[CableModel] = relationship()
    termination_type: Mapped[TerminationType] = relationship()
