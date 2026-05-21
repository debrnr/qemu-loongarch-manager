#!/bin/bash

echo "========================================"
echo "  Deepin VM Manager - 推送到所有平台"
echo "========================================"
echo ""

# 检查是否有未提交的更改
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  检测到未提交的更改！"
    echo ""
    read -p "是否先提交这些更改？(y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "请输入提交说明: " commit_msg
        git commit -m "$commit_msg"
        echo ""
    fi
fi

echo "📤 开始推送到远程仓库..."
echo ""

# 推送到 GitHub
echo "[1/3] 推送到 GitHub..."
git push origin master
if [ $? -ne 0 ]; then
    echo "❌ GitHub 推送失败！"
    exit 1
fi
echo "✅ GitHub 推送成功"
echo ""

# 推送到 Gitee
echo "[2/3] 推送到 Gitee..."
git push gitee master
if [ $? -ne 0 ]; then
    echo "⚠️  Gitee 推送失败（可能未配置）"
else
    echo "✅ Gitee 推送成功"
fi
echo ""

# 推送到 GitCode
echo "[3/3] 推送到 GitCode..."
git push gitcode master
if [ $? -ne 0 ]; then
    echo "⚠️  GitCode 推送失败（可能未配置）"
else
    echo "✅ GitCode 推送成功"
fi
echo ""

echo "========================================"
echo "  🎉 推送完成！"
echo "========================================"
