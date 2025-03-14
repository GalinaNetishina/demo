"""create tables

Revision ID: d272cc39da06
Revises: 56d0af3e5f05
Create Date: 2025-03-14 12:55:48.506719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd272cc39da06'
down_revision: Union[str, None] = '56d0af3e5f05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    terminations_types = postgresql.ENUM(
        'power_port',
        'power_outlet',
        'power_feed',
        name='terminations_types', create_type=True)
    cables_link_statuses = postgresql.ENUM(
        name='cables_link_statuses', create_type=False
    )
    cables_types = postgresql.ENUM(
        name='cables_types', create_type=False
    )
    cables_length_units = postgresql.ENUM(
        name='cables_length_units', create_type=False
    )
    power_ports_types = postgresql.ENUM(
        name='power_ports_types', create_type=False
    )
    power_outlets_types = postgresql.ENUM(
        name='power_outlets_types', create_type=False
    )
    power_outlets_feed_legs = postgresql.ENUM(
        name='power_outlets_feed_legs', create_type=False
    )
    op.create_table('cable_paths',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('path', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('is_split', sa.Boolean(), server_default='false', nullable=False),
    sa.Column('is_complete', sa.Boolean(), server_default='false', nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('cable_paths_pkey'))
    )
    op.create_table('cables',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('tenant_id', sa.String(), nullable=False),
    sa.Column('label', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('color', sa.String(), server_default='000000', nullable=False),
    sa.Column('length', sa.Numeric(precision=2, scale=6), nullable=False),
    sa.Column('status', cables_link_statuses, server_default='connected', nullable=False),
    sa.Column('type', cables_types, server_default='power', nullable=False),
    sa.Column('length_unit', cables_length_units, server_default='m', nullable=False),
    sa.Column('_abs_length', sa.Numeric(precision=2, scale=6), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('cables_pkey'))
    )
    op.create_table('device_models',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('device_models_pkey'))
    )
    op.create_table('devices',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('devices_pkey'))
    )
    op.create_table('power_panels',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('site_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('power_panels_pkey')),
    sa.UniqueConstraint('site_id', 'name', name='unique_site_name')
    )
    op.create_table('termination_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', terminations_types, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('termination_type_pkey'))
    )
    op.create_table('power_ports_templates',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('device_model_id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('label', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('max_draw', sa.Integer(), nullable=True),
    sa.Column('allocated_draw', sa.Integer(), nullable=True),
    sa.Column('type', power_ports_types, nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.CheckConstraint('allocated_draw >= 0', name='allocated_draw_positive_check'),
    sa.CheckConstraint('max_draw >= 0', name='max_draw_positive_check'),
    sa.CheckConstraint('max_draw >= allocated_draw', name='allocated_draw_limit_check'),
    sa.ForeignKeyConstraint(['device_model_id'], ['device_models.id'], name=op.f('power_ports_templates_device_model_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('power_ports_templates_pkey'))
    )
    op.create_table('power_outlets_templates',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('device_model_id', sa.BigInteger(), nullable=False),
    sa.Column('power_port_template_id', sa.BigInteger(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('label', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('type', power_outlets_types, nullable=True),
    sa.Column('feed_leg', power_outlets_feed_legs, nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"), nullable=False),
    sa.ForeignKeyConstraint(['device_model_id'], ['device_models.id'], name=op.f('power_outlets_templates_device_model_id_fkey'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['power_port_template_id'], ['power_ports_templates.id'], name=op.f('power_outlets_templates_power_port_template_id_fkey'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('power_outlets_templates_pkey'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('power_outlets_templates')
    op.drop_table('power_ports_templates')
    op.drop_table('termination_type')
    op.drop_table('power_panels')
    op.drop_table('devices')
    op.drop_table('device_models')
    op.drop_table('cables')
    op.drop_table('cable_paths')
    op.execute('DROP TYPE terminations_types')
    # ### end Alembic commands ###
