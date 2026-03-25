# Blog Hunter 🏹

A world-class, premium Astro 6 blog platform optimized for speed, SEO, and zero-cost scaling on Cloudflare.

## 🚀 Quick Start

### 1. Environment Setup
Create a `.env` file with your credentials (see `.env.example`).

### 2. Deployment & Automation
We provide automated scripts to handle the heavy lifting:

- **Full Setup**: `python scripts/setup_cloudflare.py`
  - Creates Pages project.
  - Configures Web Analytics.
  - Sets GitHub Secrets.
  - **Automates DNS (CNAME)** on Cloudflare.

- **DNS Management**: `python scripts/manage_dns.py`
  - `--sync`: Ensures `blog.oriz.in` points to Cloudflare Pages.
  - `--list`: Lists all current DNS records on Cloudflare.
  - `--spaceship`: Verifies domain status on Spaceship Registry.

### 3. Local Development
```bash
pnpm install
pnpm dev
```

## 🛠️ Tech Stack
- **Framework**: Astro 6 (Static Output)
- **Styling**: Tailwind CSS 4
- **Formatting**: Biome.js (Strict)
- **Deployment**: Cloudflare Pages
- **DNS**: Cloudflare + Spaceship

## 📜 Engineering Standards
- **Strict TypeScript**: Type safety across the board.
- **SOLID Design**: Modular components and maintainable logic.
- **Performance**: Zero-JS impact tracking via Cloudflare Beacon.
