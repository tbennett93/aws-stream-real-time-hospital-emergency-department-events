select *
from {{ ref('stg_ed_events') }}
where recorded_ts > getdate()