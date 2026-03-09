#!/bin/bash

# A股行情中心 - 一键部署到 GitHub 脚本

echo "🚀 开始部署到 GitHub..."

# 检查是否在 git 仓库中
if [ ! -d ".git" ]; then
    echo "❌ 错误：当前目录不是 git 仓库"
    echo "请先运行: git init"
    exit 1
fi

# 添加必要文件
echo "📦 添加文件..."
git add stock_app.py
git add pages_trading.py
git add trading_db.py
git add config.py
git add requirements.txt
git add .streamlit/config.toml
git add .gitignore

# 添加文档文件（如果存在）
git add README.md 2>/dev/null
git add DEPLOYMENT.md 2>/dev/null
git add USAGE_GUIDE.md 2>/dev/null

# 显示将要提交的文件
echo ""
echo "📋 将要提交的文件："
git status --short

# 确认
echo ""
read -p "确认提交这些文件？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 取消部署"
    exit 1
fi

# 提交
echo ""
echo "💾 提交更改..."
git commit -m "Deploy: Update stock app $(date +%Y-%m-%d)"

# 推送
echo ""
echo "⬆️  推送到 GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 部署成功！"
    echo ""
    echo "📝 下一步："
    echo "1. 访问你的 GitHub 仓库，确认文件已上传"
    echo "2. 访问 https://share.streamlit.io/"
    echo "3. 点击 'New app' 并选择你的仓库"
    echo "4. Main file path 填写: stock_app.py"
    echo "5. 点击 'Deploy'"
else
    echo ""
    echo "❌ 推送失败"
    echo "请检查："
    echo "1. 是否已设置远程仓库: git remote -v"
    echo "2. 是否有推送权限"
    echo "3. 网络连接是否正常"
fi
