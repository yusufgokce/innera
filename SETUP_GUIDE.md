# Complete Setup Guide: Hosting Innera on Your Linux N100

This guide covers everything from initial Linux setup to making your website accessible on the internet.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Linux Machine Initial Setup](#linux-machine-initial-setup)
3. [SSH Setup for Remote Access](#ssh-setup-for-remote-access)
4. [Install Required Software](#install-required-software)
5. [Deploy the Website](#deploy-the-website)
6. [Router Configuration (Port Forwarding)](#router-configuration-port-forwarding)
7. [Domain & DNS Setup](#domain--dns-setup)
8. [SSL Certificate Setup](#ssl-certificate-setup)
9. [Management & Maintenance](#management--maintenance)
10. [Security Best Practices](#security-best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Linux N100 machine running Ubuntu/Debian
- Home internet connection with router access
- Domain name (optional but recommended for SSL)
- Your Mac for initial setup

---

## Linux Machine Initial Setup

### 1. Find Your Linux Machine's IP Address

On your Linux machine:
```bash
# Find local IP address
hostname -I
# Example output: 192.168.1.100

# Or use:
ip addr show | grep "inet 192"
```

Note this IP address - you'll need it for SSH and router configuration.

### 2. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Create a Non-Root User (if not already done)

```bash
# Create user
sudo adduser yusuf

# Add to sudo group
sudo usermod -aG sudo yusuf

# Add to docker group (we'll install Docker later)
sudo usermod -aG docker yusuf
```

---

## SSH Setup for Remote Access

### Part A: Setup SSH Server on Linux Machine

#### 1. Install OpenSSH Server

```bash
sudo apt install openssh-server -y
```

#### 2. Configure SSH for Security

Edit SSH config:
```bash
sudo nano /etc/ssh/sshd_config
```

Recommended settings:
```bash
# Port 22 (default) or change to something else like 2222 for extra security
Port 22

# Disable root login
PermitRootLogin no

# Use public key authentication
PubkeyAuthentication yes

# Disable password authentication (after setting up keys)
# PasswordAuthentication no  # Enable this after testing key-based login

# Allow specific user only
AllowUsers yusuf
```

Save and restart SSH:
```bash
sudo systemctl restart ssh
sudo systemctl enable ssh
```

#### 3. Check SSH Status

```bash
sudo systemctl status ssh

# Should show "active (running)"
```

### Part B: Setup SSH Keys from Your Mac

#### 1. Generate SSH Key on Your Mac (if you don't have one)

```bash
# Check if you already have a key
ls -la ~/.ssh/id_*.pub

# If not, generate one
ssh-keygen -t ed25519 -C "yusufnahit6061@gmail.com"
# Press Enter to accept default location
# Enter a passphrase (recommended) or leave empty
```

#### 2. Copy SSH Key to Linux Machine

From your Mac:
```bash
# Replace 192.168.1.100 with your Linux machine's IP
ssh-copy-id yusuf@192.168.1.100

# Enter password when prompted
```

#### 3. Test SSH Connection

```bash
# From your Mac
ssh yusuf@192.168.1.100

# You should now be logged in without password!
```

#### 4. Configure SSH Config on Mac (Optional but Convenient)

On your Mac, edit `~/.ssh/config`:
```bash
nano ~/.ssh/config
```

Add:
```
Host innera-server
    HostName 192.168.1.100
    User yusuf
    Port 22
    IdentityFile ~/.ssh/id_ed25519
```

Now you can connect with just:
```bash
ssh innera-server
```

---

## Install Required Software

SSH into your Linux machine, then:

### 1. Install Docker

```bash
# Remove old versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### 2. Add User to Docker Group

```bash
sudo usermod -aG docker $USER

# Log out and back in for this to take effect
exit
# Then SSH back in
ssh yusuf@192.168.1.100

# Test Docker without sudo
docker ps
```

### 3. Install Git

```bash
sudo apt install git -y
git --version
```

### 4. Install Useful Tools

```bash
sudo apt install -y \
    htop \
    ncdu \
    net-tools \
    ufw \
    fail2ban
```

---

## Deploy the Website

### 1. Clone the Repository

```bash
cd ~
git clone https://github.com/yusufgokce/innera.git
cd innera
```

### 2. Create .env File

```bash
# Copy example
cp .env.example .env

# Edit with your API key
nano .env
```

Add your Resend API key:
```
RESEND_API_KEY=re2j9mSQQ_HYkhJqMCXzUHCB5i7vxPE21d
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

Secure the file:
```bash
chmod 600 .env
```

### 3. Configure Nginx for HTTP (Initial Setup)

Edit the nginx configuration for initial testing:
```bash
nano nginx/nginx.conf
```

Find the HTTP server block and ensure it looks like this for initial setup:
```nginx
# HTTP server - for initial testing
server {
    listen 80;
    server_name _;  # Accept any hostname

    location / {
        limit_req zone=general burst=20 nodelay;

        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        limit_req zone=api burst=10 nodelay;

        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Comment out HTTPS block for now
# server {
#     listen 443 ssl http2;
#     ...
# }
```

### 4. Build and Start Containers

```bash
# Build images
docker compose build

# Start containers
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 5. Test Locally

On your Linux machine:
```bash
curl http://localhost

# Or from your Mac on the same network:
# curl http://192.168.1.100
```

Open browser on your Mac: `http://192.168.1.100`

You should see the Innera website!

---

## Router Configuration (Port Forwarding)

To make your website accessible from the internet, you need to configure port forwarding on your router.

### 1. Find Your Router's IP

On your Linux machine:
```bash
ip route | grep default
# Example output: default via 192.168.1.1 ...
```

The router IP is usually `192.168.1.1` or `192.168.0.1`

### 2. Access Router Admin Panel

From any device on your network:
- Open browser: `http://192.168.1.1` (or your router's IP)
- Login with admin credentials (usually on router label or manual)

### 3. Configure Port Forwarding

Every router is different, but generally:

**Navigate to:** `Advanced` → `Port Forwarding` or `NAT` → `Port Forwarding`

**Add new rule:**

| Setting | Value |
|---------|-------|
| Service Name | Innera HTTP |
| External Port | 80 |
| Internal IP | 192.168.1.100 (your Linux machine) |
| Internal Port | 80 |
| Protocol | TCP |
| Enable | Yes |

**Add another rule for HTTPS:**

| Setting | Value |
|---------|-------|
| Service Name | Innera HTTPS |
| External Port | 443 |
| Internal IP | 192.168.1.100 |
| Internal Port | 443 |
| Protocol | TCP |
| Enable | Yes |

**Optional - SSH Access from Internet:**

| Setting | Value |
|---------|-------|
| Service Name | SSH |
| External Port | 2222 (use different port for security) |
| Internal IP | 192.168.1.100 |
| Internal Port | 22 |
| Protocol | TCP |
| Enable | Yes |

⚠️ **Security Warning:** Only enable SSH port forwarding if you need external access and have strong authentication (key-based only, no passwords).

### 4. Find Your Public IP

```bash
curl ifconfig.me
# Or visit: https://whatismyipaddress.com/
```

### 5. Test External Access

From your phone (using cellular data, not WiFi):
- Open browser: `http://YOUR_PUBLIC_IP`

You should see your website!

---

## Domain & DNS Setup

### Option A: Use a Domain Name (Recommended)

#### 1. Register a Domain

Register a domain at:
- Namecheap
- Google Domains
- Cloudflare
- GoDaddy

Example: `inneracounselling.ca`

#### 2. Configure DNS Records

In your domain registrar's DNS settings, add an A record:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_PUBLIC_IP | 3600 |
| A | www | YOUR_PUBLIC_IP | 3600 |

Wait 5-60 minutes for DNS to propagate.

#### 3. Test Domain

```bash
# Check DNS propagation
nslookup inneracounselling.ca

# Should return your public IP
```

### Option B: Use Dynamic DNS (for Changing IP Addresses)

If your ISP changes your IP address regularly, use Dynamic DNS:

**Providers:**
- Duck DNS (free)
- No-IP (free tier available)
- Dynu (free)

**Setup with Duck DNS (example):**

1. Sign up at https://www.duckdns.org/
2. Create subdomain: `innera.duckdns.org`
3. Install Duck DNS updater on Linux:

```bash
# Create directory
mkdir ~/duckdns
cd ~/duckdns

# Create update script
nano duck.sh
```

Add:
```bash
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=innera&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
```

Make executable and schedule:
```bash
chmod 700 duck.sh

# Add to crontab
crontab -e

# Add this line to update every 5 minutes:
*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

---

## SSL Certificate Setup

### Option A: Let's Encrypt with Certbot (For Real Domain)

#### 1. Install Certbot

```bash
sudo apt install certbot -y
```

#### 2. Stop Docker Containers

```bash
cd ~/innera
docker compose down
```

#### 3. Get Certificate

```bash
# Replace with your domain
sudo certbot certonly --standalone -d inneracounselling.ca -d www.inneracounselling.ca

# Follow prompts, enter email address
```

Certificates will be saved to:
- Certificate: `/etc/letsencrypt/live/inneracounselling.ca/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/inneracounselling.ca/privkey.pem`

#### 4. Copy Certificates

```bash
# Create ssl directory
mkdir -p ~/innera/nginx/ssl

# Copy certificates
sudo cp /etc/letsencrypt/live/inneracounselling.ca/fullchain.pem ~/innera/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/inneracounselling.ca/privkey.pem ~/innera/nginx/ssl/key.pem

# Fix permissions
sudo chown $USER:$USER ~/innera/nginx/ssl/*.pem
chmod 600 ~/innera/nginx/ssl/*.pem
```

#### 5. Setup Auto-Renewal

```bash
# Create renewal script
sudo nano /etc/cron.d/certbot-renew
```

Add:
```bash
0 3 * * * root certbot renew --quiet --deploy-hook "cp /etc/letsencrypt/live/inneracounselling.ca/fullchain.pem /home/yusuf/innera/nginx/ssl/cert.pem && cp /etc/letsencrypt/live/inneracounselling.ca/privkey.pem /home/yusuf/innera/nginx/ssl/key.pem && chown yusuf:yusuf /home/yusuf/innera/nginx/ssl/*.pem && cd /home/yusuf/innera && docker compose restart nginx"
```

#### 6. Update Nginx Configuration

```bash
nano ~/innera/nginx/nginx.conf
```

Uncomment HTTPS section and update:
```nginx
# HTTP server - redirect to HTTPS
server {
    listen 80;
    server_name inneracounselling.ca www.inneracounselling.ca;

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name inneracounselling.ca www.inneracounselling.ca;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of configuration
}
```

#### 7. Restart Containers

```bash
docker compose up -d
```

### Option B: Self-Signed Certificate (For Testing/Local)

```bash
cd ~/innera/nginx/ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem \
  -out cert.pem \
  -subj "/C=CA/ST=Ontario/L=Toronto/O=Innera/CN=innera.local"

chmod 600 *.pem
```

⚠️ Self-signed certificates will show browser warnings.

---

## Management & Maintenance

### Quick Management Script

Create a management script for common tasks:

```bash
nano ~/innera/manage.sh
```

Add:
```bash
#!/bin/bash

case "$1" in
  start)
    cd ~/innera && docker compose up -d
    echo "Innera started"
    ;;
  stop)
    cd ~/innera && docker compose down
    echo "Innera stopped"
    ;;
  restart)
    cd ~/innera && docker compose restart
    echo "Innera restarted"
    ;;
  logs)
    cd ~/innera && docker compose logs -f
    ;;
  status)
    cd ~/innera && docker compose ps
    ;;
  update)
    cd ~/innera
    git pull
    docker compose down
    docker compose build --no-cache
    docker compose up -d
    echo "Innera updated"
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|logs|status|update}"
    exit 1
    ;;
esac
```

Make executable:
```bash
chmod +x ~/innera/manage.sh
```

Usage:
```bash
# From anywhere on your Linux machine
~/innera/manage.sh start
~/innera/manage.sh stop
~/innera/manage.sh restart
~/innera/manage.sh logs
~/innera/manage.sh status
~/innera/manage.sh update
```

### Auto-Start on Boot

Create systemd service:
```bash
sudo nano /etc/systemd/system/innera.service
```

Add:
```ini
[Unit]
Description=Innera Counselling Website
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/yusuf/innera
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
User=yusuf

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable innera
sudo systemctl start innera

# Check status
sudo systemctl status innera
```

### Common Commands

```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f web
docker compose logs -f nginx

# Check resource usage
docker stats

# Restart specific service
docker compose restart web
docker compose restart nginx

# Pull latest code
cd ~/innera
git pull
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## Security Best Practices

### 1. Configure Firewall (UFW)

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (important - do this first!)
sudo ufw allow 22/tcp
# Or if using custom SSH port: sudo ufw allow 2222/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status verbose

# Enable if not already
sudo ufw enable
```

### 2. Install and Configure Fail2Ban

```bash
# Install
sudo apt install fail2ban -y

# Configure
sudo nano /etc/fail2ban/jail.local
```

Add:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
```

Restart:
```bash
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Check status
sudo fail2ban-client status
```

### 3. Disable Password Authentication for SSH

After confirming key-based SSH works:

```bash
sudo nano /etc/ssh/sshd_config
```

Change:
```
PasswordAuthentication no
```

Restart:
```bash
sudo systemctl restart ssh
```

### 4. Regular Updates

Create update script:
```bash
nano ~/update-system.sh
```

Add:
```bash
#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

Make executable:
```bash
chmod +x ~/update-system.sh
```

Run weekly:
```bash
crontab -e

# Add:
0 3 * * 0 ~/update-system.sh
```

### 5. Backup Script

```bash
nano ~/backup-innera.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Backup .env file
cp ~/innera/.env $BACKUP_DIR/env-$DATE

# Backup SSL certificates
cp -r ~/innera/nginx/ssl $BACKUP_DIR/ssl-$DATE

# Keep only last 7 backups
cd $BACKUP_DIR
ls -t | tail -n +15 | xargs rm -rf

echo "Backup completed: $DATE"
```

Make executable and schedule:
```bash
chmod +x ~/backup-innera.sh

crontab -e

# Add daily backup at 2 AM:
0 2 * * * ~/backup-innera.sh
```

---

## Troubleshooting

### Website Not Accessible

#### Check Docker Containers
```bash
docker compose ps
# All should be "Up"

docker compose logs
# Look for errors
```

#### Check Port Forwarding
```bash
# Test from outside network (use phone on cellular):
curl -I http://YOUR_PUBLIC_IP

# Should return HTTP 200 or 301
```

#### Check Firewall
```bash
sudo ufw status
# Ensure ports 80 and 443 are allowed

# Check if nginx is listening
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

#### Check Nginx Configuration
```bash
# Test nginx config
docker compose exec nginx nginx -t

# View nginx error logs
docker compose logs nginx | tail -50
```

### Can't SSH from Outside

#### Test Local SSH First
```bash
# From your Mac on same network:
ssh yusuf@192.168.1.100
```

#### Check SSH is Running
```bash
sudo systemctl status ssh
```

#### Check Port Forwarding
- Verify router has SSH port forward rule
- Try from outside network (phone on cellular)

```bash
ssh -p 2222 yusuf@YOUR_PUBLIC_IP
```

### SSL Certificate Issues

#### Check Certificate Files
```bash
ls -la ~/innera/nginx/ssl/
# Should have cert.pem and key.pem

# Verify certificate
openssl x509 -in ~/innera/nginx/ssl/cert.pem -text -noout
```

#### Renew Let's Encrypt Certificate
```bash
sudo certbot renew --force-renewal
# Then copy new certificates as shown above
```

### Docker Issues

#### Restart Everything
```bash
cd ~/innera
docker compose down
docker system prune -a
docker compose build --no-cache
docker compose up -d
```

#### Check Disk Space
```bash
df -h
# If low, clean up:
docker system prune -a --volumes
```

#### View Full Logs
```bash
docker compose logs --tail=100 web
docker compose logs --tail=100 nginx
```

### Contact Form Not Working

#### Check Resend API Key
```bash
cat ~/innera/.env
# Verify RESEND_API_KEY is correct

# Test from inside container:
docker compose exec web env | grep RESEND
```

#### Check Application Logs
```bash
docker compose logs web | grep -i error
docker compose logs web | grep -i resend
```

### Site is Slow

#### Check Resource Usage
```bash
htop
docker stats

# Check disk usage
ncdu /
```

#### Check Nginx Logs for Issues
```bash
docker compose logs nginx | grep -E "error|warn"
```

---

## Quick Reference

### Important Files
- **Application:** `~/innera/`
- **Environment:** `~/innera/.env`
- **Docker Compose:** `~/innera/docker-compose.yml`
- **Nginx Config:** `~/innera/nginx/nginx.conf`
- **SSL Certs:** `~/innera/nginx/ssl/`
- **Backups:** `~/backups/`

### Important Commands
```bash
# Management
~/innera/manage.sh {start|stop|restart|logs|status|update}

# Direct Docker commands
cd ~/innera
docker compose up -d      # Start
docker compose down       # Stop
docker compose restart    # Restart
docker compose logs -f    # View logs
docker compose ps         # Status

# System
sudo systemctl status innera  # Service status
sudo ufw status              # Firewall status
sudo fail2ban-client status  # Fail2ban status

# SSH
ssh yusuf@192.168.1.100     # Local
ssh yusuf@YOUR_PUBLIC_IP    # External (if port forwarded)
```

### Important URLs
- **Local:** `http://192.168.1.100`
- **External:** `http://YOUR_PUBLIC_IP` or `https://inneracounselling.ca`
- **Router Admin:** `http://192.168.1.1`

### Support
- **Email:** elif@inneracounselling.ca
- **GitHub Issues:** https://github.com/yusufgokce/innera/issues

---

## Summary Checklist

- [ ] Linux machine updated and configured
- [ ] SSH server installed and configured
- [ ] SSH keys set up from Mac
- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] .env file created with API key
- [ ] Website running locally
- [ ] Router port forwarding configured (80, 443)
- [ ] Website accessible from external network
- [ ] Domain DNS configured (optional)
- [ ] SSL certificate obtained and configured
- [ ] Firewall (UFW) enabled
- [ ] Fail2ban installed
- [ ] Management scripts created
- [ ] Auto-start on boot enabled
- [ ] Backup script scheduled
- [ ] System update script scheduled

Congratulations! Your Innera website is now live on the internet! 🎉
