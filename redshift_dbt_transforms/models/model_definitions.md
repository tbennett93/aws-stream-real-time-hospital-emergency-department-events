{% docs event_id %}
An identifier to uniquely identify an event
{% enddocs %}


{% docs attendance_id %}
An identifier to uniquely identify an attendance
{% enddocs %}

{% docs patient_key %}
Represents the source system key to identify a patient. 

To uniquely identify a patient at a point in time, use patient_sk
{% enddocs %}


{% docs event_type %}
Categorical label describing the type of event that occurred.

Represents the business classification of the event (for example referral created,
status change, observation recorded, etc.). Used to distinguish different event
records within the same patient timeline.
{% enddocs %}


{% docs event_ts %}
Timestamp when the event occurred in the real-world clinical or operational context.

Represents the effective time of the event itself (for example when a referral was
made or an observation became effective), rather than when it was recorded in the
source system.
{% enddocs %}


{% docs recorded_ts %}
Timestamp when the event was recorded in the source system.

This will usually from `event_ts`.

Often used to determine the most recent version of a record to decide the most up-to-date version of the truth
{% enddocs %}


{% docs source_system %}
Identifier for the source system that produced the record.

Used to track data provenance when events originate from multiple operational
systems.
{% enddocs %}


{% docs patient_sk %}
Surrogate key uniquely identifying a patient record.

Unlike `patient_key` (the business identifier), this key uniquely identifies a
single patient entity within the warehouse and is safe to use for joins.
{% enddocs %}


{% docs patient_name %}
The name of the patient

{% enddocs %}
