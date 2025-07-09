"""user_message

Revision ID: 7c562e7ab406
Revises:
Create Date: 2025-07-09 15:04:18.328321

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "7c562e7ab406"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "message_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("user_text", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("assistant_text", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("assistant_send_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_message_history_user_id"), "message_history", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_message_history_user_id"), table_name="message_history")
    op.drop_table("message_history")
