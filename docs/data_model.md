# Data Model

The database uses UUID public identifiers and JSON configuration snapshots for flexible, versioned configuration. Tables include assessments, assessment_versions, rule_sets, rule_set_versions, programs, program_versions, result_templates, leads, submissions, submission_answers, evaluation_runs, rule_evaluations, program_matches, integration_mappings, integration_deliveries, webhook_events, manual_reviews, manual_overrides, admin_users, roles, permissions, and audit_logs.

Submissions record the exact assessment version, rule-set version, answers, evaluation trace, and generated result token used at decision time.
