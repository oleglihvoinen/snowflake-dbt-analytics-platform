create table if not exists ANALYTICS.CONTROL.PIPELINE_RUN_AUDIT (
    run_id varchar not null,
    pipeline_name varchar not null,
    started_at timestamp_tz not null,
    completed_at timestamp_tz,
    previous_watermark timestamp_tz,
    new_watermark timestamp_tz,
    source_rows number,
    target_rows number,
    rejected_rows number,
    reconciliation_status varchar,
    git_sha varchar,
    primary key (run_id)
);

create table if not exists ANALYTICS.CONTROL.DATA_QUALITY_EXCEPTIONS (
    run_id varchar not null,
    model_name varchar not null,
    business_key varchar,
    rule_id varchar not null,
    observed_value variant,
    detected_at timestamp_tz default current_timestamp()
);
