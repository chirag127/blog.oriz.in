# ============================================
# CLOUDFLARE DEPLOYMENT CONFIGURATION
# ============================================
# These secrets must be set in your GitHub repo:
# Settings → Secrets and variables → Actions
#
# Required:
#   CLOUDFLARE_ACCOUNT_ID   - Your Cloudflare account ID
#   CLOUDFLARE_API_TOKEN    - Cloudflare API token with Pages permissions
#
# Optional (Analytics):
#   PUBLIC_GA_ID            - Google Analytics 4 measurement ID (G-XXXXXXXXXX)
#   PUBLIC_CLARITY_ID       - Microsoft Clarity project ID
#   PUBLIC_POSTHOG_KEY      - PostHog API key (phc_xxxxx)
#   PUBLIC_CF_BEACON        - Cloudflare Web Analytics beacon token
# ============================================

# --------------------------------------------
# HOW TO GET CLOUDFLARE_ACCOUNT_ID:
# --------------------------------------------
# 1. Login to https://dash.cloudflare.com
# 2. Look at the URL: dash.cloudflare.com/<ACCOUNT_ID>
# 3. Or go to any domain → Overview → Account ID on the right sidebar
# --------------------------------------------

# --------------------------------------------
# HOW TO GET CLOUDFLARE_API_TOKEN:
# --------------------------------------------
# 1. Go to https://dash.cloudflare.com/profile/api-tokens
# 2. Click "Create Token"
# 3. Use the "Edit Cloudflare Workers" template
#    OR create a custom token with these permissions:
#      - Account > Cloudflare Pages > Edit
#      - Zone > Zone > Read (if using custom domain)
# 4. Click "Continue to summary" → "Create Token"
# 5. Copy the token (you won't see it again!)
# --------------------------------------------

# --------------------------------------------
# HOW TO SETUP CLOUDFLARE PAGES PROJECT:
# --------------------------------------------
# Option A: Via Cloudflare Dashboard (Recommended)
#   1. Go to https://dash.cloudflare.com → Workers & Pages
#   2. Click "Create application" → "Pages" → "Connect to Git"
#   3. Select your GitHub repo: chirag127/blog-hunter
#   4. Build settings:
#      - Framework preset: Astro
#      - Build command: npm run build
#      - Build output directory: dist
#      - Root directory: /
#   5. Environment variables (add these):
#      - PUBLIC_GA_ID = (your GA4 ID)
#      - PUBLIC_CLARITY_ID = (your Clarity ID)
#      - PUBLIC_CF_BEACON = (your beacon token)
#   6. Click "Save and Deploy"
#
# Option B: Via Wrangler CLI (this workflow)
#   The GitHub Actions workflow handles deployment automatically.
#   Just set the required secrets in your repo settings.
# --------------------------------------------

# --------------------------------------------
# HOW TO SETUP CUSTOM DOMAIN (blog.oriz.in):
# --------------------------------------------
# Since oriz.in is already on Cloudflare:
#   1. Go to Workers & Pages → blog-hunter project
#   2. Go to "Custom domains" tab
#   3. Click "Set up a custom domain"
#   4. Enter: blog.oriz.in
#   5. Cloudflare will auto-configure DNS (since domain is on CF)
#   6. SSL certificate is auto-provisioned
#
# DNS Record (auto-created by Cloudflare):
#   Type: CNAME
#   Name: blog
#   Content: blog-hunter.pages.dev
#   Proxy: Enabled (orange cloud)
# --------------------------------------------
