# Custom Domain Setup Guide for SF-Bench

This guide explains how to set up a custom domain for SF-Bench to improve SEO and domain authority.

## Why Custom Domain?

- Higher domain authority than GitHub Pages subdomains
- Better SEO rankings
- Professional appearance
- Easier to remember and share

## Recommended Domains

- `sf-bench.com` (primary recommendation)
- `sfbench.dev` (alternative)
- `sfbenchmark.com` (alternative)

## Setup Steps

### 1. Purchase Domain

Purchase your chosen domain from a registrar (Namecheap, Google Domains, etc.)

### 2. Configure GitHub Pages Custom Domain

1. Go to repository Settings → Pages
2. Under "Custom domain", enter your domain (e.g., `sf-bench.com`)
3. GitHub will automatically create a `CNAME` file

### 3. Configure DNS

Add these DNS records at your domain registrar:

**For apex domain (sf-bench.com):**
```
Type: A
Name: @
Value: 185.199.108.153
Value: 185.199.109.153
Value: 185.199.110.153
Value: 185.199.111.153
```

**For www subdomain (www.sf-bench.com):**
```
Type: CNAME
Name: www
Value: yasarshaikh.github.io
```

### 4. Update Jekyll Configuration

After DNS propagates (24-48 hours), update `docs/_config.yml`:

```yaml
url: https://sf-bench.com
baseurl: ""
```

### 5. Verify in Google Search Console

1. Add property: `https://sf-bench.com`
2. Verify ownership (DNS or HTML file method)
3. Submit sitemap: `https://sf-bench.com/sitemap.xml`

### 6. Set Up Redirects

GitHub Pages will automatically redirect `yasarshaikh.github.io/SF-bench/*` to your custom domain.

## SSL Certificate

GitHub Pages automatically provides SSL certificates for custom domains. Enable "Enforce HTTPS" in repository Settings → Pages.

## Testing

After setup, verify:
- `https://sf-bench.com` loads correctly
- `https://www.sf-bench.com` redirects to apex domain
- SSL certificate is valid
- All internal links work

## Notes

- DNS propagation can take 24-48 hours
- Keep the `CNAME` file in repository root (GitHub manages this)
- Update all documentation links after domain change
- Submit new sitemap to Google Search Console
