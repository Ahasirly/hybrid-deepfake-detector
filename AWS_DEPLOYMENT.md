# AWS Deployment Guide

Complete guide for deploying the Hybrid Deepfake Detection System to AWS.

## 📋 Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally (for testing)
- Git repository access

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      AWS Cloud                               │
│                                                              │
│  ┌──────────────┐        ┌─────────────────────────┐        │
│  │  CloudFront  │───────▶│  S3 (Frontend Static)   │        │
│  │     (CDN)    │        │    - React Build        │        │
│  └──────────────┘        └─────────────────────────┘        │
│         │                                                    │
│         │ /api/*                                             │
│         ▼                                                    │
│  ┌──────────────┐        ┌─────────────────────────┐        │
│  │     ALB      │───────▶│   EC2 / ECS             │        │
│  │ (Load Bal.)  │        │  - FastAPI Backend      │        │
│  └──────────────┘        │  - ML Models (1.4GB)    │        │
│                          │  - GPU Support          │        │
│                          └─────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Deployment Options

### Option A: EC2 with Docker (Recommended for GPU)

**Pros:**
- Full control over instance
- GPU support (g4dn.xlarge recommended)
- Cost: ~$0.50-0.70/hour with GPU

**Cons:**
- Manual scaling
- Higher maintenance

### Option B: ECS with Fargate (Simpler, No GPU)

**Pros:**
- Serverless container management
- Auto-scaling
- Lower maintenance

**Cons:**
- No GPU support (CPU inference slower)
- Cost: ~$0.04-0.08/hour (varies with load)

### Option C: SageMaker (ML-Optimized)

**Pros:**
- Built for ML inference
- Auto-scaling
- Managed endpoints

**Cons:**
- Most expensive: ~$0.10-0.30/hour base
- More complex setup

## 📦 Option A: EC2 Deployment (RECOMMENDED)

### Step 1: Launch EC2 Instance

```bash
# Create security group
aws ec2 create-security-group \
    --group-name deepfake-detection-sg \
    --description "Security group for deepfake detection API"

# Add inbound rules
aws ec2 authorize-security-group-ingress \
    --group-name deepfake-detection-sg \
    --protocol tcp --port 22 --cidr 0.0.0.0/0  # SSH

aws ec2 authorize-security-group-ingress \
    --group-name deepfake-detection-sg \
    --protocol tcp --port 80 --cidr 0.0.0.0/0   # HTTP

aws ec2 authorize-security-group-ingress \
    --group-name deepfake-detection-sg \
    --protocol tcp --port 443 --cidr 0.0.0.0/0  # HTTPS

# Launch GPU instance (for ML inference)
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \  # Ubuntu 22.04 Deep Learning AMI
    --instance-type g4dn.xlarge \        # GPU instance (NVIDIA T4)
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":50}}]'
```

**Instance Size Recommendations:**
- **g4dn.xlarge**: $0.526/hour - 4 vCPU, 16GB RAM, NVIDIA T4 GPU (RECOMMENDED for production)
- **g4dn.2xlarge**: $0.752/hour - 8 vCPU, 32GB RAM, NVIDIA T4 GPU (for higher load)
- **t3.xlarge**: $0.1664/hour - 4 vCPU, 16GB RAM (CPU-only, slower inference)

### Step 2: Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# For GPU instances: Install NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Verify GPU
nvidia-smi  # Should show NVIDIA T4
```

### Step 3: Deploy Application

```bash
# Clone repository
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Create .env file
cat > backend/.env << EOF
OPENAI_API_KEY=your_openai_key_here
MODEL_SBI_PATH=/app/ml_models/deployment_package/models/sbi
MODEL_DISTILDIRE_PATH=/app/ml_models/deployment_package/models/distildire
EOF

# Upload model files (if not in git)
# Option 1: SCP from local machine
scp -i your-key.pem backend/ml_models/deepfake_deployment.tar.gz ubuntu@your-ec2-ip:~/your-repo/backend/ml_models/

# Option 2: Download from S3 (if you uploaded there)
# aws s3 cp s3://your-bucket/deepfake_deployment.tar.gz backend/ml_models/

# Extract models (if needed)
cd backend/ml_models
tar -xzf deepfake_deployment.tar.gz
cd ../..

# Build and run with Docker Compose
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Test the API
curl http://localhost:8000/health
```

### Step 4: Configure Nginx as Reverse Proxy (Production)

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/deepfake-detection

# Add this configuration:
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or use EC2 public IP

    client_max_body_size 25M;  # Allow large image uploads

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for ML inference
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/deepfake-detection /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: Setup SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
sudo certbot renew --dry-run
```

## 🔧 Option B: ECS with Fargate Deployment

### Step 1: Create ECR Repositories

```bash
# Create repositories for backend and frontend
aws ecr create-repository --repository-name deepfake-detection-backend
aws ecr create-repository --repository-name deepfake-detection-frontend

# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com
```

### Step 2: Build and Push Docker Images

```bash
# Build backend image
cd backend
docker build -t deepfake-detection-backend .
docker tag deepfake-detection-backend:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/deepfake-detection-backend:latest
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/deepfake-detection-backend:latest

# Build frontend image
cd ../frontend
docker build -t deepfake-detection-frontend .
docker tag deepfake-detection-frontend:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/deepfake-detection-frontend:latest
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/deepfake-detection-frontend:latest
```

### Step 3: Create ECS Task Definition

Save this as `task-definition.json`:

```json
{
  "family": "deepfake-detection",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "8192",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account-id.dkr.ecr.us-east-1.amazonaws.com/deepfake-detection-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "your-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/deepfake-detection",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create ECS cluster
aws ecs create-cluster --cluster-name deepfake-detection-cluster

# Create ECS service (connects to ALB)
aws ecs create-service \
    --cluster deepfake-detection-cluster \
    --service-name deepfake-detection-service \
    --task-definition deepfake-detection \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

## 💰 Cost Estimation

### Monthly Costs (24/7 operation)

**Option A: EC2 with GPU**
- g4dn.xlarge: ~$378/month
- Storage (50GB): ~$5/month
- Data transfer: ~$10-50/month
- **Total: ~$393-433/month**

**Option B: ECS Fargate (CPU only)**
- Fargate (2vCPU, 8GB): ~$60-120/month (depends on usage)
- Data transfer: ~$10-50/month
- **Total: ~$70-170/month**

**Option C: Pay-per-use (Stop when not needed)**
- EC2 GPU: ~$0.526/hour = ~$12.6/day
- **Best for development/testing**

## 🧪 Testing Deployment

```bash
# Test health endpoint
curl https://your-domain.com/health

# Test detection API
curl -X POST https://your-domain.com/api/v1/detect \
  -F "image=@test_image.jpg"

# Expected response:
# {
#   "is_fake": false,
#   "confidence": 0.85,
#   "ensemble_mode": "3_models_active",
#   "models": {
#     "sbi": {"is_fake": false, "confidence": 0.82, "status": "active"},
#     "distildire": {"is_fake": false, "confidence": 0.88, "status": "active"},
#     "chatgpt": {"is_fake": false, "confidence": 0.85, "status": "active"}
#   }
# }
```

## 📊 Monitoring

### CloudWatch Metrics

```bash
# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
    --alarm-name deepfake-high-cpu \
    --alarm-description "Alert when CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=i-xxx \
    --evaluation-periods 2
```

### Application Logs

```bash
# View Docker logs
docker-compose logs -f backend

# Or if using ECS:
aws logs tail /ecs/deepfake-detection --follow
```

## 🔒 Security Best Practices

1. **Use Environment Variables for Secrets**
   ```bash
   # Store in AWS Secrets Manager
   aws secretsmanager create-secret \
       --name deepfake/openai-api-key \
       --secret-string "your-api-key"
   ```

2. **Enable HTTPS Only**
   - Use Let's Encrypt or AWS Certificate Manager
   - Redirect HTTP to HTTPS

3. **Restrict Security Groups**
   ```bash
   # Only allow specific IPs if possible
   aws ec2 authorize-security-group-ingress \
       --group-id sg-xxx \
       --protocol tcp --port 443 \
       --cidr your-ip/32
   ```

4. **Regular Updates**
   ```bash
   # Auto-update script
   sudo apt-get update && sudo apt-get upgrade -y
   docker-compose pull
   docker-compose up -d
   ```

## 🚀 Scaling Strategies

### Horizontal Scaling (Multiple Instances)

1. **Create AMI from configured EC2**
   ```bash
   aws ec2 create-image \
       --instance-id i-xxx \
       --name "deepfake-detection-v1"
   ```

2. **Create Auto Scaling Group**
   ```bash
   # Create launch template
   # Set up Auto Scaling based on CPU/memory
   ```

3. **Add Application Load Balancer**
   - Distributes traffic across instances
   - Health checks ensure uptime

## 📝 Maintenance Tasks

### Daily
- Monitor CloudWatch metrics
- Check application logs for errors

### Weekly
- Review API usage and costs
- Update dependencies if needed

### Monthly
- Security patches
- Performance optimization
- Cost analysis

## 🔧 Troubleshooting

### Models Not Loading

```bash
# Check model files exist
docker-compose exec backend ls -lh /app/ml_models/deployment_package/models/

# Check logs for errors
docker-compose logs backend | grep -i error

# Verify GPU access (if using GPU instance)
docker-compose exec backend nvidia-smi
```

### High Memory Usage

```bash
# Monitor memory
docker stats

# Reduce batch size or use smaller instance
# Consider adding swap space
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Slow Inference

- Enable GPU if using CPU-only instance
- Reduce image size before inference
- Consider caching common results

---

## 📞 Support

For issues or questions:
1. Check application logs
2. Review CloudWatch metrics
3. Test individual models separately
4. Contact AWS support for infrastructure issues

**Deployment created**: 2026-01-06
**Last updated**: 2026-01-06
