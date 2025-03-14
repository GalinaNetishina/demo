from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Integer, MetaData, String, event, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    declared_attr,
    mapped_column,
    sessionmaker,
)

metadata = MetaData(
    naming_convention={
        "ix": "%(table_name)s_%(column_0_N_name)s_idx",
        "pk": "%(table_name)s_pkey",
        "fk": "%(table_name)s_%(column_0_name)s_fkey",
    }
)


class Model(DeclarativeBase):
    metadata = metadata

    # @classmethod
    # def polymorphic_relation_target_type(cls) -> str:
    #     table_name = cls.__tablename__
    #     schema_name: str | None = None

    #     for table_arg in getattr(cls, "__table_args__", []) or []:
    #         if isinstance(table_arg, dict) and table_arg.get("schema"):
    #             schema_name = table_arg["schema"]
    #             break

    #     if schema_name:
    #         return f"{schema_name}.{table_name}"
    #     else:
    #         return table_name
        
        
class SACreatedAtMixin:
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(),
            nullable=False,
            default=datetime.utcnow,
            server_default=func.timezone("UTC", func.current_timestamp()),
        )


class SAUpdatedAtMixin:
    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(),
            nullable=False,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            server_default=func.timezone("UTC", func.current_timestamp()),
        )


class SADeletedAtMixin:
    @declared_attr
    def deleted_at(cls) -> Mapped[datetime | None]:
        return mapped_column(DateTime())


class SANestedSetMixin:
    
    tree_structure = "NestedSet"

    @declared_attr
    def tree_id(cls):
        return Column(Integer, index=True)

    @declared_attr
    def left(cls):
        return Column(Integer, index=True)

    @declared_attr
    def right(cls):
        return Column(Integer, index=True)

    def update_node(self, session):
        if self.parent_id:
            parent = session.get(self.__class__, self.parent_id)
            
            if parent.tree_id is None or parent.left is None or parent.right is None:
                parent.update_node(session)
                
            self.tree_id = parent.tree_id

            self.left = parent.right
            self.right = self.left + 1

            session.query(self.__class__).filter(
                self.__class__.right >= self.left,
                self.__class__.tree_id == self.tree_id,
                self.__class__.id != self.id
            ).update({"right": self.__class__.right + 2}, synchronize_session='fetch')

            session.query(self.__class__).filter(
                self.__class__.left > self.left,
                self.__class__.tree_id == self.tree_id,
                self.__class__.id != self.id
            ).update({"left": self.__class__.left + 2}, synchronize_session='fetch')
        else:
            max_tree_id = session.query(func.max(self.__class__.tree_id)).scalar() or 0

            self.tree_id = max_tree_id + 1
            self.left = 1
            self.right = self.left + 1
            
    def delete_node(self, session, soft_delete: bool = False):
        width = self.right - self.left + 1

        if soft_delete:
            session.query(self.__class__).filter(
                self.__class__.left.between(self.left, self.right),
                self.__class__.tree_id == self.tree_id
            ).update(
                {self.__class__.deleted_at: func.now()},
                synchronize_session='fetch'
            )
        else:
            session.query(self.__class__).filter(
                self.__class__.left.between(self.left, self.right),
                self.__class__.tree_id == self.tree_id
            ).delete(synchronize_session='fetch')

        session.query(self.__class__).filter(
            self.__class__.right > self.right,
            self.__class__.tree_id == self.tree_id
        ).update({"right": self.__class__.right - width}, synchronize_session='fetch')

        session.query(self.__class__).filter(
            self.__class__.left > self.right,
            self.__class__.tree_id == self.tree_id
        ).update({"left": self.__class__.left - width}, synchronize_session='fetch')

        
    @classmethod
    def build_tree_for_empty_nodes(cls, session):
        def assign_left_right(node, left_value, tree_id, visited):
            if node.id in visited:
                raise ValueError(f"cyclic dependence {node.id}")
            visited.add(node.id)

            node.left = left_value
            node.tree_id = tree_id

            children = session.query(cls).filter_by(parent_id=node.id).order_by(cls.id).all()

            current_left = left_value + 1
            for child in children:
                current_left = assign_left_right(child, current_left, tree_id, visited)

            node.right = current_left
            session.commit()

            return current_left + 1

        root_nodes = session.query(cls).filter(cls.parent_id.is_(None)).order_by(cls.id).all()

        visited = set()
        tree_id_counter = session.query(func.max(cls.tree_id)).scalar() or 1

        for root in root_nodes:
            assign_left_right(root, 1, tree_id_counter, visited)
            tree_id_counter += 1

    def get_parents(self, session):
        return session.query(self.__class__).where(
            self.__class__.left < self.left,
            self.__class__.right > self.right,
            self.__class__.tree_id == self.tree_id,
            self.__class__.deleted_at == None
        ).order_by(self.__class__.right).all()


    def get_childrens(self, session):
        return session.query(self.__class__).where(
            self.__class__.left > self.left,
            self.__class__.right < self.right,
            self.__class__.tree_id == self.tree_id,
            self.__class__.deleted_at == None
        ).order_by(self.__class__.left).all()


class SAMaterializedPathMixin:
    
    tree_structure = 'MaterializedPath'

    @declared_attr
    def path(cls):
        return Column(String, index=True)

    def update_node(self, session):
        if self.parent_id:
            parent = session.query(self.__class__).get(self.parent_id)
            self.path = f"{parent.path}.{self.id}"
        else:
            self.path = str(self.id)
            
    def delete_node(self, session):
        children = (
            session.query(self.__class__)
            .where(self.__class__.path.like(f"{self.path}.%"))
            .all()
        )
        for child in children:
            child.parent_id = self.parent_id

            if self.parent_id:
                new_parent = session.query(self.__class__).get(self.parent_id)
                child.path = f"{new_parent.path}.{child.id}"
            else:
                child.path = str(child.id)

            session.add(child)

        session.commit()

    @classmethod
    def update_all_nodes(cls, session):
        items_without_path = session.query(cls).where(cls.path == None).all()

        for item in items_without_path:
            item.update_node(session)
            session.add(item)

        session.commit()

    def get_parents(self, session):
        if not self.parent_id:
            return []

        return (
            session.query(self.__class__)
            .where(self.__class__.path.like(f"{self.path[:-len(str(self.id)) - 1]}%"))
            .all()
        )

    def get_children(self, session):
        return session.query(self.__class__).where(self.__class__.path.like(f"{self.path}.%")).all()

    @classmethod
    def get_tree(cls, session):
        return session.query(cls).order_by(cls.path).all()

    @classmethod
    def get_subtree(cls, session, node):
        return session.query(cls).where(cls.path.like(f"{node.path}.%")).all()

class SATSMixin(SACreatedAtMixin, SAUpdatedAtMixin):
    pass