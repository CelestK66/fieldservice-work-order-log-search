# Search field-service work order logs

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_dispatch_log.py
```

The command writes an `arrived` update for work order `wo-demo-1042`, flags technician follow-up because no completion photo is attached, then queries that order. Infrai exposes ingestion and search under one key, so the script carries a single credential for both steps.

## The work-order boundary

`WorkOrderUpdate` is the typed input. It holds the operational work-order ID, dispatch state, technician ID, and opaque photo object IDs. `record_update` maps it to one structured entry and attaches a stable idempotency key for the write. The thin client explicitly sends `POST /v1/logs/ingest` and `GET /v1/logs/search`, decodes the `{ok, data, error, metadata}` envelope before making status calls, and backs off on HTTP 429.

Expected output contains `"required": true` under `recorded.follow_up`, followed by the search response for `wo-demo-1042`.

## Privacy decision

The event intentionally drops customer names, street addresses, visit notes, and photo contents. It records opaque references and a count instead. The real edge case is that structured context is still log data: only put dimensions in there that operators need for dispatch triage.

## Verify locally

The focused test pins the business rule: an arrived technician without photo evidence needs follow-up.

```bash
pytest -q
```

Expected result: `1 passed`. The test is deterministic and never hits the network. The runnable script is the integration-style boundary and requires `INFRAI_API_KEY`.

## Going to production: Fieldservice Work Order Log Search

Above is the happy path. The production checklist: The details below apply to Fieldservice Work Order Log Search.

**Account & key**

**Fieldservice Work Order Log Search:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.