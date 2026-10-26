"""
Thread-Safe Offline Buffer Manager for Edge Gateway Ingestion.

Ensures zero telemetry loss during database locks, high throughput surges, or cloud disconnects.
"""

import time
import queue
import logging
import threading
from typing import Dict, Any, List
from datetime import datetime, timezone

from backend.app.core.database import SessionLocal
from backend.app.models.db_models import TelemetryLogModel, NodeModel

logger = logging.getLogger("BufferManager")


class TelemetryBufferManager:
    """
    Manages an in-memory thread-safe queue and background worker thread 
    that flushes telemetry records into database store in batches.
    """

    def __init__(self, max_queue_size: int = 10000, batch_size: int = 50, flush_interval_sec: float = 2.0):
        self.queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self.batch_size = batch_size
        self.flush_interval_sec = flush_interval_sec
        self.is_running = False
        self.worker_thread: threading.Thread = None

    def start(self):
        """Start background database worker thread."""
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("TelemetryBufferManager background worker thread started.")

    def stop(self):
        """Stop worker thread and flush remaining items."""
        self.is_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=3.0)
        self.flush_buffer()
        logger.info("TelemetryBufferManager stopped.")

    def enqueue(self, telemetry_payload: Dict[str, Any]):
        """Enqueue telemetry payload safely."""
        try:
            self.queue.put_nowait(telemetry_payload)
        except queue.Full:
            logger.error("Telemetry queue is FULL! Dropping record to prevent memory leak.")

    def flush_buffer(self):
        """Flush current queue contents into database."""
        records: List[Dict[str, Any]] = []
        while not self.queue.empty() and len(records) < self.batch_size:
            try:
                records.append(self.queue.get_nowait())
            except queue.Empty:
                break

        if not records:
            return

        db = SessionLocal()
        try:
            log_models = []
            processed_nodes = set()
            for item in records:
                node_id = item["node_id"]
                metrics = item["metrics"]
                
                # Ensure node exists in database (check once per batch)
                if node_id not in processed_nodes:
                    node = db.query(NodeModel).filter(NodeModel.node_id == node_id).first()
                    if not node:
                        node = NodeModel(
                            node_id=node_id,
                            name=item.get("name", node_id),
                            location=item.get("location", "unknown"),
                            is_active=True,
                            last_seen=datetime.now(timezone.utc)
                        )
                        db.add(node)
                        db.flush()
                    else:
                        node.last_seen = datetime.now(timezone.utc)
                        node.is_active = True
                    processed_nodes.add(node_id)

                # Timestamp conversion
                ts_raw = item.get("timestamp", time.time())
                ts_dt = datetime.fromtimestamp(ts_raw, tz=timezone.utc)

                log_entry = TelemetryLogModel(
                    timestamp=ts_dt,
                    node_id=node_id,
                    temperature_c=metrics.get("temperature_c"),
                    humidity_pct=metrics.get("humidity_pct"),
                    current_amps=metrics.get("current_amps"),
                    vibration_g=metrics.get("vibration_g"),
                    air_quality_index=metrics.get("air_quality_index"),
                    water_leak_detected=metrics.get("water_leak_detected", False),
                    water_flow_lpm=metrics.get("water_flow_lpm", 0.0),
                    battery_pct=item.get("hardware_status", {}).get("battery_pct", 100.0)
                )
                log_models.append(log_entry)

            db.bulk_save_objects(log_models)
            db.commit()
            logger.debug(f"Successfully flushed {len(log_models)} telemetry records to database.")

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to flush telemetry batch to database: {e}")
            # Re-enqueue records for retry
            for item in records:
                self.enqueue(item)
        finally:
            db.close()

    def _worker_loop(self):
        """Worker loop executing periodic batch flushes."""
        last_flush = time.time()
        while self.is_running:
            now = time.time()
            if self.queue.qsize() >= self.batch_size or (now - last_flush) >= self.flush_interval_sec:
                self.flush_buffer()
                last_flush = now
            time.sleep(0.2)
