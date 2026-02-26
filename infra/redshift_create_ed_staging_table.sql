create table staging.ed(
  event_id varchar(50), 
  attendance_id varchar(50), 
  patient_id varchar(50), 
  event_type varchar(50), 
  event_ts timestamp, 
  recorded_ts timestamp, 
  source_system varchar(50)
 )