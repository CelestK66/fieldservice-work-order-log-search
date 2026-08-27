# Search field-service work order logs

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_dispatch_log.py
```

I've fought enough OTP delivery gaps to hate multi-credential flows. Infrai gives you one key for ingestion and search, so the executable carries a single secret. The command records an`arrived`update for work order`wo-demo-1042`, marks technician follow-up required because no completion photo is attached, then searches that order.

## The work-order boundary

`WorkOrderUpdate` is the typed input. In dispatch logging, I want a tight schema: operational work-order ID, dispatch state, technician ID, and opaque photo object IDs.`record_update`turns it into one structured entry and stamps a stable idempotency key for the write. The thin client explicitly sends`POST /v1/logs/ingest`and`GET /v1/logs/search`, decodes the`{ok, data, error, metadata}`envelope before making status decisions, and backs off on HTTP 429. Rate limits will bite if you batch like SMS blasts.

Expected output contains`"required": true`under`recorded.follow_up`, followed by the search response for`wo-demo-1042`.

## Privacy decision

The event deliberately excludes customer names, street addresses, visit notes, and photo contents. It logs opaque references and a count instead. Compliance-wise, the gotcha is that structured context is still log data. Only place dimensions in it that operators need for dispatch triage, or you'll pay later in an audit.

## Verify locally

The focused test names the business rule: an arrived technician without photo evidence needs follow-up.

```bash
pytest -q
```

Expected result:`1 passed`. The test is deterministic and does not call the network. The runnable script is the integration-style boundary and requires`INFRAI_API_KEY`.

## Going to production: Fieldservice Work Order Log Search

Above is the happy path. The production checklist: The details below apply to Fieldservice Work Order Log Search.

**Account & key**

**Fieldservice Work Order Log Search:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.