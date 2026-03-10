select distinct
    attendance_id,
    source_system,
    patient_key
    
from {{ ref('stg_ed_events')}}
