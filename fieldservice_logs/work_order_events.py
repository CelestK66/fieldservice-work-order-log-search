"""Privacy-minimized events for a field-service work order."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from .infrai_client import InfraiLogs


DispatchStatus = Literal["assigned", "en_route", "arrived", "completed"]


@dataclass(frozen=True)
class WorkOrderUpdate:
    work_order_id: str
    dispatch_status: DispatchStatus
    technician_id: str
    photo_object_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class FollowUpDecision:
    required: bool
    reason: str


def decide_follow_up(update: WorkOrderUpdate) -> FollowUpDecision:
    if update.dispatch_status == "arrived" and not update.photo_object_ids:
        return FollowUpDecision(True, "arrival_missing_completion_photo")
    return FollowUpDecision(False, "evidence_not_due_or_present")


def build_event(update: WorkOrderUpdate) -> dict[str, object]:
    decision = decide_follow_up(update)
    return {
        "level": "warning" if decision.required else "info",
        "message": "field service work order updated",
        "context": {
            "work_order_id": update.work_order_id,
            "dispatch_status": update.dispatch_status,
            "technician_id": update.technician_id,
            "photo_count": len(update.photo_object_ids),
            "photo_object_ids": list(update.photo_object_ids),
            "follow_up": asdict(decision),
            "contains_customer_data": False,
        },
    }


def record_update(client: InfraiLogs, update: WorkOrderUpdate) -> dict[str, object]:
    event = build_event(update)
    client.ingest([event], idempotency_key=f"work-order:{update.work_order_id}:{update.dispatch_status}")
    return {"work_order_id": update.work_order_id, "follow_up": event["context"]["follow_up"]}  # type: ignore[index]


def find_work_order(client: InfraiLogs, work_order_id: str) -> dict[str, object]:
    return client.search(work_order_id)
