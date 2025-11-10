# GitHub 打包与部署指南

## 📋 目录
1. [自动构建配置](#自动构建配置)
2. [发布新版本](#发布新版本)
3. [手动触发构建](#手动触发构建)
4. [下载构建产物](#下载构建产物)
5. [故障排除](#故障排除)

---

## 🔧 自动构建配置

### 已配置的 Workflows

项目包含两个 GitHub Actions workflows：

#### 1. **build-apk.yml** - 持续构建
- **触发条件**：
  - 推送到 `main` 或 `master` 分支
  - Pull Request 到主分支
  - 推送版本标签（如 `v1.0.0`）
  - 手动触发

- **功能**：
  - 自动构建 Android APK
  - 将 APK 上传为 Artifacts（保留 30 天）
  - 自动版本命名

#### 2. **release.yml** - 发布版本
- **触发条件**：
  - 推送版本标签（如 `v1.0.0`, `v2.1.3`）

- **功能**：
  - 构建 APK
  - 创建 GitHub Release
  - 自动生成发布说明
  - 上传 APK 到 Release

---

## 🚀 发布新版本

### 步骤 1: 准备发布

1. **更新版本信息**：
   ```bash
   # 编辑 VERSION.md 文件，更新版本号和更新说明
   ```

2. **提交更改**：
   ```bash
   git add .
   git commit -m "chore: prepare for release v1.0.0"
   git push origin main
   ```

### 步骤 2: 创建版本标签

```bash
# 创建带注释的标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签到 GitHub
git push origin v1.0.0
```

### 步骤 3: 自动构建和发布

推送标签后，GitHub Actions 会自动：
1. 触发 `release.yml` workflow
2. 构建 Android APK
3. 创建 GitHub Release
4. 上传 APK 文件到 Release

### 步骤 4: 查看发布

访问 GitHub 仓库的 Releases 页面：
```
https://github.com/l2054475689-afk/Congxiaorong/releases
```

---

## 🎯 手动触发构建

### 通过 GitHub 网页界面

1. 访问仓库的 **Actions** 标签页
2. 选择 **Build Android APK** workflow
3. 点击 **Run workflow** 按钮
4. 选择分支（默认 main）
5. 点击 **Run workflow** 确认

### 通过 GitHub CLI (gh)

```bash
# 安装 GitHub CLI
# https://cli.github.com/

# 手动触发构建
gh workflow run build-apk.yml

# 查看运行状态
gh run list --workflow=build-apk.yml
```

---

## 📥 下载构建产物

### 方式 1: 从 Artifacts 下载（开发构建）

1. 访问仓库的 **Actions** 标签页
2. 点击最近的 workflow 运行
3. 在 **Artifacts** 部分找到 APK
4. 点击下载

**注意**：Artifacts 保留 30 天后自动删除

### 方式 2: 从 Releases 下载（正式版本）

1. 访问 **Releases** 页面
2. 选择需要的版本
3. 在 **Assets** 部分下载 APK 文件

**推荐**：正式版本永久保存

---

## 🔍 故障排除

### 问题 1: 构建失败

**检查步骤**：
1. 访问 Actions 页面查看错误日志
2. 常见原因：
   - Python 依赖问题：检查 `pip install` 步骤
   - Flet 构建错误：检查 `main_mobile.py` 文件
   - 权限问题：确保仓库设置正确

**解决方案**：
```bash
# 本地测试构建
flet build apk --module main_mobile

# 检查 Python 版本
python --version  # 应该是 3.10+

# 重新安装依赖
pip install --upgrade flet
```

### 问题 2: Release 创建失败

**可能原因**：
- 权限不足：检查 workflow 的 `permissions` 设置
- 标签格式错误：必须是 `v*` 格式（如 v1.0.0）
- APK 文件未找到：检查构建步骤

**解决方案**：
```bash
# 删除错误的标签
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# 重新创建正确的标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 问题 3: APK 文件损坏或无法安装

**检查**：
1. 下载的 APK 文件大小是否正常
2. 在 Actions 日志中查看 "Get APK info" 步骤

**解决方案**：
```bash
# 本地构建测试
flet build apk --module main_mobile

# 检查生成的 APK
ls -lh build/apk/
```

### 问题 4: Workflow 权限错误

**错误信息**：
```
Permission denied: cannot create release
```

**解决方案**：
1. 访问仓库 **Settings** → **Actions** → **General**
2. 在 "Workflow permissions" 部分选择：
   - **Read and write permissions**
3. 保存更改
4. 重新运行 workflow

---

## 📚 进阶配置

### 自定义版本号格式

编辑 `.github/workflows/build-apk.yml`：

```yaml
- name: Get version info
  id: version
  run: |
    if [[ $GITHUB_REF == refs/tags/* ]]; then
      VERSION=${GITHUB_REF#refs/tags/}
    else
      # 自定义开发版本格式
      VERSION="dev-$(git rev-parse --short HEAD)"
    fi
    echo "version=$VERSION" >> $GITHUB_OUTPUT
```

### 添加构建通知

在 workflow 末尾添加：

```yaml
- name: Send notification
  if: success()
  run: |
    echo "Build successful! Version: ${{ steps.version.outputs.version }}"
    # 可以集成 Slack, Discord 等通知服务
```

### 多平台构建

可以扩展 workflow 支持 iOS 和 Windows：

```yaml
jobs:
  build-android:
    # ... Android 构建步骤

  build-ios:
    runs-on: macos-latest
    steps:
      # ... iOS 构建步骤

  build-windows:
    runs-on: windows-latest
    steps:
      # ... Windows 构建步骤
```

---

## 🎓 最佳实践

1. **语义化版本控制**：
   - 主版本号：重大变更（v2.0.0）
   - 次版本号：新功能（v1.1.0）
   - 修订号：Bug 修复（v1.0.1）

2. **发布前测试**：
   - 推送代码前本地测试构建
   - 使用 PR 触发自动构建测试
   - 标签发布前确保主分支稳定

3. **文档更新**：
   - 每次发布更新 VERSION.md
   - 在 Release 说明中详细描述更改
   - 保持 README.md 信息最新

4. **备份重要版本**：
   - 定期备份 Release 文件
   - 保存构建日志用于问题追踪

---

## 📞 获取帮助

- **GitHub Actions 文档**: https://docs.github.com/actions
- **Flet 文档**: https://flet.dev/docs/
- **问题反馈**: 在仓库创建 Issue

---

**最后更新**: 2025-01-24
**文档版本**: 1.0.0
