select distinct patient_id, patient_name 
from {{ ref('stg_ed_events') }}