"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-11
"""
from alembic import op
import sqlalchemy as sa
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('assessments', sa.Column('id', sa.String(36), primary_key=True), sa.Column('key', sa.String(100), nullable=False), sa.Column('name', sa.String(255), nullable=False), sa.Column('stage', sa.String(50), nullable=False)); op.create_index('ix_assessments_key','assessments',['key'],unique=True)
    op.create_table('assessment_versions', sa.Column('id', sa.String(36), primary_key=True), sa.Column('assessment_id', sa.String(36), sa.ForeignKey('assessments.id')), sa.Column('version', sa.Integer), sa.Column('status', sa.String(30)), sa.Column('definition', sa.JSON), sa.Column('published_at', sa.DateTime)); op.create_unique_constraint('uq_assessment_version','assessment_versions',['assessment_id','version'])
    op.create_table('rule_sets', sa.Column('id', sa.String(36), primary_key=True), sa.Column('key', sa.String(100), unique=True), sa.Column('stage', sa.String(50)))
    op.create_table('rule_set_versions', sa.Column('id', sa.String(36), primary_key=True), sa.Column('rule_set_id', sa.String(36), sa.ForeignKey('rule_sets.id')), sa.Column('version', sa.Integer), sa.Column('status', sa.String(30)), sa.Column('rules', sa.JSON))
    op.create_table('programs', sa.Column('id', sa.String(36), primary_key=True), sa.Column('key', sa.String(100), unique=True), sa.Column('name', sa.String(255)), sa.Column('active', sa.Boolean))
    op.create_table('result_templates', sa.Column('id', sa.String(36), primary_key=True), sa.Column('key', sa.String(100), unique=True), sa.Column('content', sa.JSON))
    op.create_table('leads', sa.Column('id', sa.String(36), primary_key=True), sa.Column('email', sa.String(255)), sa.Column('phone', sa.String(80)), sa.Column('name', sa.String(255)), sa.Column('created_at', sa.DateTime)); op.create_index('ix_leads_email','leads',['email'])
    op.create_table('submissions', sa.Column('id', sa.String(36), primary_key=True), sa.Column('public_token', sa.String(80), unique=True), sa.Column('assessment_id', sa.String(36), sa.ForeignKey('assessments.id')), sa.Column('assessment_version_id', sa.String(36), sa.ForeignKey('assessment_versions.id')), sa.Column('lead_id', sa.String(36), sa.ForeignKey('leads.id')), sa.Column('idempotency_key', sa.String(200)), sa.Column('answers', sa.JSON), sa.Column('result', sa.JSON), sa.Column('created_at', sa.DateTime)); op.create_unique_constraint('uq_submission_idem','submissions',['assessment_id','idempotency_key'])
    op.create_table('integration_deliveries', sa.Column('id', sa.String(36), primary_key=True), sa.Column('submission_id', sa.String(36), sa.ForeignKey('submissions.id')), sa.Column('provider', sa.String(50)), sa.Column('status', sa.String(30)), sa.Column('attempt_count', sa.Integer), sa.Column('next_retry_at', sa.DateTime), sa.Column('sanitized_response', sa.Text))

def downgrade():
    for t in ['integration_deliveries','submissions','leads','result_templates','programs','rule_set_versions','rule_sets','assessment_versions','assessments']: op.drop_table(t)
