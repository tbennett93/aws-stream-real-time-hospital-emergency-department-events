import uuid
import random
import time
from datetime import datetime, timedelta, timezone
import json
import boto3
import base64


SOURCE_SYSTEM = "ED_SYSTEM_A"

EVENT_TYPES = [
    "ARRIVAL",
    "TRIAGE_COMPLETED",
    "CLINICAL_REVIEW_STARTED",
    "DISCHARGE_HOME",
    "TRANSFER_TO_WARD",
    "LEFT_WITHOUT_BEING_SEEN"
]


def new_event(
    attendance_id: str,
    patient_id: str,
    event_type: str,
    event_ts: datetime,
    is_update: bool = False,
    supersedes_event_id: str | None = None,
    attributes: dict | None = None
) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "attendance_id": attendance_id,
        "patient_id": patient_id,
        "event_type": event_type,
        "event_ts": event_ts.isoformat(),
        "recorded_ts": datetime.now(timezone.utc).isoformat(),
        "source_system": SOURCE_SYSTEM,
        "is_update": is_update,
        "supersedes_event_id": supersedes_event_id,
        "attributes": attributes or {}
    }


def generate_attendance_events(attendance_seq: int) -> list[dict]:
    # Generate a realistic ED attendance with out-of-order events, backfilled clinician review & corrected discharge

    base_time = datetime.now(timezone.utc) - timedelta(hours=random.randint(6, 24))

    attendance_id = f"ED{base_time:%Y%m%d}_{attendance_seq}"
    
    patient_id = f"P{random.randint(100000, 999999)}"

    events = []

    # ARRIVAL (always first, correct)
    arrival_ts = base_time
    arrival = new_event(
        attendance_id,
        patient_id,
        "ARRIVAL",
        arrival_ts
    )
    events.append(arrival)

    # TRIAGE (sometimes delayed)
    triage_ts = arrival_ts + timedelta(minutes=random.randint(5, 25))
    triage = new_event(
        attendance_id,
        patient_id,
        "TRIAGE_COMPLETED",
        triage_ts,
        attributes={"triage_category": random.randint(1, 5)}
    )
    events.append(triage)

    # DISCHARGE recorded too early (mistake)
    early_discharge_ts = arrival_ts + timedelta(minutes=random.randint(90, 150))
    bad_discharge = new_event(
        attendance_id,
        patient_id,
        "DISCHARGE_HOME",
        early_discharge_ts
    )
    events.append(bad_discharge)

    # CLINICAL REVIEW backfilled later (event time before discharge)
    review_ts = arrival_ts + timedelta(minutes=random.randint(40, 80))
    clinician_review = new_event(
        attendance_id,
        patient_id,
        "CLINICAL_REVIEW_STARTED",
        review_ts
    )
    events.append(clinician_review)

    # Corrected discharge
    corrected_discharge_ts = arrival_ts + timedelta(minutes=random.randint(180, 260))
    corrected_discharge = new_event(
        attendance_id,
        patient_id,
        "DISCHARGE_HOME",
        corrected_discharge_ts,
        is_update=True,
        supersedes_event_id=bad_discharge["event_id"]
    )
    events.append(corrected_discharge)


    return events


def send_to_firehose(event):
    event = json.dumps(event).encode('utf-8') #convert dict to bytes for firehose
    # event = base64.b64encode(event)
    firehose = boto3.client('firehose')
    firehose.put_record(    
        DeliveryStreamName='ED-Event-Stream',
        Record={
            'Data': event
    }
)

def run_generator(num_attendances: int, delay_seconds: float):
    id_start = 3 #can use this to stagger IDs if producing separate test runs
    for x in range(num_attendances):
        events = generate_attendance_events(id_start)

        for event in events:
            print(json.dumps(event))
            time.sleep(delay_seconds)
            response = send_to_firehose(event)
            print(response)
            





if __name__ == "__main__":
    print(boto3.client("sts").get_caller_identity())

    run_generator(num_attendances=2, delay_seconds=1)