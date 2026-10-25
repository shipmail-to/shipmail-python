# Shipmail Python SDK

Official Python SDK for the [Shipmail](https://shipmail.to) API. Provides both synchronous and asynchronous clients. Requires Python 3.10+.

## Installation

```bash
pip install shipmail
```

## Quick Start

```python
from shipmail import Shipmail

client = Shipmail("sm_live_...")

# Create a domain
domain = client.domains.create({"name": "example.com"})

# Send an email
message = client.messages.send({
    "mailbox_id": "mbx_...",
    "to": [{"address": "user@example.com"}],
    "subject": "Hello",
    "text": "Hi there",
    "client_reference": "crm-123",
    "metadata": {"campaign": "onboarding"},
    "source_rfc_message_id": "<crm-123@example.com>",
})
same_message = client.messages.list({"client_reference": "crm-123"})
```

### Async

```python
from shipmail import AsyncShipmail

async with AsyncShipmail("sm_live_...") as client:
    domain = await client.domains.create({"name": "example.com"})

    message = await client.messages.send({
        "mailbox_id": "mbx_...",
        "to": [{"address": "user@example.com"}],
        "subject": "Hello",
        "text": "Hi there",
    })
```

## Configuration

```python
from shipmail import Shipmail

client = Shipmail(
    "sm_live_...",
    base_url="https://shipmail.to/api/v1",  # default
    max_retries=2,      # default, retries eligible requests
    timeout=30.0,       # default, in seconds
)
```

## Resources

### Domains

```python
domain = client.domains.create({"name": "example.com"})
domains = client.domains.list({"limit": 10})
domain = client.domains.get("dom_...")
updated = client.domains.update("dom_...", {"catch_all_mailbox_id": "mbx_..."})
client.domains.delete("dom_...")
result = client.domains.verify("dom_...")
records = client.domains.get_dns_records("dom_...")
health = client.domains.get_health("dom_...")
```

### Mailboxes

```python
mailbox = client.mailboxes.create({
    "domain_id": "dom_...",
    "address": "hello",
    "password": "StrongPass123",
    "display_name": "Hello",
})
mailboxes = client.mailboxes.list({"domain_id": "dom_..."})
mailbox = client.mailboxes.get("mbx_...")
updated = client.mailboxes.update("mbx_...", {"display_name": "New Name"})
client.mailboxes.suspend("mbx_...")
client.mailboxes.resume("mbx_...")
updated = client.mailboxes.reset_password("mbx_...", {"password": "NewPassword1"})
forwarding = client.mailboxes.create_forwarding("mbx_...", {
    "destination": "owner@example.net",
    "recipient": "support@example.com",
})
forwarding_list = client.mailboxes.list_forwarding("mbx_...")
client.mailboxes.delete_forwarding("mbx_...", forwarding["id"])
app_password = client.mailboxes.create_app_password("mbx_...", {
    "name": "Desktop mail",
    "expires_at": "2026-10-01T00:00:00Z",
})
app_passwords = client.mailboxes.list_app_passwords("mbx_...")
client.mailboxes.revoke_app_password("mbx_...", app_password["id"])
folders = client.mailboxes.list_folders("mbx_...")
folder = client.mailboxes.create_folder("mbx_...", {"name": "VIP", "parent_id": None})
client.mailboxes.update_folder("mbx_...", folder["id"], {"name": "VIP Clients"})
client.mailboxes.delete_folder("mbx_...", folder["id"])
identities = client.mailboxes.list_identities("mbx_...")
rules = client.mailboxes.get_rules("mbx_...")
rules = client.mailboxes.update_rules("mbx_...", {
    "rules": [
        *rules["rules"],
        {
            "id": "4f5a9d74-b0f1-49a7-bbfb-1f2af841f5b2",
            "name": "Flag invoices",
            "enabled": True,
            "position": len(rules["rules"]),
            "match_mode": "all",
            "stop": False,
            "conditions": [{"type": "subject_contains", "value": "invoice"}],
            "actions": [{"type": "star"}, {"type": "send_webhook"}],
        },
    ],
})
client.mailboxes.delete("mbx_...")

mailbox_id = "550e8400-e29b-41d4-a716-446655440000"
invoices = client.mailboxes.list_inbox_messages(mailbox_id, {
    "from": "billing@vendor.example",
    "subject": "invoice",
    "has_attachment": True,
})

# Changing API-agent hold requires both mailboxes:write and messages:review.
client.mailboxes.update(mailbox_id, {"agent_security_hold": True})
# Use a separate securityReview credential to inspect and release the exact snapshot.
reviewer = Shipmail("sm_live_review_...")
exact = reviewer.mailboxes.get_inbox_message(mailbox_id, invoices["data"][0]["id"])
reviewer.mailboxes.release_inbox_message_security(
    mailbox_id,
    exact["id"],
    {
        "decision": "release",
        "reason": "Reviewed against the customer request",
        "expected_content_sha256": exact["security"]["content_sha256"],
    },
)

queue = client.mailboxes.list_inbox_threads(mailbox_id, {
    "attention_state": "needs_reply",
    "after": "2025-07-20T00:00:00.000Z",
})
candidate = queue["data"][0]
# "conversation_id" is the ID to store. "thread_id" is deprecated: it still works and its
# value is unchanged, but the mail server can re-thread it when conversations merge.
draft = client.mailboxes.create_inbox_reply_draft(
    mailbox_id,
    candidate["conversation_id"],
    {"text": "Thanks for the note.", "expected_version": candidate["version"]},
)
# "removed_formatting" lists what the HTML sanitiser dropped, such as "table" or "h4".
print(draft["removed_formatting"])

# Read and revise a draft before sending. The new body replaces the old one.
client.mailboxes.list_inbox_reply_drafts(mailbox_id, candidate["conversation_id"])
client.mailboxes.get_inbox_reply_draft(mailbox_id, candidate["conversation_id"], draft["id"])
client.mailboxes.update_inbox_reply_draft(
    mailbox_id,
    candidate["conversation_id"],
    draft["id"],
    {"html": "<p>Thanks for the note.</p><p>I will send the contract today.</p>"},
)

# Read and approve the final snapshot. Any later subject/body edit fails with 409.
approved = client.mailboxes.get_inbox_reply_draft(
    mailbox_id, candidate["conversation_id"], draft["id"]
)
if approved["content_sha256"] is None:
    raise RuntimeError("Draft content is incomplete; read it again.")
client.mailboxes.send_inbox_reply_draft(
    mailbox_id,
    candidate["conversation_id"],
    draft["id"],
    expected_content_sha256=approved["content_sha256"],
)

# Or discard it. Drafts that are sending or sent cannot be deleted.
# client.mailboxes.delete_inbox_reply_draft(mailbox_id, candidate["conversation_id"], draft["id"])

# A full thread read carries "version" too: pass it as "expected_version".
thread = client.mailboxes.get_inbox_thread(mailbox_id, candidate["conversation_id"])
print(thread["version"])

# Save a new message to Drafts for a human to review and send. This never sends.
new_draft = client.mailboxes.create_inbox_draft(mailbox_id, {
    "to": ["Jane <jane@example.com>"],
    "subject": "Kickoff",
    "text": "Draft for review.",
})
```

### Messages

```python
message = client.messages.send({
    "mailbox_id": "mbx_...",
    "to": [{"address": "user@example.com", "name": "User"}],
    "cc": [{"address": "cc@example.com"}],
    "subject": "Hello",
    "html": "<p>Hi there</p>",
    "text": "Hi there",
})

message = client.messages.get("msg_...")

analytics = client.messages.list_analytics({
    "updated_after": "2026-07-01T00:00:00.000Z",
    "limit": 100,
})
# Follow analytics["pagination"]["next_cursor"], then persist snapshot_at.
```

### Scheduled messages and attachments

Stage raw files up to 25 MB and use the returned opaque ID instead of embedding base64 in JSON.
Base64 attachments remain supported for existing clients.

```python
with open("invoice.pdf", "rb") as file:
    attachment = client.mailboxes.stage_attachment(
        "mbx_...",
        filename="invoice.pdf",
        content_type="application/pdf",
        data=file.read(),
    )

scheduled = client.messages.send({
    "mailbox_id": "mbx_...",
    "to": ["customer@example.com"],
    "subject": "Invoice",
    "text": "Attached.",
    "staged_attachment_ids": [attachment["id"]],
    "scheduled_at": "2026-08-01T08:00:00.000Z",
})

pending = client.scheduled_messages.list()
detail = client.scheduled_messages.get(scheduled["id"])
client.scheduled_messages.update(scheduled["id"], {
    "to": detail["to"],
    "subject": detail["subject"],
    "text": detail.get("text", ""),
    "staged_attachment_ids": [attachment["id"]],
    "scheduled_at": "2026-08-02T08:00:00.000Z",
})
client.scheduled_messages.cancel(scheduled["id"])
```

Staged IDs expire after 24 hours and are bound to the API key, organization, and mailbox that
created them.

Browser-hosted components can keep the Shipmail API key off the page by calling
`client.mailboxes.prepare_staged_attachment_upload(...)`. It returns a five-minute, single-use
upload URL bound to the filename, MIME type, exact byte size, and lowercase SHA-256 digest. Upload
the raw bytes without credentials or redirects, then use the returned `sat_...` ID in a send.

### Sandbox

Use an `sm_test_...` API key to simulate sends and inbound replies without sending real email:

```python
test_client = Shipmail("sm_test_...")
test_client.messages.send({
    "mailbox_id": "mbx_...",
    "to": ["customer@example.com"],
    "subject": "Sandbox test",
    "text": "Not delivered",
    "sandbox_outcome": "bounced",
})
test_client.mailboxes.inject_sandbox_inbound("mbx_...", {
    "from_": "customer@example.com",
    "subject": "Re: Sandbox test",
    "text": "Fake inbound reply",
})
```

### Threads

```python
threads = client.threads.list({"mailbox_id": "mbx_..."})
thread = client.threads.get(threads["data"][0]["id"], {"mailbox_id": "mbx_..."})
reply = client.threads.reply(threads["data"][0]["id"], {
    "mailbox_id": "mbx_...",
    "text": "Thanks for your email",
    "to": [{"address": "user@example.com"}],
})
```

### Reply scans

Use a durable, atomically captured scan for a historical window, then page every result using the
opaque cursor unchanged. Creation returns the completed snapshot; retry a `409` with bounded
backoff while historical header classification finishes. Scans are retained for 30 days.

```python
from datetime import datetime, timedelta, timezone

scan = client.reply_scans.create({
    "mailbox_ids": ["550e8400-e29b-41d4-a716-446655440000"],
    "after": (datetime.now(timezone.utc) - timedelta(days=365)).isoformat(),
})
results = client.reply_scans.list_results(scan["id"], {"limit": 100})
print(results["data"])
```

### Audiences

```python
audience = client.audiences.create({
    "name": "Newsletter",
    "consent_source": "Website signup form",
})

client.audiences.subscribers.add(audience["id"], {
    "email_address": "jane@example.com",
    "merge_fields": {"plan": "pro"},
})

client.audiences.feeds.update(audience["id"], {
    "enabled": True,
    "title": "Release notes",
    "canonical_url": "https://example.com/feed.xml",
    "entry_limit": 25,
})
# Graceful migration: the current URL redirects to the replacement.
client.audiences.feeds.rotate(audience["id"])
# Leaked URL: immediately invalidate both current and previous URLs.
client.audiences.feeds.revoke(audience["id"])
```

### Newsletters

```python
sender_identities = client.newsletters.sender_identities.list({"limit": 25})
assets = client.newsletters.assets.list({"kind": "image", "q": "hero", "limit": 25})
for asset in client.newsletters.assets.list_auto_paginating(kind="image", q="hero", limit=25):
    print(asset["filename"])
with open("hero.png", "rb") as f:
    hero = client.newsletters.assets.upload({
        "filename": "hero.png",
        "content_type": "image/png",
        "data": f.read(),
    })
existing_hero = client.newsletters.assets.register_from_url({
    "url": "https://cdn.shipmail.to/newsletter-images/org_123/hero.png",
    "filename": "hero.png",
})

newsletter = client.newsletters.create({
    "audience_id": "aud_...",
    "sender_identity_id": sender_identities["data"][0]["id"],
    "name": "July changelog",
    "subject": "What shipped in July",
    "preview_text": "A quick product update",
    "blocks": [
        {"type": "heading", "level": 1, "text": "July updates"},
        {"type": "callout", "variant": "info", "title": "Quick note", "body": "A short intro."},
        {"type": "paragraph", "body": "A quick product update."},
        {"type": "image", "url": hero["url"], "alt": "Product screenshot"},
        {"type": "image", "url": existing_hero["url"], "alt": "Existing CDN screenshot"},
        {
            "type": "columns",
            "ratio": "50-50",
            "left": {"title": "For teams", "image_url": hero["url"], "image_fit": "natural"},
            "right": {"title": "For agents", "image_url": existing_hero["url"], "image_fit": "contain"},
        },
    ],
})

client.newsletters.preview(newsletter["id"])

client.newsletters.send_test(newsletter["id"], {
    "recipient_email": "owner@example.com",
})

client.newsletters.preflight(newsletter["id"])

client.newsletters.schedule(newsletter["id"], {
    "scheduled_at": "2026-08-01T09:00:00.000Z",
})
```

Newsletter test sends and schedules must pass preflight. Guardrail failures raise
`ValidationError` with the failed preflight items in `err.details`.
Preflight responses include `url_breakdown` so you can see which links, image
URLs, and video thumbnails contribute to deliverability checks.
Paragraph, quote, callout, list-item, and column bodies accept bare text or
sanitized inline HTML. Use `<p>` and `<br>` for line breaks. Allowed tags are
`a`, `b`, `br`, `code`, `em`, `i`, `p`, `s`, `span`, `strong`, and `u`. Use
`body_html` or `custom_html` for a fully custom email-safe layout.
Concurrent newsletter updates can raise `ConflictError` (409). Fetch the latest
newsletter, merge your changes, and retry the update.

### Webhooks

```python
webhook = client.webhooks.create({
    "url": "https://example.com/webhook",
    "events": ["message.received", "message.sent"],
    "description": "My webhook",
    # Optional. Sent as the Authorization header of every delivery. Never returned.
    "authorization": "Bearer your-endpoint-key",
    # Optional. A whsec_ secret from the receiving service, such as a Grok automation.
    # Deliveries then carry Standard Webhooks signatures. Never returned.
    "standard_webhooks_secret": "whsec_...",
})
# webhook["secret"] is only available at creation time
# webhook["has_authorization"] is True when an authorization value is set
# webhook["has_standard_webhooks_secret"] is True when a signing secret is set

webhooks = client.webhooks.list()
webhook = client.webhooks.get("whk_...")
updated = client.webhooks.update("whk_...", {"active": False})
client.webhooks.update("whk_...", {"authorization": None})  # remove the header
client.webhooks.update("whk_...", {"standard_webhooks_secret": None})  # stop signing
client.webhooks.delete("whk_...")

rotated = client.webhooks.rotate_secret("whk_...")
test = client.webhooks.test("whk_...")
deliveries = client.webhooks.list_deliveries("whk_...")
delivery = client.webhooks.get_delivery("whk_...", "dlv_...")
replay = client.webhooks.replay_delivery(
    "whk_...",
    "dlv_...",
    {"idempotency_key": "replay-dlv-123"},
)
```

### Status

```python
status = client.status.get()
```

## Pagination

List methods return a paginated response with cursor-based pagination:

```python
page = client.domains.list({"limit": 10})
print(page["data"])        # list of domains
print(page["pagination"])  # {"next_cursor": ..., "has_more": ...}

# Fetch next page
if page["pagination"]["has_more"]:
    next_page = client.domains.list({
        "cursor": page["pagination"]["next_cursor"],
        "limit": 10,
    })
```

Cursors are opaque and operation-specific. Never parse, modify, or fabricate them. Inbox and reply
queue cursors are bound to their mailbox, time window, sort, and filters.

Auto-pagination iterates through all pages automatically:

```python
for domain in client.domains.list_auto_paginating(limit=25):
    print(domain["name"])

# Async
async for domain in client.domains.list_auto_paginating(limit=25):
    print(domain["name"])
```

## Webhook Verification

Verify incoming webhook signatures without instantiating a client:

```python
from shipmail import verify_webhook, WebhookVerificationError

try:
    event = verify_webhook(raw_body, headers, webhook_secret)
    print(event["event_type"])  # e.g., "message.received"
    print(event["data"])
except WebhookVerificationError:
    # Invalid signature
    pass
```

## Error Handling

The SDK raises typed exceptions that map to API error responses:

```python
from shipmail import (
    ShipmailError,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ConflictError,
    InternalServerError,
    APIConnectionError,
)

try:
    client.domains.create({"name": ""})
except ValidationError as err:
    print(err)             # Error message
    print(err.details)     # Field-level validation errors
except RateLimitError as err:
    print(err.retry_after) # Seconds to wait
except ShipmailError as err:
    print(err.status)      # HTTP status code
    print(err.type)        # Error type string
    print(err.request_id)  # Request ID for support
    print(err.retryable)   # Whether the request can be retried
```

## Retries

The SDK retries eligible requests after connection errors, `429` responses, and retryable `5xx` errors. Automatic retries apply to `GET`, `HEAD`, and `OPTIONS`. Only POST, PATCH, and PUT mutations can retry, and they require an explicit `idempotency_key` method option or an `Idempotency-Key` header. Reuse the same key for the same operation. DELETE requests and errors marked non-retryable are never retried.

`max_retries` defaults to 2 (up to 3 total attempts) and must be a non-negative integer. Set it to 0 to disable retries.

A valid `Retry-After` header, in seconds or HTTP-date format, takes precedence over the rate-limit error body's `retry_after`. Otherwise, retries use exponential backoff with jitter. If the requested delay exceeds 60 seconds, the SDK returns the error without retrying automatically; schedule any later retry after that delay.

```python
client = Shipmail("sm_live_...", max_retries=0)  # Disable retries
```

## License

MIT
