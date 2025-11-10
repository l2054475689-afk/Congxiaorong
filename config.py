import os
import sys
from pathlib import Path

# 应用基础配置
APP_NAME = "凡人修仙3w天"
VERSION = "1.0.0"
# 6.36英寸屏幕，按照16:9比例计算
WINDOW_WIDTH = 412  # 调整为更适合6.36英寸
WINDOW_HEIGHT = 915  # 调整高度

# 数据库配置 - 优化为支持Android
def get_app_data_dir():
    """获取应用数据目录（支持跨平台）"""
    try:
        # 尝试检测Android环境
        if 'ANDROID_STORAGE' in os.environ or sys.platform == 'android':
            # Android平台使用内部存储
            try:
                from android.storage import app_storage_path
                return Path(app_storage_path())
            except:
                # 如果导入失败，使用临时目录
                import tempfile
                app_data = Path(tempfile.gettempdir()) / 'fanrenxiuxian'
                app_data.mkdir(exist_ok=True)
                return app_data
        elif os.name == 'nt':  # Windows
            app_data = os.path.expanduser('~\\AppData\\Local\\FanRenXiuXian')
        else:  # Linux/Mac
            app_data = os.path.expanduser('~/.fanrenxiuxian')

        # 创建目录如果不存在
        os.makedirs(app_data, exist_ok=True)
        return Path(app_data)
    except Exception as e:
        print(f"获取应用数据目录失败: {e}")
        # 如果以上都失败，使用临时目录
        import tempfile
        fallback_dir = Path(tempfile.gettempdir()) / 'fanrenxiuxian'
        fallback_dir.mkdir(exist_ok=True)
        return fallback_dir

BASE_DIR = get_app_data_dir()
DB_PATH = BASE_DIR / "immortal_cultivation.db"

# 主题配置
class ThemeConfig:
    # 主色调 - 仙侠紫金配色
    PRIMARY_COLOR = "#8B5CF6"  # 紫色主题（更鲜艳）
    PRIMARY_LIGHT = "#A78BFA"  # 浅紫色
    PRIMARY_DARK = "#7C3AED"   # 深紫色
    SECONDARY_COLOR = "#F59E0B"  # 金色辅助色

    # 渐变色配置
    PRIMARY_GRADIENT = ["#8B5CF6", "#EC4899"]  # 紫粉渐变
    GOLD_GRADIENT = ["#F59E0B", "#FBBF24", "#FCD34D"]  # 金色渐变
    LIFE_GRADIENT = ["#EF4444", "#F87171"]  # 生命渐变
    SPIRIT_GRADIENT = ["#06B6D4", "#22D3EE"]  # 心境渐变
    REALM_GRADIENT = ["#8B5CF6", "#6366F1", "#3B82F6"]  # 境界渐变
    SUCCESS_GRADIENT = ["#10B981", "#34D399"]  # 成功渐变

    # 功能色
    SUCCESS_COLOR = "#10B981"  # 绿色
    DANGER_COLOR = "#EF4444"   # 红色
    WARNING_COLOR = "#F59E0B"  # 橙色
    INFO_COLOR = "#3B82F6"     # 蓝色

    # 背景色
    BG_COLOR = "#F8FAFC"  # 浅灰蓝背景
    BG_GRADIENT = ["#F8FAFC", "#F1F5F9"]  # 背景渐变
    CARD_COLOR = "#FFFFFF"
    CARD_HOVER = "#FAFAFA"

    # 文字颜色
    TEXT_PRIMARY = "#1E293B"  # 深灰蓝
    TEXT_SECONDARY = "#64748B"  # 中灰
    TEXT_DISABLED = "#94A3B8"  # 浅灰
    TEXT_INVERSE = "#FFFFFF"  # 白色文字

    # 边框颜色
    BORDER_COLOR = "#E2E8F0"
    BORDER_LIGHT = "#F1F5F9"

    # 阴影配置
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

    # 尺寸配置
    PAGE_PADDING = 20
    CARD_PADDING = 20
    CARD_RADIUS = 16  # 更大的圆角
    ITEM_SPACING = 12
    SECTION_SPACING = 24

# 游戏设定
class GameConfig:
    # 生命设定
    MAX_AGE = 80  # 最大年龄
    MINUTES_PER_DAY = 24 * 60  # 每天消耗的血量
    BLOOD_DECREASE_PER_MINUTE = 1  # 每分钟减少的血量
    
    # 心境设定
    MIN_SPIRIT = -80
    MAX_SPIRIT = 200
    DEFAULT_SPIRIT = 0
    
    # 灵石设定
    DEFAULT_TARGET_MONEY = 5000000  # 默认目标500万
    
    # 境界等级
    REALM_LEVELS = ["练气期", "筑基期", "结丹期", "元婴期", "化神期"]