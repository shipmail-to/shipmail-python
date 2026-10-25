# Changelog

## 0.6.6 (2026-10-23)


### Features

* add scoped agent mail review and reliable reply workflows
* **api:** one-off booking links in the API, SDKs, CLI and MCP
* **billing:** let trials test every feature with clear limits
* composer code formatting, paragraph spacing and the reply-draft lifecycle API
* domain health API, MCP tool and shareable health reports
* **newsletters:** AI content check with human review, and subscriber domain re-check
* **newsletters:** reader engagement: tiers, engaged first, send to more, list cleanup, subject tests
* **newsletters:** summary email, subscriber page, issue timing and where an issue goes
* **newsletters:** website settings polish, and call a send a newsletter in the app and a post on the website
* **newsletters:** welcome sequences, newsletter websites, webmail button and Markdown input


### Bug Fixes

* **sending:** suppression scopes, expiring soft-bounce pauses, signup bot protection

## 0.6.5 (2026-10-14)


### Features

* act on AgentMail's agent eval findings
* inbox search filters and webhook sender allowlist for agents
* **newsletters:** link analytics for email and the Atom feed
* reply_text and sender authentication for agents

## 0.6.4 (2026-10-10)


### Features

* **rules:** run rules on the inbox, Recipient contains, keep typed values
* **webhooks:** authenticate deliveries with an Authorization header or a Standard Webhooks secret
* **webhooks:** message.delayed for deferred deliveries

## 0.6.3 (2026-10-06)


### Features

* **agents:** hand Shipmail setup to an agent, owner pays
* forward mail for a selected alias

## 0.6.2 (2026-10-03)


### Features

* **api:** member roles and mailbox access in the API, SDKs, CLI and MCP (R3b-3)
* **calendar:** add reliable multi-calendar scheduling workspace
* **newsletters:** optional open and click tracking, clearer import drop zone

## 0.6.1 (2026-10-01)


### Features

* **events:** subscriber added and newsletter sent

## 0.6.0 (2026-10-01)


### ⚠ BREAKING CHANGES

* remove the partner program

### Features

* **events:** reply overdue, needs action, event starting and booking created
* **scheduled-send:** cutover tooling, legacy import, operator resolution and draft revisions (step 4b-2)


### Code Refactoring

* remove the partner program

## 0.5.10 (2026-09-28)


### Features

* **admin:** abuse cases with lock, clear and terminate
* **webhooks:** limit a webhook to specific mailboxes or domains


### Bug Fixes

* package security and drift fixes from the audit

## 0.5.9 (2026-09-26)


### Features

* **newsletters:** add image alignment controls

## 0.5.8 (2026-09-24)


### Features

* **api:** save new-message drafts from the API and MCP

## 0.5.7 (2026-09-24)


### Documentation

* **sdk:** explain transactional senders in the from field

## 0.5.6 (2026-09-12)


### Bug Fixes

* **api:** accept RFC 5322 name-addr in the send from field

## 0.5.5 (2026-09-11)


### Bug Fixes

* **import:** skip a source folder the server refuses instead of failing the import

## 0.5.4 (2026-09-11)


### Features

* **api:** export completion webhooks and per-mailbox export quota

## 0.5.3 (2026-09-11)


### Features

* **api:** add conversation_id and deprecate thread_id

## 0.5.2 (2026-09-04)


### Features

* **newsletters:** add self-service migration center

## 0.5.1 (2026-09-04)


### Bug Fixes

* **newsletters:** load media with unlimited storage

## 0.5.0 (2026-09-03)


### ⚠ BREAKING CHANGES


### Features

* **dashboard:** polish UX and add developer workspace


### Bug Fixes

* **messages:** resolve senders by full address

## 0.4.21 (2026-08-31)


### Features

* **mailboxes:** add sender-filtered forwarding

## 0.4.20 (2026-08-20)


### Features

* **mailboxes:** add mailbox delivery routing

## 0.4.19 (2026-08-19)


### Features

* **inbox:** recover away conversations and expose members over the API
* **webhooks:** emit member.away_updated

## 0.4.18 (2026-08-17)


### Bug Fixes

* **newsletters:** allow deleting domains used by history

## 0.4.17 (2026-08-15)


### Features

* retain and restore uploaded import sources


### Bug Fixes

* retain and resume uploaded imports

## 0.4.16 (2026-08-11)


### Bug Fixes

* **imports:** stabilize large browser uploads

## 0.4.15 (2026-08-10)


### Bug Fixes

* **newsletters:** restore production media uploads

## 0.4.14 (2026-08-08)


### Features

* **newsletters:** accept inline HTML in block prose
* **newsletters:** add secure MCP media uploads

## 0.4.13 (2026-08-03)


### Features

* **calendar:** localize invitation emails

## 0.4.12 (2026-08-02)


### Features

* **api:** add public automations API

## 0.4.11 (2026-07-30)


### Features

* **status:** launch independent Cloudflare status platform

## 0.4.10 (2026-07-29)


