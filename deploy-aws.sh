#!/bin/bash

#############################################
# AWS Deployment Script for Deepfake Detection
#############################################

set -e  # Exit on error

echo "🚀 Starting AWS Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on EC2
if [ -f "/etc/aws-instance" ] || curl -s http://169.254.169.254/latest/meta-data/instance-id &>/dev/null; then
    echo -e "${GREEN}✓ Running on AWS EC2${NC}"
else
    echo -e "${YELLOW}⚠ Not detected as EC2 instance. Proceeding anyway...${NC}"
fi

# Step 1: Update system
echo -e "\n${YELLOW}Step 1: Updating system...${NC}"
sudo apt-get update -y
sudo apt-get upgrade -y

# Step 2: Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo -e "\n${YELLOW}Step 2: Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "\n${GREEN}✓ Docker already installed${NC}"
fi

# Step 3: Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "\n${YELLOW}Step 3: Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "\n${GREEN}✓ Docker Compose already installed${NC}"
fi

# Step 4: Check for GPU and install NVIDIA Docker if available
if command -v nvidia-smi &> /dev/null; then
    echo -e "\n${YELLOW}Step 4: GPU detected. Installing NVIDIA Docker...${NC}"
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    sudo apt-get update
    sudo apt-get install -y nvidia-docker2
    sudo systemctl restart docker
    echo -e "${GREEN}✓ NVIDIA Docker installed${NC}"
    nvidia-smi
else
    echo -e "\n${YELLOW}⚠ No GPU detected. Using CPU-only inference.${NC}"
fi

# Step 5: Check for .env file
echo -e "\n${YELLOW}Step 5: Checking environment variables...${NC}"
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}✗ backend/.env not found!${NC}"
    echo "Creating template .env file..."
    cat > backend/.env << 'EOF'
OPENAI_API_KEY=your_openai_key_here
MODEL_SBI_PATH=/app/ml_models/deployment_package/models/sbi
MODEL_DISTILDIRE_PATH=/app/ml_models/deployment_package/models/distildire
EOF
    echo -e "${YELLOW}⚠ Please edit backend/.env and add your OPENAI_API_KEY${NC}"
    exit 1
else
    echo -e "${GREEN}✓ .env file found${NC}"
fi

# Step 6: Check for model files
echo -e "\n${YELLOW}Step 6: Checking model files...${NC}"
if [ ! -f "backend/ml_models/deployment_package/models/sbi/exp003_best_model.pth" ]; then
    echo -e "${RED}✗ SBI model not found at backend/ml_models/deployment_package/models/sbi/exp003_best_model.pth${NC}"
    echo -e "${YELLOW}Models will use placeholder mode.${NC}"
fi

if [ ! -f "backend/ml_models/deployment_package/models/distildire/v2_best_model.pth" ]; then
    echo -e "${RED}✗ DistilDIRE model not found at backend/ml_models/deployment_package/models/distildire/v2_best_model.pth${NC}"
    echo -e "${YELLOW}Models will use placeholder mode.${NC}"
fi

# Step 7: Build and start Docker containers
echo -e "\n${YELLOW}Step 7: Building and starting Docker containers...${NC}"
docker-compose down || true  # Stop existing containers
docker-compose build --no-cache
docker-compose up -d

echo -e "\n${GREEN}✓ Docker containers started${NC}"

# Step 8: Wait for services to be healthy
echo -e "\n${YELLOW}Step 8: Waiting for services to start...${NC}"
sleep 10

# Check backend health
if curl -f http://localhost:8000/health &>/dev/null; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    echo "Logs:"
    docker-compose logs backend | tail -20
    exit 1
fi

# Step 9: Install and configure Nginx (optional)
read -p "Do you want to install Nginx as a reverse proxy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}Step 9: Installing Nginx...${NC}"

    sudo apt-get install -y nginx

    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/deepfake-detection > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 25M;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/deepfake-detection /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t
    sudo systemctl restart nginx

    echo -e "${GREEN}✓ Nginx installed and configured${NC}"
fi

# Step 10: Display status
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\nApplication is running at:"
echo -e "  Backend:  ${GREEN}http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || hostname -I | awk '{print $1}'):8000${NC}"
echo -e "  Frontend: ${GREEN}http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || hostname -I | awk '{print $1}'):3000${NC}"

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "  Nginx:    ${GREEN}http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || hostname -I | awk '{print $1}')${NC}"
fi

echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "  View logs:       ${GREEN}docker-compose logs -f${NC}"
echo -e "  Restart:         ${GREEN}docker-compose restart${NC}"
echo -e "  Stop:            ${GREEN}docker-compose down${NC}"
echo -e "  Check status:    ${GREEN}docker-compose ps${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "  1. Test the API: curl http://localhost:8000/health"
echo -e "  2. Upload test image via frontend"
echo -e "  3. Configure SSL with Let's Encrypt (if using domain)"

echo -e "\n${GREEN}Happy detecting! 🎭${NC}"
