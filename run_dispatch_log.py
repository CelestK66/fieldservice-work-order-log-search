"""Record and search one field-service dispatch update."""

import json

from fieldservice_logs.infrai_client import InfraiLogs
from fieldservice_logs.work_order_events import WorkOrderUpdate, find_work_order, record_update


def main() -> None:
    client = InfraiLogs()
    update = WorkOrderUpdate(
        work_order_id="wo-demo-1042",
        dispatch_status="arrived",
        technician_id="tech-17",
    )
    result = record_update(client, update)
    matches = find_work_order(client, update.work_order_id)
    print(json.dumps({"recorded": result, "search": matches}, indent=2))


if __name__ == "__main__":
    main()
