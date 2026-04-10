# 🚀 Deployment Guide

This guide provides step-by-step instructions for deploying the Goal Tracker application to a production server.

---

## 📋 Prerequisites

### Server Requirements
- **OS**: Ubuntu 24.04 LTS (recommended)
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: Minimum 10GB
- **CPU**: 2 cores minimum
- **Network**: Public IP or domain name

### Required Software
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

---

## 🐳 Docker Deployment (Recommended)

### Step 1: Install Docker

```bash
# Update package index
sudo apt update

# Install prerequisites
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation
sudo docker --version
sudo docker compose version

# Add your user to docker group (avoid using sudo)
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Clone Repository

```bash
git clone https://github.com/inno-se-toolkit/se-toolkit-hackathon.git
cd se-toolkit-hackathon
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env
```

Update the following in `.env`:
```bash
SECRET_KEY=your-very-secure-random-secret-key
DATABASE_URL=sqlite:///./goal_tracker.db
```

### Step 4: Build and Start

```bash
# Build and start all services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### Step 5: Verify Deployment

```bash
# Check if services are healthy
curl http://localhost:8000/docs
curl http://localhost

# View running containers
docker compose ps
```

### Step 6: Setup Firewall (Optional but Recommended)

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

---

## 🌐 Domain Setup (Optional)

### With Nginx Reverse Proxy

If you want to use a domain name:

```bash
# Install nginx
sudo apt install -y nginx

# Create nginx config
sudo tee /etc/nginx/sites-available/goal-tracker << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/goal-tracker /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### With SSL (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

---

## 🔄 Managing the Application

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
```

### Stop Services

```bash
# Stop all
docker compose down

# Stop and remove volumes (WARNING: deletes data!)
docker compose down -v
```

### Update Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose up -d --build

# Remove old images
docker image prune -f
```

### Backup Database

```bash
# Copy database file
docker cp goal-tracker-backend:/app/goal_tracker.db ./backup_$(date +%Y%m%d).db

# Or backup the entire volume
docker run --rm -v backend_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .
```

### Restore Database

```bash
# Stop backend
docker compose stop backend

# Copy database back
docker cp ./backup_20260409.db goal-tracker-backend:/app/goal_tracker.db

# Start backend
docker compose start backend
```

---

## 📊 Monitoring

### Check Resource Usage

```bash
# Docker stats
docker stats

# System resources
docker system df
```

### Health Checks

The backend includes a health check endpoint:

```bash
curl http://localhost:8000/docs
```

---

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
sudo lsof -i :80
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Container Won't Start

```bash
# Check logs
docker compose logs backend

# Rebuild without cache
docker compose build --no-cache

# Remove and recreate
docker compose down
docker compose up -d
```

### Database Issues

```bash
# Access backend container
docker exec -it goal-tracker-backend sh

# Check database file
ls -la /app/goal_tracker.db

# Exit container
exit
```

---

## 📈 Performance Optimization

### Increase Docker Resources

Edit `/etc/docker/daemon.json`:

```json
{
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  }
}
```

Restart Docker:
```bash
sudo systemctl restart docker
```

### Database Optimization

For production, consider switching to PostgreSQL:

```yaml
# Update docker-compose.yml
services:
  database:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: goal_tracker
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    environment:
      DATABASE_URL: postgresql://admin:secure_password@database:5432/goal_tracker
```

---

## 📞 Support

For issues or questions:
- Check the logs: `docker compose logs -f`
- Review the documentation
- Open an issue on GitHub

---

**Happy Deploying! 🚀**
