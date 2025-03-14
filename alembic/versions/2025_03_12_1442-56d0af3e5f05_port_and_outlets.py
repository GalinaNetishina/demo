"""create power enums

Revision ID: 56d0af3e5f05
Revises: 
Create Date: 2025-03-12 14:42:37.521884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '56d0af3e5f05'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    power_outlets_types = postgresql.ENUM(
                "iec-60320-c5",
                "iec-60320-c7",
                "iec-60320-c13",
                "iec-60320-c15",
                "iec-60320-c19",
                "iec-60320-c21",
                "iec-60309-p-n-e-4h",
                "iec-60309-p-n-e-6h",
                "iec-60309-p-n-e-9h",
                "iec-60309-2p-e-4h",
                "iec-60309-2p-e-6h",
                "iec-60309-2p-e-9h",
                "iec-60309-3p-e-4h",
                "iec-60309-3p-e-6h",
                "iec-60309-3p-e-9h",
                "iec-60309-3p-n-e-4h",
                "iec-60309-3p-n-e-6h",
                "iec-60309-3p-n-e-9h",
                "iec-60906-1",
                "nbr-14136-10a",
                "nbr-14136-20a",
                "nema-1-15r",
                "nema-5-15r",
                "nema-5-20r",
                "nema-5-30r",
                "nema-5-50r",
                "nema-6-15r",
                "nema-6-20r",
                "nema-6-30r",
                "nema-6-50r",
                "nema-10-30r",
                "nema-10-50r",
                "nema-14-20r",
                "nema-14-30r",
                "nema-14-50r",
                "nema-14-60r",
                "nema-15-15r",
                "nema-15-20r",
                "nema-15-30r",
                "nema-15-50r",
                "nema-15-60r",
                "nema-l1-15r",
                "nema-l5-15r",
                "nema-l5-20r",
                "nema-l5-30r",
                "nema-l5-50r",
                "nema-l6-15r",
                "nema-l6-20r",
                "nema-l6-30r",
                "nema-l6-50r",
                "nema-l10-30r",
                "nema-l14-20r",
                "nema-l14-30r",
                "nema-l14-50r",
                "nema-l14-60r",
                "nema-l15-20r",
                "nema-l15-30r",
                "nema-l15-50r",
                "nema-l15-60r",
                "nema-l21-20r",
                "nema-l21-30r",
                "nema-l22-20r",
                "nema-l22-30r",
                "CS6360C",
                "CS6364C",
                "CS8164C",
                "CS8264C",
                "CS8364C",
                "CS8464C",
                "ita-e",
                "ita-f",
                "ita-g",
                "ita-h",
                "ita-i",
                "ita-j",
                "ita-k",
                "ita-l",
                "ita-m",
                "ita-n",
                "ita-o",
                "ita-multistandard",
                "usb-a",
                "usb-micro-b",
                "usb-c",
                "molex-micro-fit-1x2",
                "molex-micro-fit-2x2",
                "molex-micro-fit-2x4",
                "dc-terminal",
                "eaton-c39",
                "hdot-cx",
                "saf-d-grid",
                "neutrik-powercon-20a",
                "neutrik-powercon-32a",
                "neutrik-powercon-true1",
                "neutrik-powercon-true1-top",
                "ubiquiti-smartpower",
                "hardwired",
                "other",
                name="power_outlets_types",
            )
    cables_link_statuses = postgresql.ENUM(
                "connected",
                "planned",
                "decommissioning",
                name="cables_link_statuses"
            )
    cables_ends = postgresql.ENUM(
        "A",
        "B",
        name="cables_ends"
    )
    cables_types = postgresql.ENUM(
                "cat3",
                "cat5",
                "cat5e",
                "cat6",
                "cat6a",
                "cat7",
                "cat7a",
                "cat8",
                "dac-active",
                "dac-passive",
                "mrj21-trunk",
                "coaxial",
                "mmf",
                "mmf-om1",
                "mmf-om2",
                "mmf-om3",
                "mmf-om4",
                "mmf-om5",
                "smf",
                "smf-os1",
                "smf-os2",
                "aoc",
                "power",
                "usb",
                name="cables_types",
            )
    cables_length_units = postgresql.ENUM(
        "km",
        "m",
        "cm",
        "mi",
        "ft",
        "in",
        name="cables_length_units"
        )
    power_ports_types = postgresql.ENUM(
                "iec-60320-c6",
                "iec-60320-c8",
                "iec-60320-c14",
                "iec-60320-c16",
                "iec-60320-c20",
                "iec-60320-c22",
                "iec-60309-p-n-e-4h",
                "iec-60309-p-n-e-6h",
                "iec-60309-p-n-e-9h",
                "iec-60309-2p-e-4h",
                "iec-60309-2p-e-6h",
                "iec-60309-2p-e-9h",
                "iec-60309-3p-e-4h",
                "iec-60309-3p-e-6h",
                "iec-60309-3p-e-9h",
                "iec-60309-3p-n-e-4h",
                "iec-60309-3p-n-e-6h",
                "iec-60309-3p-n-e-9h",
                "iec-60906-1",
                "nbr-14136-10a",
                "nbr-14136-20a",
                "nema-1-15p",
                "nema-5-15p",
                "nema-5-20p",
                "nema-5-30p",
                "nema-5-50p",
                "nema-6-15p",
                "nema-6-20p",
                "nema-6-30p",
                "nema-6-50p",
                "nema-10-30p",
                "nema-10-50p",
                "nema-14-20p",
                "nema-14-30p",
                "nema-14-50p",
                "nema-14-60p",
                "nema-15-15p",
                "nema-15-20p",
                "nema-15-30p",
                "nema-15-50p",
                "nema-15-60p",
                "nema-l1-15p",
                "nema-l5-15p",
                "nema-l5-20p",
                "nema-l5-30p",
                "nema-l5-50p",
                "nema-l6-15p",
                "nema-l6-20p",
                "nema-l6-30p",
                "nema-l6-50p",
                "nema-l10-30p",
                "nema-l14-20p",
                "nema-l14-30p",
                "nema-l14-50p",
                "nema-l14-60p",
                "nema-l15-20p",
                "nema-l15-30p",
                "nema-l15-50p",
                "nema-l15-60p",
                "nema-l21-20p",
                "nema-l21-30p",
                "nema-l22-20p",
                "nema-l22-30p",
                "cs6361c",
                "cs6365c",
                "cs8165c",
                "cs8265c",
                "cs8365c",
                "cs8465c",
                "ita-c",
                "ita-e",
                "ita-f",
                "ita-ef",
                "ita-g",
                "ita-h",
                "ita-i",
                "ita-j",
                "ita-k",
                "ita-l",
                "ita-m",
                "ita-n",
                "ita-o",
                "usb-a",
                "usb-b",
                "usb-c",
                "usb-mini-a",
                "usb-mini-b",
                "usb-micro-a",
                "usb-micro-b",
                "usb-micro-ab",
                "usb-3-b",
                "usb-3-micro-b",
                "molex-micro-fit-1x2",
                "molex-micro-fit-2x2",
                "molex-micro-fit-2x4",
                "dc-terminal",
                "saf-d-grid",
                "neutrik-powercon-20",
                "neutrik-powercon-32",
                "neutrik-powercon-true1",
                "neutrik-powercon-true1-top",
                "ubiquiti-smartpower",
                "hardwired",
                "other",
                name="power_ports_types",
            )
    power_outlets_feed_legs = postgresql.ENUM(
        "A",
        "B",
        "C",
        name="power_outlets_feed_legs"
        )
    power_feed_types = postgresql.ENUM(
        "primary",
        "redundant",
        name='power_feed_types'
    )
    power_feed_supplies = postgresql.ENUM(
        "ac",
        "dc",
        name='power_feed_supplies'
    )
    power_feed_phases = postgresql.ENUM(
        "single-phase",
        "three-phase",
        name='power_feed_phases'
    )
    power_feed_statuses = postgresql.ENUM(
        "offline",
        "active",
        "planned",
        "failed",
        name='power_feed_statuses'
    )

    power_outlets_types.create(op.get_bind(), checkfirst=True)
    power_outlets_feed_legs.create(op.get_bind(), checkfirst=True)
    power_ports_types.create(op.get_bind(), checkfirst=True)

    cables_link_statuses.create(op.get_bind(), checkfirst=True)
    cables_ends.create(op.get_bind(), checkfirst=True)
    cables_types.create(op.get_bind(), checkfirst=True)
    cables_length_units.create(op.get_bind(), checkfirst=True)

    power_feed_types.create(op.get_bind(), checkfirst=True)
    power_feed_supplies.create(op.get_bind(), checkfirst=True)
    power_feed_phases.create(op.get_bind(), checkfirst=True)
    power_feed_statuses.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    op.execute("DROP TYPE power_outlets_feed_legs")
    op.execute("DROP TYPE power_outlets_types")
    op.execute("DROP TYPE power_ports_types")
    op.execute("DROP TYPE cables_types")
    op.execute("DROP TYPE cables_link_statuses")
    op.execute("DROP TYPE cables_length_units")
    op.execute("DROP TYPE cables_ends")
    op.execute("DROP TYPE power_feed_types")
    op.execute("DROP TYPE power_feed_supplies")
    op.execute("DROP TYPE power_feed_phases")
    op.execute("DROP TYPE power_feed_statuses")
