# Innera Deployment Guide

This guide explains how to deploy the Innera counseling website on your Linux machine (N100) using Docker and nginx as a reverse proxy.

## Prerequisites

On your Linux machine, you need:
- Docker installed
- Docker Compose installed
- Git installed

### Installing Docker on Linux

```bash
# Update package index
sudo apt update

# Install dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

## Deployment Steps

### 1. Clone the Repository on Your Linux Machine

```bash
# Navigate to your desired directory
cd ~

# Clone the repository
git clone https://github.com/yusufgokce/innera.git

# Navigate into the project
cd innera
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your actual API key
nano .env
```

Add your Resend API key:
```
RESEND_API_KEY=re_RnXZnMGE_NT6UdvSCZiZP7fGNHkaCccNS
```

**Security Note:** Never commit the `.env` file to git. It's already in `.gitignore`.

### 3. Development Deployment (HTTP Only)

For initial testing without SSL:

Edit `nginx/nginx.conf` and comment out the HTTPS redirect:

```nginx
# Comment out this server block:
# server {
#     listen 80;
#     server_name localhost;
#     location / {
#         return 301 https://$host$request_uri;
#     }
# }

# And change the HTTPS server block to:
server {
    listen 80;  # Change from 443 ssl http2
    server_name localhost;

    # Comment out SSL lines:
    # listen 443 ssl http2;
    # ssl_certificate /etc/nginx/ssl/cert.pem;
    # ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... etc
```

Then start the services:

```bash
# Build and start containers
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps
```

Access the website at: `http://localhost` or `http://<your-linux-machine-ip>`

### 4. Production Deployment (HTTPS with SSL)

#### Option A: Self-Signed Certificate (for local network only)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=CA/ST=Ontario/L=Toronto/O=Innera/CN=innera.local"
```

#### Option B: Let's Encrypt Certificate (for public domain)

If you have a domain name pointing to your machine:

```bash
# Install certbot
sudo apt install -y certbot

# Get certificate (replace innera.example.com with your domain)
sudo certbot certonly --standalone -d innera.example.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/innera.example.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/innera.example.com/privkey.pem nginx/ssl/key.pem

# Set permissions
sudo chown $USER:$USER nginx/ssl/*.pem
```

#### Update nginx.conf for SSL

Uncomment the SSL lines in `nginx/nginx.conf`:

```nginx
# HTTP server - redirect to HTTPS
server {
    listen 80;
    server_name localhost;  # or your domain name

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name localhost;  # or your domain name

    # Uncomment SSL configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of configuration
}
```

Then restart:

```bash
docker compose down
docker compose up -d
```

### 5. Accessing from Other Devices on Your Network

Find your Linux machine's IP:
```bash
hostname -I
```

Access from other devices: `http://<linux-machine-ip>` or `https://<linux-machine-ip>`

## Managing the Application

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f nginx
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart web
```

### Stop Services
```bash
docker compose down
```

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Check Container Health
```bash
docker compose ps
docker stats
```

## Architecture

```
Internet/Local Network
         ↓
    [Port 80/443]
         ↓
    nginx (Reverse Proxy)
    - Rate limiting
    - SSL termination
    - Security headers
    - Gzip compression
         ↓
    FastAPI Application (Port 8000)
    - Serves web pages
    - Handles contact form
    - Sends emails via Resend
```

## Security Features

The nginx configuration includes:

1. **Rate Limiting**: Prevents abuse
   - General pages: 10 requests/second
   - API endpoints: 5 requests/second

2. **Security Headers**:
   - X-Frame-Options
   - X-Content-Type-Options
   - X-XSS-Protection
   - Referrer-Policy

3. **SSL/TLS**: Encryption for all traffic (when configured)

4. **Network Isolation**: Docker containers on private network

5. **Non-root User**: Application runs as non-privileged user

## Firewall Configuration

Allow traffic on your Linux machine:

```bash
# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall if not already enabled
sudo ufw enable

# Check status
sudo ufw status
```

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 80/443
sudo lsof -i :80
sudo lsof -i :443

# Stop nginx if running outside Docker
sudo systemctl stop nginx
```

### Container Won't Start
```bash
# Check logs
docker compose logs web

# Check if .env file exists
ls -la .env

# Verify environment variables
docker compose config
```

### Can't Access from Other Devices
```bash
# Check firewall
sudo ufw status

# Check if containers are running
docker compose ps

# Check nginx is listening
docker compose exec nginx netstat -tlnp
```

### SSL Certificate Issues
```bash
# Verify certificate files exist
ls -la nginx/ssl/

# Check nginx configuration syntax
docker compose exec nginx nginx -t

# View nginx error logs
docker compose logs nginx
```

## Performance Tips for N100

Your N100 is more than capable, but here are some optimizations:

1. **Limit Docker Resources** (optional):
   Add to docker-compose.yml under each service:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 512M
   ```

2. **Enable Docker BuildKit**:
   ```bash
   export DOCKER_BUILDKIT=1
   ```

3. **Clean Up Regularly**:
   ```bash
   # Remove unused images
   docker image prune -a

   # Remove unused volumes
   docker volume prune
   ```

## Backup

Regular backups of important files:

```bash
# Backup script
#!/bin/bash
BACKUP_DIR=~/innera-backup-$(date +%Y%m%d)
mkdir -p $BACKUP_DIR
cp .env $BACKUP_DIR/
cp -r nginx/ssl $BACKUP_DIR/
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR
```

## Support

For issues or questions:
- Email: elif@inneracounselling.ca
- GitHub: https://github.com/yusufgokce/innera/issues
