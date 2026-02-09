# Complete Setup Guide: Innera Counselling Website

**Last Updated:** February 9, 2026

This guide covers the complete setup of the Innera website using the current simplified stack.

## Table of Contents
1. [Current Architecture](#current-architecture)
2. [Prerequisites](#prerequisites)
3. [Initial Linux Setup](#initial-linux-setup)
4. [Tailscale VPN Setup (SSH Access)](#tailscale-vpn-setup)
5. [Install Required Software](#install-required-software)
6. [Deploy the Website](#deploy-the-website)
7. [Cloudflare Tunnel Setup](#cloudflare-tunnel-setup)
8. [Domain Configuration](#domain-configuration)
9. [Management & Maintenance](#management--maintenance)
10. [Security Best Practices](#security-best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Current Architecture

**Stack Overview:**
```
Visitor → Cloudflare CDN → Cloudflare Tunnel → FastAPI (port 8000)
You → Tailscale VPN → SSH (port 2222) → Server Management
```

**What We're Using:**
- ✅ **FastAPI** - Python web framework (direct exposure on port 8000)
- ✅ **Docker** - Containerization (single container)
- ✅ **Cloudflare Tunnel** - Handles SSL and public access
- ✅ **Tailscale VPN** - Secure SSH admin access only
- ✅ **GitHub** - Version control

**What We're NOT Using:**
- ❌ **Caddy** - Removed (Cloudflare handles SSL)
- ❌ **Nginx** - Never used
- ❌ **Port Forwarding** - Not needed with Cloudflare Tunnel
- ❌ **Let's Encrypt** - Cloudflare provides SSL automatically

**Why This Setup:**
- No exposed ports (CGNAT-friendly)
- Cloudflare handles DDoS protection
- Automatic SSL certificates
- Secure admin access via Tailscale
- Simple single-container deployment

---

## Prerequisites

- **Linux N100 machine** running Ubuntu 24.04
- **Home internet connection** (CGNAT is fine!)
- **Domain name** - inneracounselling.ca (Porkbun)
- **Cloudflare account** (free)
- **Tailscale account** (free)
- **Mac** for initial setup

---

## Initial Linux Setup

### 1. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Disable Auto-Sleep

```bash
# Prevent server from going to sleep
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

### 3. Set Static IP (Recommended)

On your router, reserve a static IP for the Linux machine:
- IP: 192.168.4.43
- MAC Address: b0:ac:82:59:44:b1

### 4. Create User (if needed)

```bash
# If user doesn't exist
sudo adduser yusuf
sudo usermod -aG sudo yusuf
```

---

## Tailscale VPN Setup

Tailscale provides secure SSH access without exposing ports to the internet.

### 1. Install Tailscale on Linux Machine

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Follow the link to authenticate in browser.

### 2. Configure SSH

Edit SSH config:
```bash
sudo nano /etc/ssh/sshd_config
```

Add/modify:
```bash
Port 2222
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication yes  # Will disable after key setup
AllowUsers yusuf
```

Restart SSH:
```bash
sudo systemctl restart sshd
sudo systemctl enable sshd
```

### 3. Install Tailscale on Mac

Download from: https://tailscale.com/download/mac

Or via Homebrew:
```bash
brew install --cask tailscale
```

Launch Tailscale and log in.

### 4. Get Tailscale IP

On Linux machine:
```bash
tailscale status
# Note the IP: 100.120.234.126
```

### 5. Setup SSH Keys from Mac

Generate key (if needed):
```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

Copy key to server:
```bash
ssh-copy-id -p 2222 yusuf@100.120.234.126
```

Test connection:
```bash
ssh -p 2222 yusuf@100.120.234.126
```

### 6. Disable Password SSH (After Testing Keys)

```bash
sudo nano /etc/ssh/sshd_config
```

Change:
```bash
PasswordAuthentication no
```

Restart:
```bash
sudo systemctl restart sshd
```

---

## Install Required Software

SSH to server:
```bash
ssh -p 2222 yusuf@100.120.234.126
```

### 1. Install Docker

```bash
# Add Docker's GPG key
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in
exit
ssh -p 2222 yusuf@100.120.234.126

# Test
docker ps
```

### 2. Install Git

```bash
sudo apt install git -y
```

### 3. Install Monitoring Tools

```bash
sudo apt install htop ncdu net-tools apache2-utils -y
```

### 4. Install Cloudflared

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
rm cloudflared.deb
```

---

## Deploy the Website

### 1. Clone Repository

```bash
cd ~/Desktop
git clone https://github.com/yusufgokce/innera.git
cd innera
```

### 2. Create .env File

```bash
nano .env
```

Add:
```env
RESEND_API_KEY=your_resend_api_key_here
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

Secure it:
```bash
chmod 600 .env
```

### 3. Build and Start Container

```bash
docker-compose up -d --build
```

### 4. Check Status

```bash
docker-compose ps
```

Should show:
```
NAME         IMAGE        COMMAND                  SERVICE   STATUS          PORTS
innera-app   innera-web   "uvicorn main:app --…"   web       Up 10 seconds   0.0.0.0:8000->8000/tcp
```

### 5. Test Locally

```bash
curl http://localhost:8000
```

You should see HTML output.

---

## Cloudflare Tunnel Setup

Cloudflare Tunnel creates a secure outbound connection from your server to Cloudflare, eliminating the need for port forwarding.

### 1. Create Cloudflare Account

Sign up at: https://dash.cloudflare.com/sign-up (free)

### 2. Add Domain to Cloudflare

1. Click "Add a site"
2. Enter: `inneracounselling.ca`
3. Choose Free plan
4. Cloudflare will scan your DNS records
5. Note the nameservers (e.g., `arely.ns.cloudflare.com`, `salvador.ns.cloudflare.com`)

### 3. Update Nameservers at Porkbun

1. Log in to Porkbun
2. Go to Domain Management → inneracounselling.ca
3. Update nameservers to Cloudflare's nameservers
4. Wait 5-60 minutes for propagation

### 4. Authenticate Cloudflared

On Linux server:
```bash
cloudflared tunnel login
```

This will give you a URL. Open it in browser and authorize.

### 5. Create Tunnel

```bash
cloudflared tunnel create innera-new
```

Note the tunnel ID (e.g., `b40b18d5-21c5-4e12-b1cd-3d2f9f5dc23a`)

### 6. Configure Tunnel

```bash
sudo mkdir -p /etc/cloudflared
sudo nano /etc/cloudflared/config.yml
```

Add (replace with your tunnel ID):
```yaml
tunnel: b40b18d5-21c5-4e12-b1cd-3d2f9f5dc23a
credentials-file: /home/yusuf/.cloudflared/b40b18d5-21c5-4e12-b1cd-3d2f9f5dc23a.json

ingress:
  - hostname: inneracounselling.ca
    service: http://localhost:8000
  - hostname: www.inneracounselling.ca
    service: http://localhost:8000
  - service: http_status:404
```

### 7. Install as System Service

```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

### 8. Check Status

```bash
sudo systemctl status cloudflared
```

Should show "active (running)" with "Registered tunnel connection".

---

## Domain Configuration

### 1. Add DNS Records in Cloudflare

Go to Cloudflare → inneracounselling.ca → DNS → Records

**Delete any existing A records** for the root domain and www.

Add CNAME records:

**Record 1:**
- Type: `CNAME`
- Name: `inneracounselling.ca` (or `@`)
- Target: `b40b18d5-21c5-4e12-b1cd-3d2f9f5dc23a.cfargotunnel.com`
- Proxy status: `Proxied` (orange cloud)
- TTL: `Auto`

**Record 2:**
- Type: `CNAME`
- Name: `www`
- Target: `b40b18d5-21c5-4e12-b1cd-3d2f9f5dc23a.cfargotunnel.com`
- Proxy status: `Proxied` (orange cloud)
- TTL: `Auto`

### 2. Configure SSL Settings

Go to Cloudflare → SSL/TLS → Overview

Set encryption mode to: **Flexible**

Turn OFF:
- Always Use HTTPS
- Automatic HTTPS Rewrites

### 3. Test Website

Wait 2-5 minutes for DNS propagation, then visit:
```
https://inneracounselling.ca
```

Should work from anywhere on the internet!

Test from server:
```bash
curl https://inneracounselling.ca
```

---

## Management & Maintenance

### Quick Health Check

Create monitoring script:
```bash
cat > ~/monitor.sh << 'EOF'
#!/bin/bash
echo "=== SYSTEM HEALTH ==="
echo "Uptime: $(uptime -p)"
echo ""
echo "=== CPU ==="
top -bn1 | grep "Cpu(s)" | awk '{print "Usage: " 100-$8 "%"}'
echo ""
echo "=== MEMORY ==="
free -h | awk 'NR==2{printf "Used: %s / %s (%.0f%%)\n", $3,$2,$3*100/$2 }'
echo ""
echo "=== DISK ==="
df -h / | awk 'NR==2{printf "Used: %s / %s (%s)\n", $3,$2,$5}'
echo ""
echo "=== DOCKER CONTAINERS ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "=== CLOUDFLARE TUNNEL ==="
if systemctl is-active --quiet cloudflared; then
    echo "Status: ✓ Running"
else
    echo "Status: ✗ Down"
fi
EOF

chmod +x ~/monitor.sh
echo "alias health='~/monitor.sh'" >> ~/.bashrc
source ~/.bashrc
```

Usage:
```bash
health
```

### Common Commands

```bash
# Check services
docker-compose ps
sudo systemctl status cloudflared

# View logs
docker-compose logs -f
sudo journalctl -u cloudflared -f

# Restart services
docker-compose restart
sudo systemctl restart cloudflared

# Update website
cd ~/Desktop/innera
git pull
docker-compose down
docker-compose up -d --build

# Purge Cloudflare cache (after major changes)
# Go to Cloudflare dashboard → Caching → Purge Everything
```

### Deploy Code Changes

From your Mac:
```bash
# 1. Make changes
# 2. Commit and push
git add -A
git commit -m "Your changes"
git push

# 3. SSH to server and deploy
ssh -p 2222 yusuf@100.120.234.126
cd ~/Desktop/innera
git pull
docker-compose down
docker-compose up -d --build
```

---

## Security Best Practices

### Current Security Posture

✅ **Secure:**
- No exposed ports (Cloudflare Tunnel uses outbound only)
- SSH only via Tailscale VPN (not exposed to internet)
- Docker runs as non-root user
- Environment variables in .env (not in code)
- Cloudflare DDoS protection
- Local network completely isolated from internet

### Additional Security (Optional)

#### 1. Enable Cloudflare Bot Protection

Cloudflare Dashboard → Security → Bots → Enable "Bot Fight Mode"

#### 2. Add Rate Limiting

Cloudflare Dashboard → Security → WAF → Rate limiting rules

Create rule for contact form:
- Path: `/contact`
- Requests: 5 per minute
- Action: Block

#### 3. Regular Updates

```bash
# Create update script
cat > ~/update-system.sh << 'EOF'
#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
EOF

chmod +x ~/update-system.sh

# Schedule weekly
crontab -e
# Add: 0 3 * * 0 ~/update-system.sh
```

#### 4. Backup Critical Files

```bash
# Backup tunnel credentials and .env
tar -czf ~/innera-backup-$(date +%Y%m%d).tar.gz \
  ~/.cloudflared \
  ~/Desktop/innera/.env

# Copy to external drive/cloud storage
```

---

## Troubleshooting

### Website Not Loading

**Check Docker:**
```bash
docker-compose ps
# Should show "Up"

docker-compose logs --tail=50
# Look for errors
```

**Check Cloudflare Tunnel:**
```bash
sudo systemctl status cloudflared
# Should show "active (running)"

sudo journalctl -u cloudflared -n 50
# Look for "Registered tunnel connection"
```

**Test local access:**
```bash
curl http://localhost:8000
# Should return HTML
```

**Restart everything:**
```bash
docker-compose restart
sudo systemctl restart cloudflared
```

**Purge Cloudflare cache:**
- Cloudflare Dashboard → Caching → Purge Everything

### Redirect Loop (ERR_TOO_MANY_REDIRECTS)

**Fix Cloudflare SSL mode:**
- SSL/TLS → Overview → Set to "Flexible"
- Purge cache
- Try incognito/private browsing

### Can't SSH to Server

**Check Tailscale on Mac:**
```bash
tailscale status
# If not running: sudo tailscale up
```

**Check Tailscale on server** (requires physical access):
```bash
sudo systemctl status tailscaled
# Should be running and auto-start on boot
```

**Test connection:**
```bash
ssh -p 2222 yusuf@100.120.234.126
```

### Changes Not Showing

1. Did you pull on server? `git pull`
2. Did you rebuild? `docker-compose up -d --build`
3. Clear browser cache (Cmd+Shift+R)
4. Purge Cloudflare cache
5. Try incognito mode

### Docker Build Fails

```bash
# Clean rebuild
docker-compose down
docker system prune -a
docker-compose up -d --build --no-cache
```

---

## Performance & Capacity

**Load Test Results (Apache Bench):**
- Requests per second: 2,561
- Average response time: 39ms
- Concurrent capacity: 500+ users
- Expected traffic: 5-20 concurrent users
- **Overhead: 100x-500x more capacity than needed**

Your N100 is incredibly overpowered for this use case!

---

## Adding Additional Domains (Future)

To add another domain (e.g., `innera.ca`):

1. Add domain to Cloudflare
2. Update nameservers at registrar
3. Add CNAME records pointing to tunnel
4. Update tunnel config (`/etc/cloudflared/config.yml`)
5. Restart tunnel

See DEPLOYMENT_GUIDE.txt for detailed steps.

---

## Quick Reference

### Server Details
- **Machine:** T8 (N100)
- **Local IP:** 192.168.4.43
- **Tailscale IP:** 100.120.234.126
- **SSH:** `ssh -p 2222 yusuf@100.120.234.126`
- **Domain:** inneracounselling.ca

### Tunnel Details
- **Tunnel ID:** b40b18d5-21c5-4e12-b1cd-3d2f9f5dc23a
- **Config:** `/etc/cloudflared/config.yml`
- **Credentials:** `~/.cloudflared/*.json`

### Important Commands
```bash
# Health check
health

# Restart services
docker-compose restart && sudo systemctl restart cloudflared

# Deploy updates
cd ~/Desktop/innera && git pull && docker-compose up -d --build

# View all logs
docker-compose logs -f & sudo journalctl -u cloudflared -f
```

### Important URLs
- **Website:** https://inneracounselling.ca
- **Cloudflare:** https://dash.cloudflare.com
- **Tailscale:** https://login.tailscale.com/admin
- **GitHub:** https://github.com/yusufgokce/innera

---

## Summary Checklist

- [ ] Linux machine updated and configured
- [ ] Tailscale VPN installed on both machines
- [ ] SSH keys set up and password auth disabled
- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] .env file created with Resend API key
- [ ] Website running locally (port 8000)
- [ ] Cloudflare account created
- [ ] Domain added to Cloudflare
- [ ] Nameservers updated at Porkbun
- [ ] Cloudflared installed and authenticated
- [ ] Tunnel created and configured
- [ ] Tunnel running as system service
- [ ] DNS CNAME records added in Cloudflare
- [ ] SSL mode set to "Flexible"
- [ ] Website accessible from internet
- [ ] Health monitoring script created
- [ ] Auto-start on boot enabled (Docker & Cloudflared)

**Congratulations! Your Innera website is live on the internet!** 🎉

No port forwarding, no exposed ports, no SSL certificate management needed. Everything just works!

---

**For more detailed maintenance and troubleshooting, see DEPLOYMENT_GUIDE.txt**
