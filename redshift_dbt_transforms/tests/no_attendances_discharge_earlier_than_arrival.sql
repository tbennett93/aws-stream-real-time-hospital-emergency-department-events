select *
from {{ ref('fact_ed_attendances') }}
where discharge_ts < arrival_ts