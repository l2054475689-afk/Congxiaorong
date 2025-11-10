@echo off
title 凡人修仙3w天 - 增强版启动器
color 0b

echo.
echo     ╔══════════════════════════════════════════════════════╗
echo     ║                凡人修仙3w天 - 增强版                   ║
echo     ║                                                      ║
echo     ║  🌟 第三阶段：优化提升版本                             ║
echo     ║  📊 报告导出 ^| 💾 数据备份 ^| 🎨 UI美化               ║
echo     ║  📈 图表组件 ^| ⚡ 性能优化 ^| 📐 布局改善               ║
echo     ║                                                      ║
echo     ║  版本: v3.0.0                                        ║
echo     ╚══════════════════════════════════════════════════════╝
echo.

echo 🚀 正在启动增强版应用...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python，请先安装Python 3.8+
    echo 下载地址：https://python.org/downloads/
    pause
    exit /b 1
)

REM 检查是否在正确目录
if not exist "run_enhanced.py" (
    echo ❌ 错误：请确保此批处理文件在 mortal_3W_day_1 目录中运行
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 📦 检查依赖包...
python -c "import flet" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  检测到缺少依赖包，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo ✅ 依赖检查完成
echo.

REM 启动应用
echo 🎯 启动增强版用户界面...
echo.
python run_enhanced.py

REM 检查退出状态
if errorlevel 1 (
    echo.
    echo ❌ 应用程序异常退出
    echo 请查看错误信息或联系技术支持
) else (
    echo.
    echo ✅ 应用程序正常退出
)

echo.
echo 感谢使用凡人修仙3w天增强版！
pause 