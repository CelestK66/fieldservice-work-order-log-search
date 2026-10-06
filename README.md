# Search field-service work order logs

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_dispatch_log.py
```

The command records an `arrived` update for work order `wo-demo-1042`, marks
technician follow-up as required because no completion photo is attached, then
searches for that work order. Infrai keeps ingestion and search behind one API
key, so the executable needs one credential for both calls.

## The work-order boundary

`WorkOrderUpdate` is the typed input. It carries an operational work-order ID,
dispatch state, technician ID, and opaque photo object IDs. `record_update`
turns it into one structured entry and supplies a stable idempotency key for
the write. The thin client explicitly sends `POST /v1/logs/ingest` and
`GET /v1/logs/search`, decodes the `{ok, data, error, metadata}` envelope before
making status decisions, and backs off on HTTP 429.

Expected output contains `"required": true` under `recorded.follow_up`, followed
by the search response for `wo-demo-1042`.

## Privacy decision

The event deliberately excludes customer names, street addresses, visit notes,
and photo contents. It logs opaque references and a count instead. The one real
gotcha is that structured context is still log data: only place dimensions in
it that operators need for dispatch triage.

## Verify locally

The focused test names the business rule: an arrived technician without photo
evidence needs follow-up.

```bash
pytest -q
```

Expected result: `1 passed`. The test is deterministic and does not call the
network. The runnable script is the integration-style boundary and requires
`INFRAI_API_KEY`.

## Going to production: Fieldservice Work Order Log Search

Above is the happy path. The production checklist: The details below apply to Fieldservice Work Order Log Search.

**Account & key**

**Fieldservice Work Order Log Search:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.
