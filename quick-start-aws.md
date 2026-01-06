# Quick Start Guide - AWS Deployment

最快速的AWS部署指南（中文）

## 🚀 30分钟快速部署

### 准备工作（在本地完成）

1. **确保模型文件已解压**
   ```bash
   cd backend/ml_models
   ls deployment_package/models/sbi/exp003_best_model.pth
   ls deployment_package/models/distildire/v2_best_model.pth
   ```

2. **Push代码到GitHub**
   ```bash
   git add .
   git commit -m "Prepare for AWS deployment with all models"
   git push origin main
   ```

### AWS部署（在EC2上完成）

#### 步骤1: 启动EC2实例

在AWS Console中:
1. 进入 EC2 Dashboard
2. 点击 "Launch Instance"
3. 选择配置:
   - **Name**: deepfake-detection
   - **AMI**: Ubuntu Server 22.04 LTS 或 Deep Learning AMI (如果需要GPU)
   - **Instance type**:
     - 开发/测试: `t3.xlarge` (4 vCPU, 16GB RAM) - $0.17/hour
     - 生产/GPU: `g4dn.xlarge` (4 vCPU, 16GB RAM, NVIDIA T4) - $0.53/hour
   - **Storage**: 50GB
   - **Security Group**: 开放端口 22 (SSH), 80 (HTTP), 443 (HTTPS)
4. 下载key pair并启动实例

#### 步骤2: SSH连接到EC2

```bash
# 在本地电脑运行
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>
```

#### 步骤3: 克隆仓库

```bash
# 在EC2上运行
git clone https://github.com/your-username/COSC449_hybrid-deepfake-detection.git
cd COSC449_hybrid-deepfake-detection
```

#### 步骤4: 上传模型文件（如果模型没有push到git）

**选项A: 从本地上传（在另一个终端窗口）**
```bash
# 在本地电脑运行
scp -i your-key.pem backend/ml_models/deepfake_deployment.tar.gz ubuntu@<EC2-PUBLIC-IP>:~/COSC449_hybrid-deepfake-detection/backend/ml_models/

# 回到EC2终端，解压
cd backend/ml_models
tar -xzf deepfake_deployment.tar.gz
cd ../..
```

**选项B: 从S3下载（如果上传到了S3）**
```bash
# 在EC2上运行
aws s3 cp s3://your-bucket/deepfake_deployment.tar.gz backend/ml_models/
cd backend/ml_models && tar -xzf deepfake_deployment.tar.gz && cd ../..
```

#### 步骤5: 配置环境变量

```bash
# 创建.env文件
cat > backend/.env << EOF
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
MODEL_SBI_PATH=/app/ml_models/deployment_package/models/sbi
MODEL_DISTILDIRE_PATH=/app/ml_models/deployment_package/models/distildire
EOF
```

#### 步骤6: 一键部署

```bash
# 运行自动部署脚本
./deploy-aws.sh
```

脚本会自动:
- ✅ 安装Docker和Docker Compose
- ✅ 检测并配置GPU (如果有)
- ✅ 构建Docker镜像
- ✅ 启动服务
- ✅ 配置Nginx反向代理
- ✅ 运行健康检查

#### 步骤7: 测试部署

```bash
# 测试后端健康检查
curl http://localhost:8000/health

# 测试检测API
curl -X POST http://localhost:8000/api/v1/detect \
  -F "image=@/path/to/test-image.jpg"
```

#### 步骤8: 访问应用

在浏览器打开:
```
http://<EC2-PUBLIC-IP>
```

---

## 📊 部署后检查清单

### 验证所有模型已加载

```bash
# 查看启动日志
docker-compose logs backend | grep "model loaded"

# 应该看到:
# ✓ SBI model loaded successfully on cuda
# ✓ DistilDIRE model loaded successfully on cuda
# ✓ ChatGPT Vision model loaded successfully
# ✓ Detection Service initialized:
#   - SBI: Active
#   - DistilDIRE: Active
#   - ChatGPT Vision: Active
```

### 检查GPU使用情况（如果使用GPU实例）

```bash
# 查看GPU状态
nvidia-smi

# 应该看到GPU被PyTorch使用
```

### 测试完整流程

1. 打开浏览器访问 `http://<EC2-PUBLIC-IP>`
2. 上传一张测试图片
3. 查看结果，确保显示三个模型的预测结果
4. 检查 `ensemble_mode` 是否为 `"3_models_active"`

---

## 🔧 常见问题排查

### 问题1: 模型加载失败

```bash
# 检查模型文件是否存在
docker-compose exec backend ls -lh /app/ml_models/deployment_package/models/sbi/
docker-compose exec backend ls -lh /app/ml_models/deployment_package/models/distildire/

# 如果文件不存在，重新上传并重启
docker-compose restart backend
```

### 问题2: GPU不可用

```bash
# 检查NVIDIA驱动
nvidia-smi

# 如果报错，安装NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 问题3: 内存不足

```bash
# 查看内存使用
docker stats

# 如果内存不足，添加swap空间
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 问题4: API响应慢

- 确保使用GPU实例 (g4dn系列)
- 检查是否所有三个模型都在使用GPU
- 考虑升级到更大的实例

---

## 💰 成本优化建议

### 开发/测试阶段
- 使用 `t3.xlarge` (CPU only) - 便宜但慢
- 只在工作时间运行，下班后停止实例
- 使用 Spot Instances 可节省70%成本

### 生产环境
- 使用 `g4dn.xlarge` (GPU) - 性能好
- 设置Auto Scaling根据流量调整
- 使用Reserved Instances节省40-60%

### 停止实例节省成本

```bash
# 停止实例但保留数据
aws ec2 stop-instances --instance-ids i-xxxxxxxxx

# 重启实例
aws ec2 start-instances --instance-ids i-xxxxxxxxx
```

---

## 🔒 安全加固（可选）

### 1. 启用HTTPS（如果有域名）

```bash
# 安装Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 测试自动续期
sudo certbot renew --dry-run
```

### 2. 限制SSH访问

```bash
# 只允许你的IP访问SSH
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxx \
    --protocol tcp --port 22 \
    --cidr YOUR-IP/32

# 撤销所有人的SSH访问
aws ec2 revoke-security-group-ingress \
    --group-id sg-xxx \
    --protocol tcp --port 22 \
    --cidr 0.0.0.0/0
```

### 3. 使用AWS Secrets Manager存储API密钥

```bash
# 创建secret
aws secretsmanager create-secret \
    --name deepfake/openai-api-key \
    --secret-string "your-api-key"

# 在代码中读取（需要修改config.py）
```

---

## 📈 监控和日志

### 查看实时日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 只查看backend日志
docker-compose logs -f backend

# 查看最近100行
docker-compose logs --tail=100 backend
```

### 设置CloudWatch告警

```bash
# CPU使用率超过80%时发送告警
aws cloudwatch put-metric-alarm \
    --alarm-name deepfake-high-cpu \
    --alarm-description "CPU exceeds 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=InstanceId,Value=i-xxx \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:region:account-id:topic-name
```

---

## 🎯 下一步

1. ✅ 部署完成并测试通过
2. 📝 配置域名和SSL证书
3. 📊 设置监控和告警
4. 💰 优化成本（停机策略）
5. 🔒 加强安全配置
6. 📈 根据使用情况调整实例大小

---

**创建时间**: 2026-01-06
**适用版本**: v1.0
**预计部署时间**: 30-45分钟
