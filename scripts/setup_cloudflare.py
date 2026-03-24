#!/usr/bin/env python3
"""
Cloudflare Pages + GitHub Setup Automation
==========================================
Automates:
1. Creates Cloudflare Pages project
2. Sets custom domain (blog.oriz.in)
3. Creates Cloudflare Web Analytics site
4. Sets GitHub Actions secrets

Usage: python scripts/setup_cloudflare.py
"""

import os
import sys
import json
import re
import subprocess
import urllib.request
import urllib.error
from pathlib import Path


def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print("ERROR: .env file not found at", env_path)
        sys.exit(1)
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value:
                    os.environ[key] = value


load_env()

CF_ACCOUNT_ID = os.environ["CLOUDFLARE_ACCOUNT_ID"]
CF_EMAIL = os.environ["CLOUDFLARE_EMAIL"]
CF_GLOBAL_KEY = os.environ["CLOUDFLARE_GLOBAL_API_KEY"]
CF_API_BASE = "https://api.cloudflare.com/client/v4"

PROJECT_NAME = "blog"
CUSTOM_DOMAIN = "blog.oriz.in"
GITHUB_REPO = "chirag127/blog-hunter"


def cf_request(method, endpoint, data=None):
    url = f"{CF_API_BASE}{endpoint}"
    headers = {
        "X-Auth-Email": CF_EMAIL,
        "X-Auth-Key": CF_GLOBAL_KEY,
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
            if error_json.get("errors"):
                for err in error_json["errors"]:
                    code = err.get("code", 0)
                    msg = err.get("message", "")
                    if code in (10009, 8000006, 8000011):
                        return {"success": True, "already_exists": True}
                    print(f"  API Error {code}: {msg}")
        except (json.JSONDecodeError, KeyError):
            pass
        if e.code in (409, 400):
            # Check if it's "already exists"
            if "already" in error_body.lower() or "exist" in error_body.lower():
                return {"success": True, "already_exists": True}
        return {
            "success": False,
            "errors": [{"message": error_body[:300]}],
            "status_code": e.code,
        }


def github_set_secret(repo, secret_name, secret_value):
    try:
        result = subprocess.run(
            [
                "gh",
                "secret",
                "set",
                secret_name,
                "--body",
                secret_value,
                "--repo",
                repo,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"  [OK] GitHub secret '{secret_name}' set")
        else:
            print(
                f"  [WARN] GitHub secret '{secret_name}': {result.stderr.strip()[:100]}"
            )
    except FileNotFoundError:
        print(f"  [SKIP] 'gh' CLI not found for '{secret_name}'")


def create_cf_api_token():
    print("\n[*] Generating scoped Cloudflare API token...")
    data = {
        "name": f"github-actions-{PROJECT_NAME}",
        "policies": [
            {
                "effect": "allow",
                "resources": {f"com.cloudflare.api.account.{CF_ACCOUNT_ID}": "*"},
                "permission_groups": [
                    {"id": "e086da7e217949db9b3b03e0529f4c88"},
                    {"id": "c8fed203ed3043cba015a93ad1616f1f"},
                ],
            }
        ],
    }
    result = cf_request("POST", "/user/tokens", data)
    if result.get("success") and result.get("result"):
        token = result["result"].get("value", "")
        if token:
            print(f"  [OK] Token created: {token[:12]}...")
            return token
    print("  [WARN] Could not auto-create token")
    return None


def main():
    print("=" * 60)
    print("  CLOUDFLARE PAGES SETUP - blog.oriz.in")
    print("=" * 60)
    print(f"\n  Account ID: {CF_ACCOUNT_ID}")
    print(f"  Email:      {CF_EMAIL}")
    print(f"  Project:    {PROJECT_NAME}")
    print(f"  Domain:     {CUSTOM_DOMAIN}")
    print(f"  GitHub:     {GITHUB_REPO}")

    # Step 1: Create Pages Project
    print(f"\n[1/5] Creating Cloudflare Pages project...")
    existing = cf_request(
        "GET", f"/accounts/{CF_ACCOUNT_ID}/pages/projects/{PROJECT_NAME}"
    )
    if existing.get("success") and existing.get("result"):
        proj = existing["result"]
        subdomain = proj.get("subdomain", PROJECT_NAME)
        print(f"  [OK] Project exists: https://{subdomain}.pages.dev")
    else:
        data = {
            "name": PROJECT_NAME,
            "build_config": {
                "build_command": "npm run build",
                "destination_dir": "dist",
                "root_dir": "/",
            },
            "source": {
                "type": "github",
                "config": {
                    "owner": "chirag127",
                    "repo_name": "blog-hunter",
                    "production_branch": "main",
                },
            },
            "deployment_configs": {
                "production": {
                    "compatibility_date": "2026-03-24",
                },
            },
        }
        result = cf_request("POST", f"/accounts/{CF_ACCOUNT_ID}/pages/projects", data)
        if result.get("success"):
            proj = result.get("result", {})
            subdomain = proj.get("subdomain", PROJECT_NAME)
            print(f"  [OK] Project created: https://{subdomain}.pages.dev")
        elif result.get("already_exists"):
            print(f"  [OK] Project already exists")
        else:
            print(f"  [WARN] Project creation issue (may already exist)")

    # Step 2: Custom Domain
    print(f"\n[2/5] Setting up custom domain {CUSTOM_DOMAIN}...")
    domain_data = {"name": CUSTOM_DOMAIN}
    result = cf_request(
        "POST",
        f"/accounts/{CF_ACCOUNT_ID}/pages/projects/{PROJECT_NAME}/domains",
        domain_data,
    )
    if result.get("success"):
        print(f"  [OK] Custom domain '{CUSTOM_DOMAIN}' added")
    elif result.get("already_exists"):
        print(f"  [OK] Custom domain already configured")
    else:
        print(f"  [WARN] Domain setup issue (may already be configured)")

    # Step 3: Web Analytics
    print(f"\n[3/5] Setting up Cloudflare Web Analytics...")
    beacon_token = ""

    # Try RUM site_info endpoint
    wa_data = {"name": CUSTOM_DOMAIN, "auto_install": True}
    wa_result = cf_request("POST", f"/accounts/{CF_ACCOUNT_ID}/rum/site_info", wa_data)

    if wa_result.get("success") and wa_result.get("result"):
        beacon_token = wa_result["result"].get("token", "")
        if beacon_token:
            print(f"  [OK] Web Analytics token: {beacon_token[:10]}...")
    else:
        # Try listing existing WA sites
        list_result = cf_request("GET", f"/accounts/{CF_ACCOUNT_ID}/rum/site_info")
        if list_result.get("success") and list_result.get("result"):
            sites = (
                list_result["result"] if isinstance(list_result["result"], list) else []
            )
            for site in sites:
                if isinstance(site, dict) and CUSTOM_DOMAIN in str(
                    site.get("host", "")
                ):
                    beacon_token = site.get("token", "")
                    if beacon_token:
                        print(f"  [OK] Found existing WA token: {beacon_token[:10]}...")
                        break

        if not beacon_token:
            print(f"  [INFO] Create Web Analytics manually:")
            print(f"         Cloudflare Dashboard > Web Analytics > Add site")
            print(f"         Enter: {CUSTOM_DOMAIN}")

    # Step 4: GitHub Secrets
    print(f"\n[4/5] Setting GitHub secrets...")
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)

        github_set_secret(GITHUB_REPO, "CLOUDFLARE_ACCOUNT_ID", CF_ACCOUNT_ID)

        scoped_token = create_cf_api_token()
        if scoped_token:
            github_set_secret(GITHUB_REPO, "CLOUDFLARE_API_TOKEN", scoped_token)
        else:
            print("  [INFO] Set CLOUDFLARE_API_TOKEN manually:")
            print("         dash.cloudflare.com/profile/api-tokens")

        if beacon_token:
            github_set_secret(GITHUB_REPO, "PUBLIC_CF_BEACON", beacon_token)

    except (FileNotFoundError, subprocess.CalledProcessError):
        print("  [SKIP] 'gh' CLI not installed. Set secrets manually:")
        print(f"         gh secret set CLOUDFLARE_ACCOUNT_ID --body '{CF_ACCOUNT_ID}'")
        print(f"         gh secret set CLOUDFLARE_API_TOKEN --body 'YOUR_TOKEN'")
        if beacon_token:
            print(f"         gh secret set PUBLIC_CF_BEACON --body '{beacon_token}'")

    # Step 5: Deploy via wrangler
    print(f"\n[5/5] Deploying...")
    project_root = str(Path(__file__).parent.parent)
    try:
        # Build first
        print("  Building...")
        build = subprocess.run(
            ["npm", "run", "build"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=project_root,
        )
        if build.returncode == 0:
            print("  [OK] Build successful")
            # Deploy
            print("  Deploying to Cloudflare Pages...")
            env = os.environ.copy()
            deploy = subprocess.run(
                [
                    "npx",
                    "wrangler",
                    "pages",
                    "deploy",
                    "dist",
                    "--project-name",
                    PROJECT_NAME,
                ],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=project_root,
                env=env,
            )
            if deploy.returncode == 0:
                print("  [OK] Deployed!")
                if deploy.stdout:
                    for line in deploy.stdout.strip().split("\n")[-5:]:
                        print(f"       {line}")
            else:
                print(f"  [INFO] Deploy via: git push origin main")
                if deploy.stderr:
                    print(f"         {deploy.stderr[:200]}")
        else:
            print(f"  [WARN] Build issue, push to GitHub to trigger CI/CD")
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"  [INFO] Push to GitHub to deploy: git push origin main")

    # Summary
    print("\n" + "=" * 60)
    print("  SETUP COMPLETE")
    print("=" * 60)
    print(f"\n  Site:     https://{CUSTOM_DOMAIN}")
    print(f"  CMS:      https://{CUSTOM_DOMAIN}/admin")
    print(f"  Guide:    https://{CUSTOM_DOMAIN}/cms-guide")
    print(f"  RSS:      https://{CUSTOM_DOMAIN}/rss.xml")
    print(f"\n  Deploy:   git push origin main")
    print("=" * 60)


if __name__ == "__main__":
    main()
