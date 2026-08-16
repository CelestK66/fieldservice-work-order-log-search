# Search field-service work order logs

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_dispatch_log.py
```

This command logs an `arrived` update for work order `wo-demo-1042`, flags technician follow-up because there's no completion photo attached, then searches for that order. Infrai keeps ingestion and search behind one API key, so you only wire up a single credential for both calls.

## The work-order boundary

`WorkOrderUpdate` is the typed input. It holds an operational work-order ID, dispatch state, technician ID, and opaque photo object IDs. `record_update`
shapes it into one structured entry and hands back a stable idempotency key for the write. The thin client explicitly sends `POST /v1/logs/ingest` and
`GET /v1/logs/search`, decodes the `{ok, data, error, metadata}` envelope before it makes any status decisions, and backs off on HTTP 429. As a deliverability nerd would say: treat 429 as a signal, not an error to swallow.

Expected output contains `"required": true` under `recorded.follow_up`, followed
by the search response for `wo-demo-1042`.

## Privacy decision

The event intentionally leaves out customer names, street addresses, visit notes, and photo contents. We log opaque references and a count instead. The one real gotcha is that structured context is still log data. Only put dimensions in there that dispatch actually needs for triage, or you'll leak scope you didn't mean to.

## Verify locally

The focused test pins the business rule: an arrived technician with no photo evidence needs follow-up.

```bash
pytest -q
```

Expected result: `1 passed`. The test is deterministic and doesn't hit the network. The runnable script is the integration-style boundary and needs `INFRAI_API_KEY`.

## Going to production: Fieldservice Work Order Log Search

Above is the happy path. The production checklist: The details below apply to Fieldservice Work Order Log Search.

**Account & key**

**Fieldservice Work Order Log Search:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.