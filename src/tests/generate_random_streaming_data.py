import random
import time
from datetime import datetime, timedelta, timezone
from send_to_firehose import send_to_firehose
from generate_new_event import new_event

SOURCE_SYSTEM = "RANDOM_GENERATOR"

def generate_attendance_events(attendance_seq: int) -> list[dict]:
    # Generate a realistic ED attendance with out-of-order events, backfilled clinician review & corrected discharge

    base_time = datetime.now(timezone.utc) - timedelta(hours=random.randint(6, 24))

    attendance_id = f"ED{base_time:%Y%m%d}_{attendance_seq}" 
    
    patient_id = f"P{random.randint(100000, 999999)}"

    events = []

    # ARRIVAL 
    arrival_ts = base_time
    arrival = new_event(
        attendance_id,
        patient_id,
        "ARRIVAL",
        arrival_ts,
        SOURCE_SYSTEM
    )
    events.append(arrival)

    # TRIAGE 
    triage_ts = arrival_ts + timedelta(minutes=random.randint(5, 25))
    triage = new_event(
        attendance_id,
        patient_id,
        "TRIAGE_COMPLETED",
        triage_ts,
        SOURCE_SYSTEM
    )
    events.append(triage)

    # DISCHARGE 
    early_discharge_ts = arrival_ts + timedelta(minutes=random.randint(90, 150))
    bad_discharge = new_event(
        attendance_id,
        patient_id,
        "DISCHARGE_HOME",
        early_discharge_ts,
        SOURCE_SYSTEM
    )
    events.append(bad_discharge)

    # CLINICAL REVIEW 
    review_ts = arrival_ts + timedelta(minutes=random.randint(40, 80))
    clinician_review = new_event(
        attendance_id,
        patient_id,
        "CLINICAL_REVIEW_STARTED",
        review_ts,
        SOURCE_SYSTEM
    )
    events.append(clinician_review)

    # # Corrected discharge
    # corrected_discharge_ts = arrival_ts + timedelta(minutes=random.randint(180, 260))
    # corrected_discharge = new_event(
    #     attendance_id,
    #     patient_id,
    #     "DISCHARGE_HOME",
    #     corrected_discharge_ts,
    #     SOURCE_SYSTEM,
    #     supersedes_event_id=bad_discharge["event_id"]
    # )
    # events.append(corrected_discharge)


    return events





def run_generator(num_attendances: int, delay_seconds: float):
    id_start = 1 #can use this to stagger IDs if producing separate test runs
    for x in range(num_attendances):
        events = generate_attendance_events(id_start)

        for event in events:
            # print(json.dumps(event))
            time.sleep(delay_seconds)
            response = send_to_firehose(event)
            print(response) #Can introduce logging at a later date


if __name__ == "__main__":
    run_generator(num_attendances=2, delay_seconds=2) 