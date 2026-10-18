# Deploying Orbit (free tier)

A personal-project deployment on free tiers:

| Piece | Host | Cost |
|---|---|---|
| Backend (Django) | **Render** (web service) | Free (sleeps when idle) |
| Database | **Neon** (Postgres) | Free |
| Frontend (React) | **Vercel** | Free |
| Search | Postgres fallback (no Elasticsearch) | Free |

> Elasticsearch is **not** used in this deployment. When `ELASTICSEARCH_HOST`
> is empty, search automatically uses a database backend. (To use real ES,
> point `ELASTICSEARCH_HOST` at a hosted cluster, e.g. Bonsai, and run
> `python manage.py search_index --rebuild`.)

The repo is already deploy-ready: `render.yaml`, `vercel.json`, env-driven
settings, gunicorn, whitenoise, and a `seed_demo` management command. You just
need to create the three free accounts and connect them.

---

## 1. Database — Neon (2 min)

1. Sign up at <https://neon.tech> and create a project.
2. Copy the **connection string** (the `postgresql://…` URL, pooled is fine).
   Keep it for step 2.

## 2. Backend — Render (5 min)

1. Sign up at <https://render.com> and connect your GitHub.
2. **New → Blueprint**, pick the **orbit** repo. Render reads `render.yaml`.
3. Fill the env vars it asks for (the `sync: false` ones):
   - `DATABASE_URL` = the Neon string from step 1
   - `ALLOWED_HOSTS` = `orbit-api.onrender.com` (your Render host, no scheme)
   - `CSRF_TRUSTED_ORIGINS` = `https://orbit-api.onrender.com`
   - `CORS_ALLOWED_ORIGINS` = `https://orbit-client.vercel.app` (your Vercel URL from step 3 — you can set this after)
   - `BASE_FRONTEND_URL` = `https://orbit-client.vercel.app`
   - `SECRET_KEY` is auto-generated; `DEBUG` is already `False`; `ELASTICSEARCH_HOST` is empty.
4. Deploy. The build runs `collectstatic` + `migrate` automatically.
5. Open the Render **Shell** and seed a login + sample data:
   ```bash
   cd orbit && python manage.py seed_demo --users 60 --posts 6
   ```
   This creates **demo / SyncoDemo123**.

> Free Render services spin down after ~15 min idle; the first request then
> takes ~30s to wake. Normal for a hobby project.

## 3. Frontend — Vercel (3 min)

1. Sign up at <https://vercel.com> and import the **orbit-client** repo.
2. Framework preset: **Create React App** (auto-detected). `vercel.json`
   handles client-side routing.
3. Add an **Environment Variable**:
   - `REACT_APP_API_BASE_URL` = `https://orbit-api.onrender.com` (your Render URL)
4. Deploy. Note the resulting URL (e.g. `https://orbit-client.vercel.app`).

## 4. Link them

Back in Render, make sure `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, and
`BASE_FRONTEND_URL` match your actual Vercel URL, then redeploy the backend.

Visit the Vercel URL and sign in with **demo / SyncoDemo123**. 🎉

---

## Notes
- **Branch**: deploy from whichever branch you push (this work is on
  `feat/social-feed`). Merge it into your default branch first if you prefer.
- **Email**: uses the console backend, so password-reset links appear in the
  Render logs rather than real emails — fine for a personal project.
- **Media**: posts are text-only today; if you add image uploads, wire up
  `django-storages` + Cloudflare R2 and set the S3 env vars.
- **Local dev** is unchanged: no env vars → SQLite + the Elasticsearch dev
  container on `:9201`.
