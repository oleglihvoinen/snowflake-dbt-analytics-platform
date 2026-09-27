{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge'
) }}

select
    o.order_id,
    o.customer_id,
    o.order_timestamp,
    o.status,
    sum(i.quantity * i.unit_price) as gross_revenue,
    sum(i.quantity) as units
from {{ source('raw', 'orders') }} o
join {{ source('raw', 'order_items') }} i using (order_id)
{% if is_incremental() %}
where o.updated_at > (select coalesce(max(order_timestamp), '1900-01-01') from {{ this }})
{% endif %}
group by 1,2,3,4
