with 
    patient as (
        select 
            patient_key, 
            patient_name ,  
            lag(patient_name) over (partition by patient_key order by event_ts ) as lag_name,
            event_ts as from_dttm
        from {{ ref('stg_ed_events') }}
    ),

    patient_changes as (
        select 
            patient_key,
            patient_name, 
            from_dttm
        from patient
        WHERE patient_name <> lag_name
        or lag_name is null
    )


select 
    {{ dbt_utils.generate_surrogate_key(['patient_key', 'from_dttm']) }}  as patient_sk,
    patient_key,
    patient_name,
    from_dttm,
    DATEADD(millisecond, -1, lead(from_dttm, 1) over (partition by patient_key order by from_dttm)) as to_dttm
from patient_changes