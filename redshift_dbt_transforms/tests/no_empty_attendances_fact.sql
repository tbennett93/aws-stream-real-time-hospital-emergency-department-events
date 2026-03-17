select 1
from {{ ref('fact_ed_attendances') }}
having count(*) = 0