# 📚 文档中心

欢迎来到 Deepin LoongArch VM Manager 的文档中心！

## 📖 文档列表

### 📘 [README.md](README.md) - 项目说明
**适合人群**: 所有用户  
**内容概要**:
- 项目介绍和功能特性
- 系统要求和安装说明
- 快速开始指南
- 配置说明和使用方法
- 项目结构和开发说明

👉 **首次使用请阅读此文档**

---

### 📗 [QUICK_START.md](QUICK_START.md) - 快速开始指南
**适合人群**: 准备推送代码到 Git 平台的用户  
**内容概要**:
- Git 仓库创建步骤
- 远程仓库配置方法
- 一键推送脚本使用
- 认证问题处理
- 常用命令速查

👉 **需要推送到 GitHub/Gitee/GitCode 时阅读**

---

### 📙 [GIT_PUSH_GUIDE.md](GIT_PUSH_GUIDE.md) - Git 推送详细指南
**适合人群**: 需要深入了解 Git 操作的用户  
**内容概要**:
- 三个平台的详细配置步骤
- HTTPS 和 SSH 认证方式详解
- 分支管理策略
- 常见问题排查
- 自动化脚本说明

👉 **遇到 Git 推送问题时查阅**

---

### 📕 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目整理总结
**适合人群**: 想了解项目整体情况的开发者  
**内容概要**:
- 项目分析结果
- 已完成工作清单
- Git 提交历史
- 文件清单和统计
- 下一步操作建议

👉 **了解项目全貌时阅读**

---

### 📔 [EXE_NAMING_RULES.md](EXE_NAMING_RULES.md) - EXE 文件命名规则
**适合人群**: 开发者和发布管理人员  
**内容概要**:
- 版本号格式详解（QML_YYMMDD_HM）
- 日期和时间代码说明
- 完整示例和查询表
- 生成的文件类型说明
- 最佳实践和使用场景

👉 **打包发布前必读**

---

### 📓 [RELEASE_GUIDE.md](RELEASE_GUIDE.md) - 发布指南
**适合人群**: 需要发布 EXE 到 Git 平台的用户  
**内容概要**:
- Releases 发布流程详解
- GitHub/Gitee/GitCode 发布步骤
- Release 描述模板
- 自动化方案（GitHub Actions）
- 版本管理策略
- 常见问题解答

👉 **准备发布 EXE 时必读**

---

### ⚡ [QUICK_RELEASE.md](QUICK_RELEASE.md) - 快速发布指南
**适合人群**: 想要快速发布的用户  
**内容概要**:
- 一键发布流程
- 完整示例演示
- 常见问题速查
- 最简操作步骤

👉 **想快速发布时看这个**

---

### 📊 [PUBLISH_CHECKLIST.md](PUBLISH_CHECKLIST.md) - 发布检查清单
**适合人群**: 需要跟踪发布进度的用户  
**内容概要**:
- 多平台发布状态跟踪
- GitCode Token 配置指南
- Release 创建步骤详解
- 最终验证清单

👉 **发布过程中随时查看**

---

### 📋 [PUBLISH_STATUS.md](PUBLISH_STATUS.md) - 发布状态报告
**适合人群**: 需要了解当前发布状态的用户  
**内容概要**:
- 各平台推送状态汇总
- Git Tag 信息
- 下一步操作指南
- 快速命令参考

👉 **查看发布进度时阅读**

---

### 📝 [RELEASE_NOTES_v260521-A4.md](RELEASE_NOTES_v260521-A4.md) - Release 说明模板
**适合人群**: 需要复制 Release 描述的用户  
**内容概要**:
- v260521-A4 版本更新内容
- Bug 修复说明
- 下载链接和系统要求
- 相关资源链接

👉 **创建 Release 时复制使用**

---

### 📄 [PUBLISH_REPORT.md](PUBLISH_REPORT.md) - 发布完成报告
**适合人群**: 已完成发布需要总结的用户  
**内容概要**:
- 完整的发布流程回顾
- 代码提交和 EXE 打包状态
- Git Tag 创建情况
- 各平台操作指南

👉 **发布完成后归档参考**

---

## 🎯 快速导航

### 我是新用户，想开始使用
→ 阅读 [README.md](README.md)

### 我想把代码推送到 Git 平台
→ 先看 [QUICK_START.md](QUICK_START.md)，遇到问题再看 [GIT_PUSH_GUIDE.md](GIT_PUSH_GUIDE.md)

### 我想了解项目的详细信息
→ 阅读 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

### 我需要打包程序为 EXE
→ 查看 [README.md](README.md) 中的"打包为可执行文件"章节  
→ 了解版本命名规则：[EXE_NAMING_RULES.md](EXE_NAMING_RULES.md)

### 我要发布新版本
→ **快速方式**: 查看 [QUICK_RELEASE.md](QUICK_RELEASE.md)  
→ **详细指南**: 阅读 [RELEASE_GUIDE.md](RELEASE_GUIDE.md)  
→ **命名规范**: 先了解 [EXE_NAMING_RULES.md](EXE_NAMING_RULES.md)

---

## 📂 项目结构

```
LoongarchWorkstationManagerGui/
├── docs/                      # 📚 文档目录（你在这里）
│   ├── README.md             # 项目说明
│   ├── QUICK_START.md        # 快速开始
│   ├── GIT_PUSH_GUIDE.md     # Git 推送指南
│   ├── PROJECT_SUMMARY.md    # 项目总结
│   └── EXE_NAMING_RULES.md   # EXE 命名规则 ⭐新增
├── vm_manager.py              # 主程序
├── build_exe.py               # 打包脚本
├── setup.py                   # 安装配置
├── requirements.txt           # 依赖列表
├── push_all.bat               # Windows 推送脚本
├── push_all.sh                # Linux/Mac 推送脚本
└── icon.ico                   # 应用图标
```

---

## 💡 提示

- 所有文档都使用 Markdown 格式，可以在 GitHub/Gitee/GitCode 上直接查看
- 建议使用支持 Markdown 预览的编辑器（如 VS Code）阅读
- 文档会随项目更新而更新，请定期查看最新版本

---

**最后更新**: 2026-05-21