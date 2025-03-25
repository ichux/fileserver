"""add triggers

Revision ID: a59f9d6601b4
Revises: e7a13cb13d50
Create Date: 2025-03-25 13:01:37.906342+01:00

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a59f9d6601b4"
down_revision: Union[str, None] = "e7a13cb13d50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
            CREATE TRIGGER set_users_timestamps_and_enabled_on_insert
            BEFORE INSERT ON users
            FOR EACH ROW
            BEGIN
                UPDATE users 
                SET added_on = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP,
                    enabled = 1
                WHERE id = NEW.id;
            END;
        """
    )
    # Trigger for update (updates only updated_at)
    op.execute(
        """
            CREATE TRIGGER update_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            BEGIN
                UPDATE users 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = OLD.id;
            END;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER set_users_timestamps_and_enabled_on_insert")
    op.execute("DROP TRIGGER update_users_updated_at")
