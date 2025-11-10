import os
from pathlib import Path

# 应用基础配置
APP_NAME = "凡人修仙3w天"
VERSION = "1.0.0"
# 6.36英寸屏幕，按照16:9比例计算
WINDOW_WIDTH = 412  # 调整为更适合6.36英寸
WINDOW_HEIGHT = 915  # 调整高度

# 数据库配置
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "immortal_cultivation.db"

# 主题配置
class ThemeConfig:
    # 颜色配置
    PRIMARY_COLOR = "#667eea"  # 紫色主题
    PRIMARY_GRADIENT = ["#667eea", "#764ba2"]
    SUCCESS_COLOR = "#4CAF50"  # 绿色
    DANGER_COLOR = "#f5576c"   # 红色
    WARNING_COLOR = "#ffa500"  # 橙色
    GOLD_GRADIENT = ["#f6d365", "#fda085"]  # 金色渐变
    LIFE_GRADIENT = ["#f093fb", "#f5576c"]  # 生命渐变
    
    # 背景色
    BG_COLOR = "#f5f5f5"
    CARD_COLOR = "#ffffff"
    
    # 文字颜色
    TEXT_PRIMARY = "#333333"
    TEXT_SECONDARY = "#666666"
    TEXT_DISABLED = "#999999"
    
    # 尺寸配置
    PAGE_PADDING = 20
    CARD_PADDING = 15
    CARD_RADIUS = 10
    ITEM_SPACING = 10

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