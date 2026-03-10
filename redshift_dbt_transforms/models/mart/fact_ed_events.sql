select 
    events.event_id,
    events.attendance_id,
    events.patient_key,
    events.event_type,
    events.event_ts,
    events.recorded_ts,
    events.source_system,
    patient.patient_sk
from {{ ref( 'stg_ed_events') }} events

left join {{ ref('dim_patient') }} patient
on patient.patient_key = events.patient_key
and events.event_ts between patient.from_dttm and ISNULL(patient.to_dttm, cast('9999-01-01' as date))