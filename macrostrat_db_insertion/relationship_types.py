"""Relationship type creation shared by feedback save and overwrite."""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert


def ensure_relationship_type(session, table, name, src_type_id, dst_type_id, *, user_id=None):
    """Resolve a type without committing the caller's transaction."""
    query = select(table.c.id).where(table.c.name == name)
    existing_id = session.execute(query).scalar_one_or_none()
    if existing_id is not None:
        return existing_id
    if src_type_id is None or dst_type_id is None:
        raise ValueError(f"Relationship type {name!r} requires both endpoint types")

    # A competing request may create this name after our SELECT. In that case,
    # read its ID instead of relying on an empty inserted_primary_key result.
    session.execute(
        insert(table).values(
            name=name,
            src_entity_type_id=src_type_id,
            dst_entity_type_id=dst_type_id,
            user_id=user_id,
        ).on_conflict_do_nothing(index_elements=["name"])
    )
    return session.execute(query).scalar_one()
