import time
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2])) #modules saved in parent folder

from generate_new_event import new_event
from send_to_firehose import send_to_firehose

SOURCE_SYSTEM = "FUNCTIONALITY_TESTS"


def generate_test_events(attendance_id, patient_id, patient_name):

    events = []

    arrival = new_event(
        attendance_id,
        patient_id,
        "ARRIVAL",
        datetime(2026,1,2),
        SOURCE_SYSTEM,
        patient_name
    )

    events.append(arrival)

   # TRIAGE 
    triage = new_event(
        attendance_id,
        patient_id,
        "TRIAGE_COMPLETED",
        datetime(2026,1,2,1,0,0),
        SOURCE_SYSTEM,
        patient_name
    )

    events.append(triage)

    # CLINICAL REVIEW 
    clinician_review = new_event(
        attendance_id,
        patient_id,
        "CLINICAL_REVIEW_STARTED",
        datetime(2026,1,2,2,0,0),
        SOURCE_SYSTEM,
        patient_name
    )

    events.append(clinician_review)


    # DISCHARGE 
    discharge = new_event(
        attendance_id,
        patient_id,
        "DISCHARGE_HOME",
        datetime(2026,1,2,3,0,0),
        SOURCE_SYSTEM,
        patient_name
    )
    
    events.append(discharge)

    return events


def stream_events(events, delay_seconds):
    for event in events:
        # print(json.dumps(event))
        time.sleep(delay_seconds)
        response = send_to_firehose(event)
        print(response) #Can introduce logging at a later date


if __name__ == "__main__":
    events = generate_test_events( 'Test_Attendance_ID_6', 'Test_Patient_ID_6', 'Updated Name') 
    stream_events(events, delay_seconds=2)
