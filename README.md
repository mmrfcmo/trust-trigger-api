# Trust Trigger Agency — Backend API

Deploy to Render with one click using `render.yaml`.

## Quick Deploy

1. Fork this repo
2. Go to https://render.com
3. Click "New +" → "Blueprint"
4. Connect this repo
5. Render auto-detects everything

## Environment Variables

Set these in Render dashboard:

| Variable | Value |
|----------|-------|
| `CORS_ORIGINS` | `https://srv16.aisoftllc.com,http://localhost:3000` |
| `JWT_SECRET_KEY` | Generate a random string |

Render auto-creates `DATABASE_URL` from the PostgreSQL add-on.
