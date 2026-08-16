from fieldservice_logs.work_order_events import WorkOrderUpdate, build_event, decide_follow_up


def test_arrival_without_photo_requires_technician_follow_up() -> None:
    update = WorkOrderUpdate(
        work_order_id="wo-42",
        dispatch_status="arrived",
        technician_id="tech-7",
    )

    decision = decide_follow_up(update)
    event = build_event(update)

    assert decision.required is True
    assert decision.reason == "arrival_missing_completion_photo"
    assert event["level"] == "warning"
    assert event["context"]["contains_customer_data"] is False  # type: ignore[index]
    assert event["context"]["photo_count"] == 0  # type: ignore[index]
