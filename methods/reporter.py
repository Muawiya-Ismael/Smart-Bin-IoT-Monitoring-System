import datetime
import time
from methods.database import get_raw_logs, get_reports
from methods.config import CAPACITY_THRESHOLD
from methods.utils import minute_floor, parse_iso_to_utc_naive
from methods.metrics import calculate_bin_metrics


def generate_minute_reports():

    print("Minute Reporter initiated. Aligning to next minute boundary...")
    now = datetime.datetime.utcnow()
    next_minute = minute_floor(now) + datetime.timedelta(minutes=1)
    wait_seconds = (next_minute - now).total_seconds()
    time.sleep(wait_seconds)

    while True:
        minute_end = minute_floor(datetime.datetime.utcnow())
        minute_start = minute_end - datetime.timedelta(minutes=1)

        print(f"\n--- Generating Minute Report ({minute_start.isoformat()} to {minute_end.isoformat()}) ---")
        
        try:
            raw_logs = get_raw_logs()
            reports_col = get_reports()
            
            query = {
                "$or": [
                    {"sensor_timestamp": {"$gte": minute_start, "$lt": minute_end}},
                    {"received_at": {"$gte": minute_start, "$lt": minute_end}},
                ]
            }

            cursor = raw_logs.find(query)
            all_readings = []
            for r in cursor:
                ts = None
                if 'sensor_timestamp' in r and r['sensor_timestamp'] is not None:
                    ts = r['sensor_timestamp']
                    if isinstance(ts, str):
                        ts = parse_iso_to_utc_naive(ts)
                if ts is None and 'received_at' in r:
                    ts = r['received_at']
                if ts is None:
                    ts = datetime.datetime.utcnow()
                r['ts'] = ts
                all_readings.append(r)
            
            if not all_readings:
                print("No readings found in the last minute. Skipping report.")
                time.sleep(0.5)
                continue

            bins_data = {}
            all_readings.sort(key=lambda x: (x.get('bin_id'), x.get('ts')))
            for reading in all_readings:
                bid = reading.get('bin_id')
                bins_data.setdefault(bid, []).append(reading)
            
            generated_reports = []
            for bid, readings in bins_data.items():
                readings.sort(key=lambda r: r.get('ts'))
                last_capacity = readings[-1]['capacity_percent']
                sentinel = {'capacity_percent': last_capacity, 'ts': minute_end}
                readings_with_sentinel = readings + [sentinel]

                metrics = calculate_bin_metrics(bid, readings_with_sentinel)
                if metrics:
                    # Add two hours to the times
                    report_start_time_plus2 = minute_start + datetime.timedelta(hours=2)
                    report_end_time_plus2 = minute_end + datetime.timedelta(hours=2)
                    report_generated_at_plus2 = metrics['report_generated_at'] + datetime.timedelta(hours=2)
                    report_doc = {
                        'bin_id': bid,
                        'report_start_time': report_start_time_plus2,
                        'report_end_time': report_end_time_plus2,
                        'report_generated_at': report_generated_at_plus2,
                        'capacity_avg_percent': metrics['avg_capacity'],
                        'capacity_max_percent': metrics['max_capacity'],
                        'capacity_min_percent': metrics['min_capacity'],
                        'readings_count': metrics['readings_count'],
                        'emptied_count': metrics['freed_count'],
                        'last_emptied_time': metrics['last_freed_time'],
                        'max_full_duration_seconds': int(metrics.get('max_full_duration_seconds', 0)),
                    }
                    reports_col.update_one({'bin_id': bid, 'report_start_time': report_start_time_plus2}, {'$set': report_doc}, upsert=True)
                    generated_reports.append(report_doc)
            
            if generated_reports:
                print(f"Generated/updated {len(generated_reports)} minute reports.")

            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error in Minute Reporter: {e}")
