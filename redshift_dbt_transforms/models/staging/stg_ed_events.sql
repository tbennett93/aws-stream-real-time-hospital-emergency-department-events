with source as (

    select * from {{ source('ed_events','ed') }}

),

clean as (

    select
        cast(event_id as varchar) as event_id,
        cast(attendance_id as varchar) as attendance_id,
        cast(patient_id as varchar) as patient_id,
        cast(upper(event_type) as varchar) as event_type,
        cast(event_ts as timestamp) as event_ts,
        cast(recorded_ts as timestamp) as recorded_ts,
        cast(upper(source_system) as varchar) as source_system,
        row_number() over (partition by event_id order by recorded_ts desc) rn 

    from source

)

select * 
from clean
where rn=1