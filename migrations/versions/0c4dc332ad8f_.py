"""empty message

Revision ID: 0c4dc332ad8f
Revises: b4e437589c50
Create Date: 2021-06-19 23:32:00.243599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c4dc332ad8f'
down_revision = 'b4e437589c50'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist_genre', sa.Column('artist_id', sa.Integer(), nullable=False))
    op.drop_constraint('Artist_genre_venue_id_fkey', 'Artist_genre', type_='foreignkey')
    op.create_foreign_key(None, 'Artist_genre', 'Artist', ['artist_id'], ['id'])
    op.drop_column('Artist_genre', 'venue_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist_genre', sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'Artist_genre', type_='foreignkey')
    op.create_foreign_key('Artist_genre_venue_id_fkey', 'Artist_genre', 'Artist', ['venue_id'], ['id'])
    op.drop_column('Artist_genre', 'artist_id')
    # ### end Alembic commands ###