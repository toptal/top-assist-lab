"""Add index columns

Revision ID: 209d7088ea81
Revises: 59b9eced0668
Create Date: 2024-04-12 14:04:01.691616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '209d7088ea81'
down_revision: Union[str, None] = '59b9eced0668'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_page_data_page_id', 'page_data', ['page_id'], unique=True)
    op.create_index('ix_bookmarked_conversations_thread_id', 'bookmarked_conversations', ['thread_id'], unique=False)
    op.create_index('ix_qa_interactions_thread_id', 'qa_interactions', ['thread_id'], unique=False)
    op.create_index('ix_quiz_questions_thread_id', 'quiz_questions', ['thread_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_page_data_page_id', 'page_data')
    op.drop_index('ix_bookmarked_conversations_thread_id', 'bookmarked_conversations')
    op.drop_index('ix_qa_interactions_thread_id', 'qa_interactions')
    op.drop_index('ix_quiz_questions_thread_id', 'quiz_questions')
