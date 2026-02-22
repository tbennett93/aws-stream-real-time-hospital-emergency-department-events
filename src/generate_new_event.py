import uuid
from datetime import datetime, timezone



EVENT_TYPES = [
    "ARRIVAL",                  
    "TRIAGE_COMPLETED",
    "CLINICAL_REVIEW_STARTED",  
    "DISCHARGE_HOME",           #counts as discharge method
    "TRANSFER_TO_WARD",         #counts as discharge method
    "LEFT_WITHOUT_BEING_SEEN"   #counts as discharge method
]



def new_event(
    attendance_id: str,
    patient_id: str,
    event_type: str,
    event_ts: datetime,
    source_system: str
) -> dict:
    
    if event_type not in EVENT_TYPES:
        raise ValueError("Invalid event type") #hard fail for manual review
    
    return {
        "event_id": str(uuid.uuid4()),
        "attendance_id": attendance_id,
        "patient_id": patient_id,
        "event_type": event_type,
        "event_ts": event_ts.isoformat(),
        "recorded_ts": datetime.now(timezone.utc).isoformat(),
        "source_system": source_system
    }