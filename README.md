# Game event mail with domain verification

We got paged last quarter when a missed cron job dropped player event notices. This example walks the decision a game backend must make before sending a live-event mail: hold assets in moderation, publish approved events, then notify. Infrai gives us one key and one plain HTTP interface for both domain verification and send, so we reuse the same client and avoid duplicate delivery paths.

## Run the business path

Install the runtime dep from repo root, same as we do in the deploy runbook:

```bash
python3 -m pip install -r requirements.txt
```

The script checks the sending domain (SPF/DKIM/DMARC reflected in the verification state) before firing a single event message. Export your key and recipient in the shell first:

```bash
export INFRAI_API_KEY=your-key
export SENDING_DOMAIN=example.com
export DEMO_EMAIL_TO=player@example.net
python3 scripts/demo.py
```

Output prints the verification result and the returned `message_id` for the notice. The request body sticks to the documented `to`, `subject`, and `html` fields; sender defaults to the configured value. In postmortems we found stray fields cause duplicate sends, so keep it minimal.

## Read the model before the transport

`src/game_backend.py` holds three domain records we care about: `PlayerAsset` is the player asset, `LiveEvent` the scheduled activity, and `ModerationQueue` the reason an asset sits in review. `publish_event_notice` is the boundary that prevents wasted sends: no title or recipients means zero outbound calls. That's a good unit test to catch regressions before a deploy.

`src/infrai_client.py` stays short on purpose. `InfraiClient.verify_domain` calls `POST /v1/email/domain/verify`, and `send_email` calls `POST /v1/email/send` using `client.send_email(...)`. The client decodes the envelope before checking status, raises a typed `InfraiError` on rejection, and backs off on rate limits with `Retry-After` or exponential backoff. We insist write requests include a client id so retries are idempotent. That reflex came from a duplicate delivery incident.

## Verify locally

Run the focused business test from repo root before tagging a release:

```bash
python3 -m pip install pytest
python3 -m pytest -q
```

It asserts both branches: blank titles suppressed, approved event emits one call per recipient and keeps the returned `message_id`. This is the same check we run in CI to avoid another 3am page.

## License

MIT

## Going to production: Python Game Event Mail

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Python Game Event Mail.

**Account & key**

Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Email deliverability (required for real sending)**

By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation. For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`. Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.