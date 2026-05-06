# Troubleshooting

Common issues and solutions for DClaw SEO.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-seo

# Check logs
kubectl logs -n dclaw-seo deployment/dclaw-seo-backend

# Check database
kubectl get clusters -n dclaw-seo
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
