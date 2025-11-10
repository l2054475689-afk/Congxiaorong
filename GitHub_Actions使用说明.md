# GitHub Actions 自动打包 APK 使用说明

## 前提条件

1. 在 GitHub 上创建一个仓库
2. 将项目代码推送到 GitHub

## 使用步骤

### 1. 初始化 Git 仓库（如果还没有）

```bash
# 在项目目录下执行
git init
git add .
git commit -m "Initial commit"
```

### 2. 创建 .gitignore 文件

项目中已包含 `.gitignore` 文件，会自动排除以下内容：
- `__pycache__/`
- `*.pyc`
- `build/`
- `*.db`
- `*.db-shm`
- `*.db-wal`
- 等其他临时文件

### 3. 连接到 GitHub 仓库

```bash
# 创建 GitHub 仓库后，执行以下命令
git remote add origin https://github.com/你的用户名/你的仓库名.git
git branch -M main
git push -u origin main
```

### 4. 触发自动打包

GitHub Actions 会在以下情况自动运行：

#### 方式 1: 自动触发
- 当您推送代码到 `main` 或 `master` 分支时
- 当有 Pull Request 时

```bash
# 修改代码后
git add .
git commit -m "更新代码"
git push
```

#### 方式 2: 手动触发
1. 访问 GitHub 仓库页面
2. 点击 "Actions" 选项卡
3. 选择 "Build Android APK" 工作流
4. 点击 "Run workflow" 按钮
5. 选择分支（通常是 main）
6. 点击绿色的 "Run workflow" 按钮

### 5. 下载生成的 APK

1. 在 GitHub 仓库的 "Actions" 页面查看工作流运行状态
2. 等待构建完成（通常需要 5-10 分钟）
3. 点击已完成的工作流
4. 在页面底部的 "Artifacts" 部分找到 `app-release-apk`
5. 点击下载 APK 文件

## 工作流说明

GitHub Actions 工作流会自动执行以下步骤：

1. ✅ 检出代码
2. ✅ 设置 Python 3.10 环境
3. ✅ 安装 Flet 及依赖
4. ✅ 构建 Android APK
5. ✅ 上传 APK 文件（保留 30 天）

## 优势

- ✅ **无需本地环境**：不需要在 Windows 上配置复杂的 Android 开发环境
- ✅ **避免编码问题**：在 Linux 环境中运行，避免 Windows GBK 编码问题
- ✅ **自动化**：代码更新后自动打包
- ✅ **免费**：GitHub Actions 对公开仓库免费
- ✅ **可追溯**：每次构建都有完整的日志

## 故障排除

### 构建失败

1. 查看 Actions 日志，找到错误信息
2. 常见问题：
   - 依赖包问题：检查 `requirements.txt`
   - 代码错误：确保代码在本地可以运行
   - Flutter 版本问题：Flet 会自动下载合适的 Flutter 版本

### 私有仓库

如果您的仓库是私有的：
- 免费账户每月有 2000 分钟的免费额度
- 超出后需要付费

## 本地测试（可选）

如果想在推送到 GitHub 前本地测试：

```bash
# 使用 act 工具在本地运行 GitHub Actions
# 需要先安装 Docker 和 act
act -j build
```

## 配置文件位置

- GitHub Actions 配置：`.github/workflows/build-apk.yml`
- 应用配置：`flet.toml`
- 依赖列表：`requirements.txt`
- 移动端入口：`main_mobile.py`

## 自定义配置

如需修改构建配置，可以编辑 `.github/workflows/build-apk.yml`：

```yaml
# 修改 Python 版本
python-version: '3.11'

# 添加其他构建选项
flet build apk --module main_mobile --build-version 1.0.1
```

## 注意事项

1. 确保 `requirements.txt` 包含所有必需的依赖
2. 不要提交敏感信息（密码、密钥等）到 GitHub
3. APK 文件会在 Actions 中保留 30 天
4. 首次运行可能需要更长时间（下载依赖）

## 后续步骤

1. 将代码推送到 GitHub
2. 等待自动构建完成
3. 下载 APK 并在 Android 设备上测试
4. 如有问题，查看构建日志进行调试

---

**祝您打包顺利！** 🎉
