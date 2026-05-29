# API Reference

## Base URL

```
https://seo.yourdomain.com/api
```

## Authentication

API requests require a Bearer token:

```bash
curl -H "Authorization: Bearer $TOKEN"   https://seo.yourdomain.com/api/health
```

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{"status": "ok", "version": "0.1.0"}
```

### SEO Endpoints

All under the `/api/v1/seo` prefix:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/seo/audit` | Run a site audit |
| POST | `/api/v1/seo/keywords` | Keyword research & suggestions |
| POST | `/api/v1/seo/content/optimize` | Optimize content for a target keyword |
| POST | `/api/v1/seo/rankings/track` | Record + return rank-tracking history |

See the OpenAPI spec at `/openapi.json` for full request/response schemas.

## Error Handling

All errors follow the RFC 7807 Problem Details format:

```json
{
  "type": "https://api.dclawstack.io/errors/not-found",
  "title": "Resource not found",
  "status": 404,
  "detail": "The requested resource does not exist."
}
```
