select distinct
    attendance_id,
    source_system,
    patient_id
    
from {{ ref('stg_ed_events')}}