### Bug Fixes

* **mcp:** start the server when capabilities cannot be fetched

## 0.4.9 (2026-07-29)


### Features

* **api:** expose inbound authentication results to clients

## 0.4.8 (2026-07-29)


### Features

* **api:** add message analytics sync endpoint

## 0.4.7 (2026-07-29)


### Features

* **sdk:** support multiple newsletter sender identities

## 0.4.6 (2026-07-29)


### Bug Fixes

* **assistant:** smarter reply triage, remove unused needs_reply webhook

## 0.4.5 (2026-07-29)


### Features

* **api:** expose feed canonical URL and entry limit

## 0.4.4 (2026-07-28)


### Features

* **newsletters:** add safe feed token lifecycle

## 0.4.3 (2026-07-27)


### Features

* **newsletters:** publish an audience as an opt-in Atom feed

## 0.4.2 (2026-07-27)


### Features

* **newsletters:** plain styling mode and code-view round-trip fixes

## 0.4.1 (2026-07-27)


### Features

* **assistant:** manage inbox rules by name and expose rule disposition in the API

## 0.4.0 (2026-07-25)


### ⚠ BREAKING CHANGES

* **mcp:** add capability-complete connector controls

### Features

* **mcp:** add capability-complete connector controls

## 0.3.0 (2026-07-23)


### ⚠ BREAKING CHANGES

* **assistant:** replace Agent OS with admin-only AI assistant

### Features

* **assistant:** replace Agent OS with admin-only AI assistant

## 0.2.3 (2026-07-20)


### Features

* **api:** add agent-safe reply queue workflows

## 0.2.2 (2026-07-19)


### Features

* **newsletters:** add team collaboration

## 0.2.1 (2026-07-17)


### Features

* **import:** add Infomaniak, OVHcloud, and Gandi migrations

## 0.2.0 (2026-07-16)


### ⚠ BREAKING CHANGES


### Features

* **partner:** complete embedded mailbox credentials

## 0.1.20 (2026-07-14)


### Features

* **api:** expose conferencing_provider on booking pages
* **partner:** add invite-only reseller beta

## 0.1.19 (2026-07-13)


### Features

* add api mailbox infrastructure foundations
* **api:** automate domain and mailbox provisioning
* **mailboxes:** add verified forwarding and partner pilot

## 0.1.18 (2026-07-12)


### Features

* **calendar:** complete launch follow-ups
* **webhooks:** add delivery detail and failed-delivery replay
* **sandbox:** add isolated test sends, synthetic outcomes, and fake inbound messages
* **mailboxes:** add suspend and resume methods with independent suspension reasons

## 0.1.17 (2026-07-09)


### Documentation

* full documentation overhaul + managed_by vendor-leak fix

## 0.1.16 (2026-07-07)


### Features

* calendar — events, invites, booking links, API, conferencing

## 0.1.15 (2026-07-06)


### Features

* add newsletter audience resubscribe

## 0.1.14 (2026-07-06)


### Bug Fixes

* **newsletters:** tune URL policy for media-rich sends

## 0.1.13 (2026-07-05)


### Features

* **newsletters:** block insert seams, hover-reachable rail, and button alignment

## 0.1.12 (2026-07-05)


### Features

* **newsletters:** full-page block editor with blocks-first API

## 0.1.11 (2026-07-03)


### Features

* **newsletters:** add API and SDK support

## 0.1.10 (2026-07-02)


### Features

* programmatic audience sync for broadcasts (API, SDK, MCP, CLI)

## 0.1.9 (2026-06-14)


### Bug Fixes

* expose inbox message bodies in API

## 0.1.8 (2026-06-13)


### Features

* mailbox import from Gmail, Outlook, and any IMAP provider

## 0.1.7 (2026-05-17)


### Features

* SEO metadata, comparison tables, and Shipmail brand consistency

## 0.1.6 (2026-05-15)


### Bug Fixes

* **billing:** atomic trial activation + 24h DNS reminder

## 0.1.5 (2026-03-25)


### Bug Fixes

* sync SDK types and OpenAPI spec with actual API responses

## 0.1.4 (2026-03-17)


### Features

* add attachment support to API send endpoint

## 0.1.3 (2026-03-15)


### Features

* improve API developer experience

## 0.1.2 (2026-03-14)


### Features

* auto-reply / out-of-office vacation responder

## 0.1.1 (2026-03-14)


### Features

* Python SDK with sync and async clients

## 0.1.0 (Unreleased)

Initial release of the Shipmail Python SDK.

- Sync client (`Shipmail`) and async client (`AsyncShipmail`)
- All API resources: Domains, Mailboxes, Messages, Threads, Webhooks, Suppressions, Status
- Cursor-based auto-pagination (sync and async iterators)
- Webhook signature verification with HMAC-SHA256
- Typed error hierarchy matching API error responses
- Automatic retries with exponential backoff on 5xx and 429 responses
- Context manager support for client lifecycle
- PEP 561 typed package
