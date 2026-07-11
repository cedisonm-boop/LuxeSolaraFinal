# Qualification Engine

Rules are validated structured JSON. Supported logic: `all`, `any`, `none`, `not`. Supported operators: equals, not_equals, in, not_in, greater_than, greater_than_or_equal, less_than, less_than_or_equal, between, contains, contains_any, contains_all, exists, is_empty, starts_with, ends_with.

Actions include score changes, tags, risk flags, reason codes, verification flags, disqualification, manual review, Paid Audit qualification, program recommendation/exclusion/priority changes, alternative paths, result template selection, CTA selection, and stop processing.

The engine returns public-safe summaries separately from internal traces and never exposes weights in public result responses.
