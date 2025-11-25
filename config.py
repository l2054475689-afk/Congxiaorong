# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

# Application Configuration
APP_NAME = "FanRen XiuXian 3W Day"
VERSION = "1.0.0"
# Screen size: 6.36 inch, 16:9 ratio
WINDOW_WIDTH = 412
WINDOW_HEIGHT = 915

# Database Configuration - Android compatible
def get_app_data_dir():
    """Get app data directory (cross-platform)"""
    try:
        # Detect Android environment
        if 'ANDROID_STORAGE' in os.environ or sys.platform == 'android' or hasattr(sys, 'getandroidapilevel'):
            # Android: use current working directory (Flet auto-sets to app private dir)
            try:
                app_data = Path.cwd() / 'data'
                app_data.mkdir(exist_ok=True)
                return app_data
            except Exception as e:
                # Android fallback: use /data/data directory
                try:
                    app_data = Path('/data/data') / 'com.fanrenxiuxian.app' / 'files' / 'data'
                    app_data.mkdir(parents=True, exist_ok=True)
                    return app_data
                except:
                    # Final fallback: temp directory
                    import tempfile
                    app_data = Path(tempfile.gettempdir()) / 'fanrenxiuxian' / 'data'
                    app_data.mkdir(parents=True, exist_ok=True)
                    return app_data
        elif os.name == 'nt':  # Windows
            app_data = Path(os.path.expanduser('~\\AppData\\Local\\FanRenXiuXian'))
        else:  # Linux/Mac
            app_data = Path(os.path.expanduser('~/.fanrenxiuxian'))

        # Create directory if not exists
        app_data.mkdir(parents=True, exist_ok=True)
        return app_data
    except Exception as e:
        # Final fallback: temp directory
        import tempfile
        fallback_dir = Path(tempfile.gettempdir()) / 'fanrenxiuxian'
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir

# Delayed initialization to avoid import-time errors
BASE_DIR = None
DB_PATH = None

def init_paths():
    """Initialize paths (delayed initialization)"""
    global BASE_DIR, DB_PATH
    if BASE_DIR is None:
        BASE_DIR = get_app_data_dir()
        DB_PATH = BASE_DIR / "immortal_cultivation.db"
    return BASE_DIR, DB_PATH

# Theme Configuration
class ThemeConfig:
    # Primary colors - Purple and Gold theme
    PRIMARY_COLOR = "#8B5CF6"  # Purple
    PRIMARY_LIGHT = "#A78BFA"  # Light purple
    PRIMARY_DARK = "#7C3AED"   # Dark purple
    SECONDARY_COLOR = "#F59E0B"  # Gold

    # Gradient colors
    PRIMARY_GRADIENT = ["#8B5CF6", "#EC4899"]  # Purple-Pink gradient
    GOLD_GRADIENT = ["#F59E0B", "#FBBF24", "#FCD34D"]  # Gold gradient
    LIFE_GRADIENT = ["#EF4444", "#F87171"]  # Life gradient
    SPIRIT_GRADIENT = ["#06B6D4", "#22D3EE"]  # Spirit gradient
    REALM_GRADIENT = ["#8B5CF6", "#6366F1", "#3B82F6"]  # Realm gradient
    SUCCESS_GRADIENT = ["#10B981", "#34D399"]  # Success gradient

    # Functional colors
    SUCCESS_COLOR = "#10B981"  # Green
    DANGER_COLOR = "#EF4444"   # Red
    WARNING_COLOR = "#F59E0B"  # Orange
    INFO_COLOR = "#3B82F6"     # Blue

    # Background colors
    BG_COLOR = "#F8FAFC"  # Light gray-blue
    BG_GRADIENT = ["#F8FAFC", "#F1F5F9"]  # Background gradient
    CARD_COLOR = "#FFFFFF"
    CARD_HOVER = "#FAFAFA"

    # Text colors
    TEXT_PRIMARY = "#1E293B"  # Dark gray-blue
    TEXT_SECONDARY = "#64748B"  # Medium gray
    TEXT_DISABLED = "#94A3B8"  # Light gray
    TEXT_INVERSE = "#FFFFFF"  # White text

    # Border colors
    BORDER_COLOR = "#E2E8F0"
    BORDER_LIGHT = "#F1F5F9"

    # Shadow configuration
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    SHADOW_XL = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"

    # Size configuration
    PAGE_PADDING = 20
    CARD_PADDING = 20
    CARD_RADIUS = 16
    ITEM_SPACING = 12
    SECTION_SPACING = 24

# Game Configuration
class GameConfig:
    # Life settings
    MAX_AGE = 80  # Maximum age
    MINUTES_PER_DAY = 24 * 60  # Blood consumed per day
    BLOOD_DECREASE_PER_MINUTE = 1  # Blood decreased per minute

    # Spirit settings
    MIN_SPIRIT = -80
    MAX_SPIRIT = 200
    DEFAULT_SPIRIT = 0

    # Currency settings
    DEFAULT_TARGET_MONEY = 5000000  # Default target: 5 million
    USD_TO_CNY_RATE = 7.25  # USD to CNY exchange rate

    # Realm levels
    REALM_LEVELS = ["Qi Refining", "Foundation", "Golden Core", "Nascent Soul", "Spirit Severing"]