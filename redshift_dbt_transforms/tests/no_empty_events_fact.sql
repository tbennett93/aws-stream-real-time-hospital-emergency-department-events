select 1
from {{ ref('fact_ed_events') }}
having count(*) = 0