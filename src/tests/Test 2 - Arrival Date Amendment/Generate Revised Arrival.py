import time
import random
from datetime import datetime, timedelta, timezone, date
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).resolve().parents[2])) #modules saved in parent folder

from generate_new_event import new_event
from send_to_firehose import send_to_firehose


SOURCE_SYSTEM = "FUNCTIONALITY_TESTS"




def generate_test_events(attendance_id, patient_id):

    events = []

    arrival = new_event(
        attendance_id,
        patient_id,
        "ARRIVAL",
        datetime(2026,2,1),
        SOURCE_SYSTEM
    )

    events.append(arrival)

    return events


def stream_events(events, delay_seconds):
    for event in events:
        # print(json.dumps(event))
        time.sleep(delay_seconds)
        response = send_to_firehose(event)
        print(response) #Can introduce logging at a later date


if __name__ == "__main__":
    events = generate_test_events( 'Test_Attendance_ID_2', 'Test_Patient_ID_2') 
    stream_events(events, delay_seconds=2)
