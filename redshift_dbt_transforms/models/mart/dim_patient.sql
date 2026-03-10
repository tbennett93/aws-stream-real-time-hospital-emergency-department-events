with 
    patient as (
        select 
            patient_id, 
            patient_name ,  
            lag(patient_name) over (partition by patient_id order by recorded_ts ) as lag_name,
            recorded_ts as from_dttm
        from {{ ref('stg_ed_events') }}
    ),

    patient_changes as (
        select 
            patient_id,
            patient_name, 
            from_dttm
        from patient
        WHERE patient_name <> lag_name
        or lag_name is null
    )


select 
    {{ dbt_utils.generate_surrogate_key(['patient_id', 'from_dttm']) }}  as patient_sk,
    patient_id as patient_key,
    patient_name,
    from_dttm,
    lead(from_dttm, 1) over (partition by patient_id order by from_dttm) as to_dttm
from patient_changes