{{ config(materialized='incremental', unique_key='order_id', incremental_strategy='merge') }}

with source_changes as (
    select
        order_id,
        customer_id,
        status,
        net_revenue,
        updated_at,
        md5(
            coalesce(customer_id::varchar, '') || '|' ||
            coalesce(status, '') || '|' ||
            coalesce(net_revenue::varchar, '')
        ) as payload_hash
    from {{ source('raw', 'orders') }}
    {% if is_incremental() %}
      -- Intentional lookback catches late-arriving updates. MERGE + payload hash
      -- makes reprocessing deterministic and idempotent.
      where updated_at >= dateadd(
          minute,
          -30,
          (select coalesce(max(updated_at), '1900-01-01'::timestamp) from {{ this }})
      )
    {% endif %}
),
latest as (
    select *
    from source_changes
    qualify row_number() over (
        partition by order_id
        order by updated_at desc, payload_hash desc
    ) = 1
)
select * from latest
