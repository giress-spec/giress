# Project notes

## What this is

A single static page (`index.html`): no build step, no backend, no dependencies,
no credentials. Car cards are rendered client-side from an inline `cars` array, and
the car photos plus the hero background are loaded from Unsplash in the browser
(so the preview needs outbound internet access to see the images).

## Running it in the Base44 sandbox

```bash
docker compose -f docker-compose.base44.yml up -d --build
```

- The `web` service runs `docker/serve.py` (Python stdlib) from the `python:3.12-slim`
  image and serves the repo bind-mounted at `/app` on host port 3000.
- It runs as root on purpose: the mounted repo root is only readable by root, so
  nginx's unprivileged worker gets 403 and cannot serve the files.
- The whole repo directory is mounted, not just `index.html`. A single-file bind
  mount keeps pointing at the old inode after an in-place rewrite (e.g. `sed -i`),
  so edits silently stop appearing.
- `docker/serve.py` refuses paths containing a dot-segment, keeping `.git` and
  `.base44` off the public preview, and sends `Cache-Control: no-store` so a refresh
  always shows the current source. New css/js/image files need no compose change.

## Verifying it works

```bash
curl -s http://localhost:3000/ | grep -c "NVP Motors"   # expect >0
docker compose -f docker-compose.base44.yml ps          # web should be healthy
```

The Compose healthcheck fetches `/` and requires the body to contain `NVP Motors`,
so it tests the real page rather than an open port.
