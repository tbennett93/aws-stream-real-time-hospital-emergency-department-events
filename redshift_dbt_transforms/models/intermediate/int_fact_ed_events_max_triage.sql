with _data as (
    select 
        event_id,
        attendance_id,
        patient_id,
        event_ts,
        recorded_ts,
        source_system,
        patient_name,
        ROW_NUMBER() over (partition by attendance_id order by recorded_ts desc) rn
    from {{ ref('stg_ed_events')}}
    where event_type = 'TRIAGE_COMPLETED'
)

select 
    event_id,
    attendance_id,
    patient_id,
    event_ts,
    recorded_ts,
    source_system,
    patient_name
from
    _data
where rn = 1