# 部署到 Streamlit Cloud 检查清单

## 问题：stock_app.py This file does not exist

这个错误说明文件没有正确上传到 GitHub。请按以下步骤检查：

## 步骤1：检查 Git 状态

```bash
# 查看当前状态
git status

# 应该看到哪些文件被追踪
```

## 步骤2：确保所有必要文件都被添加

```bash
# 添加所有必要文件
git add stock_app.py
git add pages_trading.py
git add trading_db.py
git add config.py
git add requirements.txt
git add .streamlit/config.toml

# 或者一次性添加所有文件
git add .

# 查看将要提交的文件
git status
```

## 步骤3：提交并推送

```bash
# 提交
git commit -m "Add stock app files"

# 推送到 GitHub
git push origin main

# 如果是第一次推送，可能需要：
git push -u origin main
```

## 步骤4：在 GitHub 上验证

1. 访问你的 GitHub 仓库页面
2. 确认以下文件都存在：
   - ✅ stock_app.py
   - ✅ pages_trading.py
   - ✅ trading_db.py
   - ✅ config.py
   - ✅ requirements.txt
   - ✅ .streamlit/config.toml

## 步骤5：在 Streamlit Cloud 重新部署

1. 访问 https://share.streamlit.io/
2. 点击 "New app"
3. 填写信息：
   - Repository: 你的仓库名（例如：username/stock-app）
   - Branch: main
   - Main file path: stock_app.py
4. 点击 "Deploy"

## 常见问题

### Q1: 如果没有 .git 目录怎么办？

```bash
# 初始化 git
git init

# 添加远程仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 添加文件
git add .

# 提交
git commit -m "Initial commit"

# 推送
git push -u origin main
```

### Q2: 推送时提示需要登录

```bash
# 配置 git 用户信息
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 如果需要，设置 GitHub token
# 访问 https://github.com/settings/tokens 创建 token
# 推送时使用 token 作为密码
```

### Q3: 推送被拒绝（rejected）

```bash
# 先拉取远程更改
git pull origin main --allow-unrelated-histories

# 再推送
git push origin main
```

## 必需文件清单

确保以下文件都在 GitHub 仓库中：

### 核心文件（必须）
- [x] stock_app.py - 主应用文件
- [x] pages_trading.py - 交易页面
- [x] trading_db.py - 数据库管理
- [x] config.py - 配置文件
- [x] requirements.txt - 依赖列表

### 配置文件（可选但推荐）
- [x] .streamlit/config.toml - Streamlit 配置

### 文档文件（可选）
- [ ] README.md - 项目说明
- [ ] DEPLOYMENT.md - 部署指南
- [ ] USAGE_GUIDE.md - 使用指南

## 快速命令（复制粘贴）

```bash
# 一键部署命令
git add stock_app.py pages_trading.py trading_db.py config.py requirements.txt .streamlit/
git commit -m "Deploy to Streamlit Cloud"
git push origin main
```

## 验证部署

部署成功后，你会得到一个地址，类似：
- https://your-app-name.streamlit.app

访问这个地址，应该能看到你的应用。

## 如果还是不行

1. 检查 GitHub 仓库是否是 public（公开）
2. 确认分支名是 main 还是 master
3. 查看 Streamlit Cloud 的部署日志
4. 尝试删除应用重新部署
