{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge'
) }}

with order_items as (
    select
        order_id,
        sum(quantity * unit_price) as gross_revenue,
        sum(quantity) as units
    from {{ source('raw', 'order_items') }}
    group by 1
),
source_changes as (
    select
        o.order_id,
        o.customer_id,
        o.order_timestamp,
        o.status,
        i.gross_revenue,
        i.units,
        o.updated_at as source_updated_at,
        md5(
            coalesce(o.customer_id::varchar, '') || '|' ||
            coalesce(o.status, '') || '|' ||
            coalesce(i.gross_revenue::varchar, '') || '|' ||
            coalesce(i.units::varchar, '')
        ) as payload_hash
    from {{ source('raw', 'orders') }} o
    join order_items i using (order_id)
    {% if is_incremental() %}
    where o.updated_at >= dateadd(
        minute,
        -30,
        (
            select coalesce(
                max(source_updated_at),
                '1900-01-01'::timestamp
            )
            from {{ this }}
        )
    )
    {% endif %}
),
latest as (
    select *
    from source_changes
    qualify row_number() over (
        partition by order_id
        order by source_updated_at desc, payload_hash desc
    ) = 1
)
select
    order_id,
    customer_id,
    order_timestamp,
    status,
    gross_revenue,
    units,
    source_updated_at,
    payload_hash
from latest
