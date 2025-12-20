import json
import datetime
from methods.database import get_raw_logs, get_alerts
from methods.config import CAPACITY_THRESHOLD, EMPTIED_THRESHOLD
from methods.utils import parse_iso_to_utc_naive

bin_full_state = {}


def process_and_store_data(data_payload):
    try:
        reading = json.loads(data_payload)
        print(f"\n[RECEIVED] Bin {reading['bin_id']} @ {reading['capacity_percent']}%")

        reading['received_at'] = datetime.datetime.utcnow()
        if 'timestamp' in reading:
            reading['sensor_timestamp'] = parse_iso_to_utc_naive(reading['timestamp'])

        raw_logs = get_raw_logs()
        raw_logs.insert_one(reading)
        print(f"   -> Stored raw log for {reading['bin_id']}.")

        bin_id = reading['bin_id']
        capacity = reading['capacity_percent']
        
        if bin_id not in bin_full_state:
            bin_full_state[bin_id] = False

        receibed_at = reading['received_at'] + datetime.timedelta(hours=2)
        
        if capacity >= CAPACITY_THRESHOLD:
            if not bin_full_state[bin_id]:
                bin_full_state[bin_id] = True
                alerts_col = get_alerts()
                report_doc = {
                    "bin_id": bin_id,
                    "status": "BIN_FULL_ALERT",
                    "capacity": capacity,
                    "alert_timestamp":  receibed_at,
                    "message": f"Bin {bin_id} has reached {capacity}% capacity."
                }
                alerts_col.insert_one(report_doc)
                print(f"   -> !!! Generated and stored 'BIN_FULL_ALERT' for {bin_id} !!!")
        
        elif capacity < EMPTIED_THRESHOLD and bin_full_state[bin_id]:
            bin_full_state[bin_id] = False
            alerts_col = get_alerts()
            report_doc = {
                "bin_id": bin_id,
                "status": "BIN_EMPTIED_ALERT",
                "capacity": capacity,
                "alert_timestamp": receibed_at,
                "message": f"Bin {bin_id} has been emptied (capacity now {capacity}%)."
            }
            alerts_col.insert_one(report_doc)
            print(f"   -> !!! Generated and stored 'BIN_FREED_ALERT' for {bin_id} !!!")

    except json.JSONDecodeError:
        print("Error: Could not decode JSON payload.")
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}")
