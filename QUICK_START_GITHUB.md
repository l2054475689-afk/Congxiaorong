# 快速开始 - GitHub 自动打包

## 🎯 已完成的配置

✅ GitHub Actions 自动构建配置
✅ 自动发布 Release 配置
✅ 版本管理系统
✅ 部署文档

## 🚀 立即使用

### 1️⃣ 推送代码到 GitHub

```bash
# 添加所有文件
git add .

# 提交更改
git commit -m "feat: add GitHub Actions workflows for APK building"

# 推送到 GitHub
git push origin main
```

推送后，GitHub Actions 会自动构建 APK！

### 2️⃣ 查看构建进度

1. 访问你的 GitHub 仓库
2. 点击 **Actions** 标签
3. 查看 "Build Android APK" 运行状态

### 3️⃣ 下载 APK

构建完成后：
1. 点击完成的 workflow 运行
2. 在页面底部找到 **Artifacts**
3. 下载 APK 文件

## 🎊 发布正式版本

当你准备发布正式版本时：

```bash
# 创建版本标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0
```

GitHub 会自动：
- ✅ 构建 APK
- ✅ 创建 Release
- ✅ 上传 APK 到 Release 页面

访问 `https://github.com/你的用户名/仓库名/releases` 查看！

## 📋 需要配置的权限（如果遇到权限错误）

1. 访问仓库 **Settings** → **Actions** → **General**
2. 在 "Workflow permissions" 选择：**Read and write permissions**
3. 勾选 "Allow GitHub Actions to create and approve pull requests"
4. 保存

## 📚 详细文档

- **完整部署指南**: 查看 `DEPLOYMENT_GUIDE.md`
- **版本信息**: 查看 `VERSION.md`
- **故障排除**: 参考部署指南中的故障排除章节

## 🎁 额外功能

### 手动触发构建
在 Actions 页面点击 "Build Android APK" → "Run workflow"

### 自动化场景
- 每次 push 到 main 分支 → 自动构建
- 创建 PR → 自动构建测试
- 推送版本标签 → 自动发布 Release

---

**开始使用**: 运行上面的 git 命令即可！🚀
