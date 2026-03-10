select 
    attendances.attendance_id,
    attendances.source_system,
    arrival.event_ts as arrival_ts,
    review.event_ts as review_ts,
    triage.event_ts as triage_ts,
    disch.event_ts as discharge_ts,
    datediff(minute, arrival.event_ts, review.event_ts) as arrival_to_review_mins,
    datediff(minute, arrival.event_ts, triage.event_ts) as arrival_to_triage_mins,
    datediff(minute, arrival.event_ts, disch.event_ts) as arrival_to_discharge_mins,

    attendances.patient_key,
    patient.patient_sk
from {{ ref( 'int_fact_ed_events_as_attendances') }} attendances
left join {{ ref( 'int_fact_ed_events_max_arrival' )}} arrival
on attendances.attendance_id = arrival.attendance_id
left join {{ ref( 'int_fact_ed_events_max_clinic_review' )}} review
on attendances.attendance_id = review.attendance_id
left join {{ ref( 'int_fact_ed_events_max_triage' )}} triage
on attendances.attendance_id = triage.attendance_id
left join {{ ref( 'int_fact_ed_events_max_discharge' )}} disch
on attendances.attendance_id = disch.attendance_id
left join {{ ref('dim_patient') }} patient
on patient.patient_key = attendances.patient_key
and arrival.event_ts between patient.from_dttm and ISNULL(patient.to_dttm, cast('9999-01-01' as date))