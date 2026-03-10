select 
    event_id,
    attendance_id,
    patient_id,
    event_type,
    event_ts,
    recorded_ts,
    source_system
from {{ ref( 'stg_ed_events') }} 
