# A股行情中心 - 部署指南

## 方案1：Streamlit Cloud（推荐）⭐

### 优点
- 完全免费
- 最简单，无需服务器
- 自动HTTPS
- 适合演示和竞赛

### 部署步骤

1. **准备GitHub仓库**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <你的GitHub仓库地址>
git push -u origin main
```

2. **部署到Streamlit Cloud**
- 访问 https://share.streamlit.io/
- 用GitHub账号登录
- 点击 "New app"
- 选择仓库：你的仓库名
- 选择分支：main
- 选择主文件：stock_app.py
- 点击 "Deploy"

3. **等待部署完成**
- 大约2-3分钟
- 会得到一个公网地址：https://xxx.streamlit.app

### 注意事项
- 确保 requirements.txt 包含所有依赖
- 数据库文件会在每次重启时重置（可以考虑使用云数据库）

---

## 方案2：内网穿透（临时演示）

### 使用 ngrok

1. **注册并下载**
- 访问 https://ngrok.com/
- 注册账号并下载

2. **启动应用**
```bash
streamlit run stock_app.py
```

3. **创建隧道**
```bash
# 在另一个终端
ngrok http 8501
```

4. **获取公网地址**
- 会显示类似：https://xxxx.ngrok.io
- 分享这个地址给别人

### 使用 localtunnel

```bash
# 安装
npm install -g localtunnel

# 启动应用
streamlit run stock_app.py

# 创建隧道
lt --port 8501
```

---

## 方案3：云服务器部署

### 阿里云/腾讯云

1. **购买云服务器**
- 选择Ubuntu 20.04
- 学生优惠约10元/月

2. **连接服务器**
```bash
ssh root@你的服务器IP
```

3. **安装环境**
```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3-pip -y

# 上传代码（或使用git clone）
# 方式1：使用scp上传
scp -r /本地路径/* root@服务器IP:/root/stock_app/

# 方式2：使用git
git clone <你的仓库地址>
cd stock_app
```

4. **安装依赖**
```bash
pip3 install -r requirements.txt
```

5. **运行应用**
```bash
# 前台运行（测试用）
streamlit run stock_app.py --server.port 8501 --server.address 0.0.0.0

# 后台运行（生产环境）
nohup streamlit run stock_app.py --server.port 8501 --server.address 0.0.0.0 > app.log 2>&1 &
```

6. **配置防火墙**
- 在云服务器控制台开放8501端口
- 或使用命令：
```bash
sudo ufw allow 8501
```

7. **访问应用**
- 浏览器访问：http://你的服务器IP:8501

### 使用systemd管理（推荐）

创建服务文件：
```bash
sudo nano /etc/systemd/system/stock-app.service
```

内容：
```ini
[Unit]
Description=Stock App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/stock_app
ExecStart=/usr/local/bin/streamlit run stock_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start stock-app
sudo systemctl enable stock-app
sudo systemctl status stock-app
```

---

## 方案4：Docker部署

### 本地构建和运行

```bash
# 构建镜像
docker build -t stock-app .

# 运行容器
docker run -d -p 8501:8501 --name stock-app stock-app

# 查看日志
docker logs -f stock-app
```

### 部署到云平台

#### Railway.app（推荐）
1. 访问 https://railway.app/
2. 连接GitHub仓库
3. 自动检测Dockerfile并部署
4. 免费额度：每月500小时

#### Render.com
1. 访问 https://render.com/
2. 创建新的Web Service
3. 连接GitHub仓库
4. 选择Docker部署
5. 免费版可用

---

## 推荐方案对比

| 方案 | 难度 | 费用 | 稳定性 | 适用场景 |
|------|------|------|--------|----------|
| Streamlit Cloud | ⭐ | 免费 | ⭐⭐⭐⭐ | 演示、竞赛 |
| ngrok/localtunnel | ⭐⭐ | 免费 | ⭐⭐ | 临时测试 |
| 云服务器 | ⭐⭐⭐ | 10-50元/月 | ⭐⭐⭐⭐⭐ | 长期运行 |
| Docker云平台 | ⭐⭐ | 免费/付费 | ⭐⭐⭐⭐ | 专业部署 |

## 竞赛建议

对于内部AI竞赛，推荐使用 **Streamlit Cloud**：
1. 完全免费
2. 部署简单（5分钟搞定）
3. 自动HTTPS，看起来专业
4. 可以随时更新代码
5. 提供公网访问地址

## 常见问题

### Q: 数据库会丢失吗？
A: Streamlit Cloud每次重启会重置文件系统。解决方案：
- 使用云数据库（如Supabase、MongoDB Atlas）
- 或者接受每次重启后数据重置（演示够用）

### Q: 如何配置域名？
A: 
- Streamlit Cloud：可以自定义子域名
- 云服务器：购买域名并配置DNS解析

### Q: 性能够用吗？
A: 对于演示和小规模使用完全够用。如果需要支持大量用户，建议使用云服务器。

## 需要帮助？

如果部署遇到问题，可以：
1. 检查 requirements.txt 是否完整
2. 查看部署日志
3. 确保所有文件都已上传
