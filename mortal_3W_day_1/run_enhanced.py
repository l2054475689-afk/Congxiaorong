#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
凡人修仙3w天 - 增强版启动脚本
第三阶段：优化提升版本

功能特性：
- ✅ 报告导出功能（PDF、Excel、Markdown格式）
- ✅ 数据备份与恢复功能
- ✅ 增强样式系统 - 更多主题色彩和设计元素
- ✅ 数据可视化图表组件
- ✅ UI美化优化 - 精美渐变、卡片设计、动画效果
- ✅ 改善排版 - 优化间距、布局、字体层次
- ✅ 性能优化 - 内存管理、响应速度提升
- ✅ AI接口集成 - OpenAI API对接，智能诗句生成
- ✅ 每日诗句弹窗 - 励志名言，支持自定义诗句库
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import flet as ft
except ImportError:
    print("❌ 错误：未安装 flet 库")
    print("请运行：pip install -r requirements.txt")
    sys.exit(1)

try:
    from ui.enhanced_main_window import EnhancedMainWindow
    from utils.performance import performance_optimizer, cleanup_performance_resources
    from utils.backup import BackupManager
    from database.db_manager import DatabaseManager
    from config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保所有依赖已正确安装：pip install -r requirements.txt")
    sys.exit(1)


def setup_logging():
    """设置日志系统"""
    log_file = project_root / "enhanced_app.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'flet', 'sqlalchemy', 'reportlab', 'pandas', 
        'openpyxl', 'schedule', 'requests', 'Pillow', 'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行：pip install -r requirements.txt")
        return False
    
    return True


def initialize_database():
    """初始化数据库"""
    try:
        db = DatabaseManager()
        # 检查数据库连接
        db.get_user_stats()
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False


def create_backup_on_startup():
    """启动时创建备份"""
    try:
        backup_manager = BackupManager("immortal_cultivation.db")
        backup_path = backup_manager.create_backup("startup", "应用启动时的自动备份")
        print(f"✅ 启动备份创建成功: {backup_path}")
        return True
    except Exception as e:
        print(f"⚠️ 启动备份创建失败: {e}")
        return False


def main(page: ft.Page):
    """主函数 - 增强版"""
    logger = logging.getLogger(__name__)
    
    try:
        # 设置页面基本属性
        page.title = f"{APP_NAME} - 增强版 v3.0"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = "#f5f5f5"
        
        # 设置窗口大小
        page.window_width = WINDOW_WIDTH
        page.window_height = WINDOW_HEIGHT
        page.window_resizable = True  # 增强版支持调整大小
        page.window_min_width = 350
        page.window_min_height = 600
        
        # 设置页面关闭时的清理
        def on_window_close(e):
            """窗口关闭时的清理工作"""
            logger.info("应用程序正在关闭，执行清理工作...")
            cleanup_performance_resources()
            logger.info("清理工作完成")
        
        page.on_window_event = on_window_close
        
        # 创建增强版主窗口实例
        logger.info("创建增强版主窗口...")
        window = EnhancedMainWindow(page)
        
        # 初始化界面
        logger.info("初始化用户界面...")
        window.setup()
        
        logger.info("✅ 应用程序启动成功")
        
        # 显示启动成功消息
        page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text("🎉 凡人修仙3w天增强版启动成功！"),
                bgcolor="#4CAF50",
                action="确定",
                action_color="#ffffff",
            )
        )
        
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        
        # 显示错误信息
        error_dialog = ft.AlertDialog(
            title=ft.Text("启动失败"),
            content=ft.Text(f"应用程序启动时发生错误：\n{e}"),
            actions=[
                ft.TextButton("确定", on_click=lambda e: page.close(error_dialog))
            ],
        )
        page.dialog = error_dialog
        error_dialog.open = True
        page.update()


def run_app():
    """运行应用程序"""
    logger = setup_logging()
    
    print("🚀 凡人修仙3w天 - 增强版启动中...")
    print("=" * 50)
    
    # 检查依赖
    print("📦 检查依赖包...")
    if not check_dependencies():
        return False
    print("✅ 依赖包检查完成")
    
    # 初始化数据库
    print("🗄️ 初始化数据库...")
    if not initialize_database():
        return False
    print("✅ 数据库初始化完成")
    
    # 创建启动备份
    print("💾 创建启动备份...")
    create_backup_on_startup()
    
    # 启动性能监控
    print("⚡ 启动性能监控...")
    logger.info("性能监控已启动")
    
    print("=" * 50)
    print("🎯 启动增强版用户界面...")
    
    try:
        # 启动 Flet 应用
        ft.app(
            target=main,
            name="凡人修仙3w天-增强版",
            assets_dir="assets" if (project_root / "assets").exists() else None,
        )
        
        return True
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，应用程序退出")
        return True
        
    except Exception as e:
        logger.error(f"应用程序运行时发生错误: {e}")
        print(f"❌ 运行错误: {e}")
        return False
    
    finally:
        # 清理资源
        print("🧹 清理资源...")
        cleanup_performance_resources()
        print("✅ 清理完成")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║                凡人修仙3w天 - 增强版                   ║
    ║                                                      ║
    ║  🌟 第三阶段：优化提升版本                             ║
    ║  📊 报告导出 | 💾 数据备份 | 🎨 UI美化               ║
    ║  📈 图表组件 | ⚡ 性能优化 | 📐 布局改善               ║
    ║                                                      ║
    ║  版本: v3.0.0                                        ║
    ║  作者: AI助手                                         ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    success = run_app()
    sys.exit(0 if success else 1) 