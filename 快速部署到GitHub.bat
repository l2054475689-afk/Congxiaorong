@echo off
chcp 65001 >nul
echo ========================================
echo  凡人修仙3w天 - GitHub Actions 快速部署
echo ========================================
echo.

echo 步骤 1: 检查 Git 是否已安装
git --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Git，请先安装 Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [✓] Git 已安装

echo.
echo 步骤 2: 初始化 Git 仓库
if not exist ".git" (
    git init
    echo [✓] Git 仓库已初始化
) else (
    echo [✓] Git 仓库已存在
)

echo.
echo 步骤 3: 配置 Git（如果尚未配置）
git config user.name >nul 2>&1
if errorlevel 1 (
    set /p git_name="请输入您的 Git 用户名: "
    git config user.name "%git_name%"
)
git config user.email >nul 2>&1
if errorlevel 1 (
    set /p git_email="请输入您的 Git 邮箱: "
    git config user.email "%git_email%"
)

echo.
echo 步骤 4: 添加所有文件到暂存区
git add .
echo [✓] 文件已添加

echo.
echo 步骤 5: 创建初始提交
git commit -m "Initial commit: 凡人修仙3w天应用 + GitHub Actions自动打包配置" >nul 2>&1
if errorlevel 1 (
    echo [提示] 没有新的更改需要提交，或已经提交过
) else (
    echo [✓] 提交已创建
)

echo.
echo ========================================
echo  接下来请手动操作:
echo ========================================
echo.
echo 1. 在 GitHub 上创建一个新仓库
echo    访问: https://github.com/new
echo.
echo 2. 复制仓库 URL（例如: https://github.com/用户名/仓库名.git）
echo.
echo 3. 在下面输入仓库 URL，然后按回车
echo.
set /p repo_url="请输入 GitHub 仓库 URL: "

if "%repo_url%"=="" (
    echo [错误] 未输入仓库 URL
    pause
    exit /b 1
)

echo.
echo 步骤 6: 添加远程仓库
git remote add origin "%repo_url%" 2>nul
if errorlevel 1 (
    echo [提示] 远程仓库可能已存在，尝试更新...
    git remote set-url origin "%repo_url%"
)
echo [✓] 远程仓库已配置

echo.
echo 步骤 7: 推送到 GitHub
echo [提示] 需要输入 GitHub 用户名和密码（或Personal Access Token）
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo [错误] 推送失败，可能的原因:
    echo - 网络问题
    echo - 认证失败（需要 Personal Access Token）
    echo - 仓库已存在内容
    echo.
    echo 解决方案:
    echo 1. 检查网络连接
    echo 2. 使用 Personal Access Token 而不是密码
    echo    创建Token: https://github.com/settings/tokens
    echo 3. 如果仓库有内容，可以尝试: git pull origin main --rebase
    pause
    exit /b 1
)

echo.
echo ========================================
echo  部署成功! 🎉
echo ========================================
echo.
echo 下一步:
echo 1. 访问您的 GitHub 仓库
echo 2. 点击 "Actions" 选项卡
echo 3. 查看自动打包进度
echo 4. 等待完成后下载 APK 文件
echo.
echo 说明文档: GitHub_Actions使用说明.md
echo.
pause
