#!/usr/bin/env python3
"""
DNS Management Automation
=========================
Manages DNS records for oriz.in via Cloudflare and Spaceship APIs.
Ensures blog.oriz.in points to blog.pages.dev.

Usage: 
  python scripts/manage_dns.py --sync
  python scripts/manage_dns.py --list
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print(f"ERROR: .env not found at {env_path}")
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip().strip('"').strip("'")

load_env()

# Config
DOMAIN = "oriz.in"
SUBDOMAIN = "blog"
PAGES_TARGET = "blog-ehu.pages.dev"

# Cloudflare
CF_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CF_EMAIL = os.environ.get("CLOUDFLARE_EMAIL")
CF_GLOBAL_KEY = os.environ.get("CLOUDFLARE_GLOBAL_API_KEY")
CF_API_BASE = "https://api.cloudflare.com/client/v4"

# Spaceship
S_KEY = os.environ.get("SPACESHIP_API_KEY")
S_SECRET = os.environ.get("SPACESHIP_API_SECRET")
S_URL = os.environ.get("SPACESHIP_API_URL", "https://spaceship.dev/api/v1")

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
        return {"success": False, "error": e.read().decode(), "code": e.code}

def spaceship_request(method, endpoint, data=None):
    url = f"{S_URL}{endpoint}"
    headers = {
        "X-API-Key": S_KEY,
        "X-API-Secret": S_SECRET,
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"success": False, "error": e.read().decode(), "code": e.code}

def get_cf_zone_id(domain):
    res = cf_request("GET", f"/zones?name={domain}")
    if res.get("success") and res.get("result"):
        return res["result"][0]["id"]
    return None

def sync_dns():
    print(f"[*] Syncing DNS for {SUBDOMAIN}.{DOMAIN}...")
    
    zone_id = get_cf_zone_id(DOMAIN)
    if not zone_id:
        print(f"  [ERROR] Zone {DOMAIN} not found on Cloudflare")
        return

    # List records to find existing
    records = cf_request("GET", f"/zones/{zone_id}/dns_records?name={SUBDOMAIN}.{DOMAIN}")
    existing_id = None
    if records.get("success") and records.get("result"):
        for r in records["result"]:
            if r["type"] == "CNAME":
                existing_id = r["id"]
                if r["content"] == PAGES_TARGET:
                    print(f"  [OK] CNAME for {SUBDOMAIN} already points to {PAGES_TARGET}")
                    return

    data = {
        "type": "CNAME",
        "name": SUBDOMAIN,
        "content": PAGES_TARGET,
        "ttl": 1,
        "proxied": True
    }

    if existing_id:
        print(f"  [*] Updating existing CNAME record...")
        res = cf_request("PATCH", f"/zones/{zone_id}/dns_records/{existing_id}", data)
    else:
        print(f"  [*] Creating new CNAME record...")
        res = cf_request("POST", f"/zones/{zone_id}/dns_records", data)

    if res.get("success"):
        print(f"  [OK] Successfully synchronized {SUBDOMAIN}.{DOMAIN} -> {PAGES_TARGET}")
    else:
        print(f"  [ERROR] Failed to sync DNS: {res.get('error')}")

def list_dns():
    print(f"[*] Listing DNS records for {DOMAIN} on Cloudflare...")
    zone_id = get_cf_zone_id(DOMAIN)
    if not zone_id: return
    res = cf_request("GET", f"/zones/{zone_id}/dns_records?per_page=100")
    if res.get("success") and res.get("result"):
        print(f"{'TYPE':<8} {'NAME':<30} {'CONTENT':<40}")
        print("-" * 80)
        for r in res["result"]:
            name = r["name"]
            if name.endswith(f".{DOMAIN}"): name = name[:-len(DOMAIN)-1]
            if name == DOMAIN: name = "@"
            print(f"{r['type']:<8} {name:<30} {r['content']:<40}")

def check_spaceship():
    print(f"[*] Checking {DOMAIN} on Spaceship Registry...")
    # Using the path observed in docs or common pattern
    res = spaceship_request("GET", f"/domains/{DOMAIN}")
    if isinstance(res, dict) and "name" in res:
        print(f"  [OK] Domain: {res['name']}")
        print(f"  [OK] Status: {res.get('lifecycleStatus')}")
        ns = res.get("nameservers", {})
        print(f"  [OK] NS Provider: {ns.get('provider')}")
        if ns.get("hosts"):
            print(f"  [OK] NS Hosts: {', '.join(ns['hosts'])}")
    else:
        print(f"  [WARN] Could not retrieve domain info from Spaceship (Code: {res.get('code')})")

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--list" in args:
        list_dns()
    elif "--sync" in args:
        sync_dns()
    elif "--spaceship" in args:
        check_spaceship()
    else:
        # Default behavior: sync
        sync_dns()
        check_spaceship()
