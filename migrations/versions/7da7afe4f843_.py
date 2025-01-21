"""empty message

Revision ID: 7da7afe4f843
Revises: 017cb533cb90
Create Date: 2024-12-02 16:37:33.092866

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7da7afe4f843"
down_revision = "017cb533cb90"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("DocumentEdit", schema=None) as batch_op:
        batch_op.drop_constraint("DocumentEdit_user_id_fkey", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("Entity", schema=None) as batch_op:
        batch_op.add_column(sa.Column("document_edit_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("document_recommendation_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(None, "DocumentEdit", ["document_edit_id"], ["id"])
        batch_op.create_foreign_key(
            None, "DocumentRecommendation", ["document_recommendation_id"], ["id"]
        )

    with op.batch_alter_table("Relation", schema=None) as batch_op:
        batch_op.add_column(sa.Column("document_edit_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("document_recommendation_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(None, "DocumentEdit", ["document_edit_id"], ["id"])
        batch_op.create_foreign_key(
            None, "DocumentRecommendation", ["document_recommendation_id"], ["id"]
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("Relation", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_column("document_recommendation_id")
        batch_op.drop_column("document_edit_id")

    with op.batch_alter_table("Entity", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_column("document_recommendation_id")
        batch_op.drop_column("document_edit_id")

    with op.batch_alter_table("DocumentEdit", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False)
        )
        batch_op.create_foreign_key(
            "DocumentEdit_user_id_fkey", "User", ["user_id"], ["id"]
        )

    # ### end Alembic commands ###
