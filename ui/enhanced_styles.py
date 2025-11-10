import flet as ft
from config import ThemeConfig
from typing import Dict, List, Tuple, Optional
import math


class EnhancedStyles:
    """增强的样式系统 - 精美UI设计"""
    
    # 扩展颜色方案
    COLORS = {
        # 主题色系
        "primary": "#667eea",
        "primary_light": "#9bb5ff",
        "primary_dark": "#3f51b5",
        
        # 功能色系
        "success": "#4CAF50",
        "success_light": "#81C784",
        "success_dark": "#388E3C",
        
        "warning": "#FF9800",
        "warning_light": "#FFB74D",
        "warning_dark": "#F57C00",
        
        "error": "#f5576c",
        "error_light": "#ff8a80",
        "error_dark": "#d32f2f",
        
        "info": "#2196F3",
        "info_light": "#64B5F6",
        "info_dark": "#1976D2",
        
        # 灰度色系
        "grey_50": "#fafafa",
        "grey_100": "#f5f5f5",
        "grey_200": "#eeeeee",
        "grey_300": "#e0e0e0",
        "grey_400": "#bdbdbd",
        "grey_500": "#9e9e9e",
        "grey_600": "#757575",
        "grey_700": "#616161",
        "grey_800": "#424242",
        "grey_900": "#212121",
        
        # 修仙主题色
        "spirit_purple": "#9c27b0",
        "spirit_blue": "#3f51b5",
        "spirit_teal": "#009688",
        "spirit_gold": "#ff9800",
        "blood_red": "#e91e63",
        "life_gradient_start": "#f093fb",
        "life_gradient_end": "#f5576c",
        "money_gradient_start": "#f6d365",
        "money_gradient_end": "#fda085",
    }
    
    # 字体大小系统
    FONT_SIZES = {
        "xs": 10,
        "sm": 12,
        "base": 14,
        "lg": 16,
        "xl": 18,
        "2xl": 20,
        "3xl": 24,
        "4xl": 28,
        "5xl": 32,
        "6xl": 36,
    }
    
    # 间距系统
    SPACING = {
        "xs": 4,
        "sm": 8,
        "md": 12,
        "lg": 16,
        "xl": 20,
        "2xl": 24,
        "3xl": 32,
        "4xl": 40,
        "5xl": 48,
        "6xl": 64,
    }
    
    # 圆角系统
    RADIUS = {
        "none": 0,
        "sm": 4,
        "md": 8,
        "lg": 12,
        "xl": 16,
        "2xl": 20,
        "full": 999,
    }
    
    @classmethod
    def get_gradient(cls, colors: List[str], direction: str = "vertical") -> ft.LinearGradient:
        """获取渐变色
        
        Args:
            colors: 颜色列表
            direction: 渐变方向 (vertical, horizontal, diagonal)
        """
        if direction == "vertical":
            begin = ft.alignment.top_center
            end = ft.alignment.bottom_center
        elif direction == "horizontal":
            begin = ft.alignment.center_left
            end = ft.alignment.center_right
        elif direction == "diagonal":
            begin = ft.alignment.top_left
            end = ft.alignment.bottom_right
        else:
            begin = ft.alignment.top_center
            end = ft.alignment.bottom_center
        
        return ft.LinearGradient(
            begin=begin,
            end=end,
            colors=colors,
        )
    
    @classmethod
    def get_radial_gradient(cls, colors: List[str], center: Tuple[float, float] = (0.5, 0.5)) -> ft.RadialGradient:
        """获取径向渐变"""
        return ft.RadialGradient(
            colors=colors,
            center=ft.Alignment(center[0], center[1]),
            radius=0.8,
        )
    
    @classmethod
    def get_shadow(cls, elevation: int = 2, color: str = "#000000", opacity: float = 0.1) -> ft.BoxShadow:
        """获取阴影效果
        
        Args:
            elevation: 阴影层级 (1-5)
            color: 阴影颜色
            opacity: 透明度
        """
        shadow_configs = {
            1: {"blur": 3, "spread": 1, "offset": (0, 1)},
            2: {"blur": 6, "spread": 2, "offset": (0, 2)},
            3: {"blur": 10, "spread": 3, "offset": (0, 4)},
            4: {"blur": 15, "spread": 4, "offset": (0, 6)},
            5: {"blur": 20, "spread": 5, "offset": (0, 8)},
        }
        
        config = shadow_configs.get(elevation, shadow_configs[2])
        
        return ft.BoxShadow(
            spread_radius=config["spread"],
            blur_radius=config["blur"],
            color=f"{color}{int(opacity * 255):02x}",
            offset=ft.Offset(config["offset"][0], config["offset"][1]),
        )
    
    @classmethod
    def get_neumorphism_shadow(cls, depth: int = 2) -> List[ft.BoxShadow]:
        """获取新拟态阴影效果"""
        return [
            # 浅色阴影（高光）
            ft.BoxShadow(
                spread_radius=depth,
                blur_radius=depth * 3,
                color="#ffffff40",
                offset=ft.Offset(-depth, -depth),
            ),
            # 深色阴影
            ft.BoxShadow(
                spread_radius=depth,
                blur_radius=depth * 3,
                color="#00000020",
                offset=ft.Offset(depth, depth),
            ),
        ]
    
    @classmethod
    def create_glass_card(
        cls,
        content: ft.Control,
        width: Optional[float] = None,
        height: Optional[float] = None,
        padding: float = 16,
        border_radius: float = 16,
        blur: float = 20,
        opacity: float = 0.1
    ) -> ft.Container:
        """创建毛玻璃效果卡片"""
        return ft.Container(
            content=content,
            width=width,
            height=height,
            padding=padding,
            border_radius=border_radius,
            bgcolor=f"#ffffff{int(opacity * 255):02x}",
            border=ft.border.all(1, "#ffffff30"),
            shadow=cls.get_shadow(2, "#000000", 0.1),
            # Flet 目前不支持backdrop-filter，这里用半透明背景模拟
        )
    
    @classmethod
    def create_gradient_card(
        cls,
        content: ft.Control,
        gradient_colors: List[str],
        width: Optional[float] = None,
        height: Optional[float] = None,
        padding: float = 16,
        border_radius: float = 16,
        shadow_elevation: int = 2
    ) -> ft.Container:
        """创建渐变背景卡片"""
        return ft.Container(
            content=content,
            width=width,
            height=height,
            padding=padding,
            border_radius=border_radius,
            gradient=cls.get_gradient(gradient_colors),
            shadow=cls.get_shadow(shadow_elevation),
        )
    
    @classmethod
    def create_elevated_card(
        cls,
        content: ft.Control,
        width: Optional[float] = None,
        height: Optional[float] = None,
        padding: float = 16,
        border_radius: float = 12,
        elevation: int = 2,
        bgcolor: str = "#ffffff"
    ) -> ft.Container:
        """创建悬浮卡片"""
        return ft.Container(
            content=content,
            width=width,
            height=height,
            padding=padding,
            border_radius=border_radius,
            bgcolor=bgcolor,
            shadow=cls.get_shadow(elevation),
        )
    
    @classmethod
    def create_neumorphic_card(
        cls,
        content: ft.Control,
        width: Optional[float] = None,
        height: Optional[float] = None,
        padding: float = 16,
        border_radius: float = 16,
        depth: int = 2,
        bgcolor: str = "#f0f0f3"
    ) -> ft.Container:
        """创建新拟态卡片"""
        return ft.Container(
            content=content,
            width=width,
            height=height,
            padding=padding,
            border_radius=border_radius,
            bgcolor=bgcolor,
            shadow=cls.get_neumorphism_shadow(depth),
        )
    
    @classmethod
    def create_progress_ring(
        cls,
        value: float,
        size: float = 60,
        stroke_width: float = 6,
        color: str = "#667eea",
        background_color: str = "#e0e0e0",
        show_text: bool = True
    ) -> ft.Stack:
        """创建圆形进度条"""
        # 计算进度角度
        angle = (value / 100) * 360 if value <= 100 else 360
        
        # 创建进度环
        progress_ring = ft.Container(
            width=size,
            height=size,
            border_radius=size / 2,
            border=ft.border.all(stroke_width, background_color),
        )
        
        # 进度覆盖层（这里简化实现，实际可能需要自定义绘制）
        progress_overlay = ft.Container(
            width=size - stroke_width,
            height=size - stroke_width,
            border_radius=(size - stroke_width) / 2,
            bgcolor=color if value >= 100 else "transparent",
        )
        
        controls = [progress_ring, progress_overlay]
        
        if show_text:
            text = ft.Text(
                f"{int(value)}%",
                size=size * 0.2,
                weight=ft.FontWeight.BOLD,
                color=cls.COLORS["grey_700"],
                text_align=ft.TextAlign.CENTER,
            )
            controls.append(ft.Container(
                content=text,
                alignment=ft.alignment.center,
            ))
        
        return ft.Stack(
            controls=controls,
            width=size,
            height=size,
        )
    
    @classmethod
    def create_animated_button(
        cls,
        text: str,
        on_click: callable,
        width: Optional[float] = None,
        height: float = 48,
        style: str = "primary",  # primary, secondary, success, warning, error
        size: str = "md"  # sm, md, lg
    ) -> ft.Container:
        """创建动画按钮"""
        
        style_configs = {
            "primary": {
                "colors": [cls.COLORS["primary"], cls.COLORS["primary_dark"]],
                "text_color": "#ffffff",
            },
            "secondary": {
                "colors": [cls.COLORS["grey_100"], cls.COLORS["grey_200"]],
                "text_color": cls.COLORS["grey_800"],
            },
            "success": {
                "colors": [cls.COLORS["success"], cls.COLORS["success_dark"]],
                "text_color": "#ffffff",
            },
            "warning": {
                "colors": [cls.COLORS["warning"], cls.COLORS["warning_dark"]],
                "text_color": "#ffffff",
            },
            "error": {
                "colors": [cls.COLORS["error"], cls.COLORS["error_dark"]],
                "text_color": "#ffffff",
            },
        }
        
        size_configs = {
            "sm": {"height": 36, "font_size": cls.FONT_SIZES["sm"], "padding": cls.SPACING["sm"]},
            "md": {"height": 48, "font_size": cls.FONT_SIZES["base"], "padding": cls.SPACING["md"]},
            "lg": {"height": 56, "font_size": cls.FONT_SIZES["lg"], "padding": cls.SPACING["lg"]},
        }
        
        config = style_configs.get(style, style_configs["primary"])
        size_config = size_configs.get(size, size_configs["md"])
        
        button_text = ft.Text(
            text,
            size=size_config["font_size"],
            weight=ft.FontWeight.W500,
            color=config["text_color"],
            text_align=ft.TextAlign.CENTER,
        )
        
        return ft.Container(
            content=button_text,
            width=width,
            height=size_config["height"],
            padding=ft.padding.symmetric(horizontal=size_config["padding"]),
            border_radius=cls.RADIUS["md"],
            gradient=cls.get_gradient(config["colors"]),
            shadow=cls.get_shadow(2),
            alignment=ft.alignment.center,
            on_click=on_click,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
            # 添加悬停效果
            ink=True,
        )
    
    @classmethod
    def create_status_chip(
        cls,
        text: str,
        status: str = "default",  # default, success, warning, error, info
        size: str = "sm"
    ) -> ft.Container:
        """创建状态标签"""
        
        status_configs = {
            "default": {"bg_color": cls.COLORS["grey_100"], "text_color": cls.COLORS["grey_700"]},
            "success": {"bg_color": cls.COLORS["success_light"], "text_color": cls.COLORS["success_dark"]},
            "warning": {"bg_color": cls.COLORS["warning_light"], "text_color": cls.COLORS["warning_dark"]},
            "error": {"bg_color": cls.COLORS["error_light"], "text_color": cls.COLORS["error_dark"]},
            "info": {"bg_color": cls.COLORS["info_light"], "text_color": cls.COLORS["info_dark"]},
        }
        
        size_configs = {
            "xs": {"font_size": cls.FONT_SIZES["xs"], "padding": 4, "radius": cls.RADIUS["sm"]},
            "sm": {"font_size": cls.FONT_SIZES["sm"], "padding": 6, "radius": cls.RADIUS["md"]},
            "md": {"font_size": cls.FONT_SIZES["base"], "padding": 8, "radius": cls.RADIUS["lg"]},
        }
        
        config = status_configs.get(status, status_configs["default"])
        size_config = size_configs.get(size, size_configs["sm"])
        
        return ft.Container(
            content=ft.Text(
                text,
                size=size_config["font_size"],
                weight=ft.FontWeight.W500,
                color=config["text_color"],
            ),
            padding=size_config["padding"],
            border_radius=size_config["radius"],
            bgcolor=config["bg_color"],
        )
    
    @classmethod
    def create_data_card(
        cls,
        title: str,
        value: str,
        subtitle: Optional[str] = None,
        icon: Optional[str] = None,
        trend: Optional[str] = None,  # up, down, stable
        color_scheme: str = "default"
    ) -> ft.Container:
        """创建数据展示卡片"""
        
        color_schemes = {
            "default": {"primary": cls.COLORS["primary"], "bg": "#ffffff"},
            "success": {"primary": cls.COLORS["success"], "bg": "#f8fbf8"},
            "warning": {"primary": cls.COLORS["warning"], "bg": "#fffbf0"},
            "error": {"primary": cls.COLORS["error"], "bg": "#fef7f7"},
            "spirit": {"primary": cls.COLORS["spirit_purple"], "bg": "#faf5ff"},
            "money": {"primary": cls.COLORS["spirit_gold"], "bg": "#fffbf0"},
        }
        
        scheme = color_schemes.get(color_scheme, color_schemes["default"])
        
        # 构建内容
        content_controls = []
        
        # 标题行
        title_row = [ft.Text(title, size=cls.FONT_SIZES["sm"], color=cls.COLORS["grey_600"])]
        if icon:
            title_row.insert(0, ft.Icon(icon, size=16, color=scheme["primary"]))
        
        content_controls.append(ft.Row(title_row, spacing=cls.SPACING["xs"]))
        
        # 数值行
        value_row = [ft.Text(value, size=cls.FONT_SIZES["3xl"], weight=ft.FontWeight.BOLD, color=scheme["primary"])]
        
        # 趋势指示器
        if trend:
            trend_icons = {
                "up": ft.icons.TRENDING_UP,
                "down": ft.icons.TRENDING_DOWN,
                "stable": ft.icons.TRENDING_FLAT,
            }
            trend_colors = {
                "up": cls.COLORS["success"],
                "down": cls.COLORS["error"],
                "stable": cls.COLORS["grey_500"],
            }
            
            value_row.append(
                ft.Icon(
                    trend_icons.get(trend, ft.icons.TRENDING_FLAT),
                    size=20,
                    color=trend_colors.get(trend, cls.COLORS["grey_500"]),
                )
            )
        
        content_controls.append(ft.Row(value_row, spacing=cls.SPACING["sm"]))
        
        # 副标题
        if subtitle:
            content_controls.append(
                ft.Text(subtitle, size=cls.FONT_SIZES["xs"], color=cls.COLORS["grey_500"])
            )
        
        return cls.create_elevated_card(
            content=ft.Column(content_controls, spacing=cls.SPACING["xs"], tight=True),
            padding=cls.SPACING["lg"],
            bgcolor=scheme["bg"],
            elevation=1,
        )
    
    @classmethod
    def get_spirit_level_style(cls, spirit_value: int) -> Dict[str, str]:
        """根据心境值获取样式"""
        if spirit_value <= -80:
            return {"name": "心魔入体", "color": cls.COLORS["error"], "bg": "#fef2f2"}
        elif -80 < spirit_value <= -60:
            return {"name": "烦躁不堪", "color": "#dc2626", "bg": "#fef2f2"}
        elif -60 < spirit_value <= -20:
            return {"name": "心烦意乱", "color": "#ea580c", "bg": "#fff7ed"}
        elif -20 < spirit_value <= 0:
            return {"name": "略有烦躁", "color": cls.COLORS["warning"], "bg": "#fffbeb"}
        elif 0 < spirit_value <= 40:
            return {"name": "心平气和", "color": "#16a34a", "bg": "#f0fdf4"}
        elif 40 < spirit_value <= 80:
            return {"name": "清心寡欲", "color": cls.COLORS["success"], "bg": "#f0fdf4"}
        elif 80 < spirit_value <= 100:
            return {"name": "守静笃行", "color": "#0891b2", "bg": "#f0f9ff"}
        elif 100 < spirit_value <= 120:
            return {"name": "虚怀若谷", "color": cls.COLORS["info"], "bg": "#eff6ff"}
        elif 120 < spirit_value <= 140:
            return {"name": "返璞归真", "color": cls.COLORS["spirit_purple"], "bg": "#faf5ff"}
        else:
            return {"name": "逍遥自在", "color": "#7c3aed", "bg": "#f3e8ff"}
    
    @classmethod
    def create_spirit_indicator(cls, spirit_value: int) -> ft.Container:
        """创建心境指示器"""
        style = cls.get_spirit_level_style(spirit_value)
        
        # 心境进度条（-80 到 200 的范围）
        progress = max(0, min(100, (spirit_value + 80) / 280 * 100))
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("心境", size=cls.FONT_SIZES["sm"], color=cls.COLORS["grey_600"]),
                    ft.Text(style["name"], size=cls.FONT_SIZES["sm"], color=style["color"], weight=ft.FontWeight.W500),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(
                    height=8,
                    border_radius=cls.RADIUS["full"],
                    bgcolor=cls.COLORS["grey_200"],
                    content=ft.Container(
                        width=f"{progress}%",
                        height=8,
                        border_radius=cls.RADIUS["full"],
                        bgcolor=style["color"],
                    ),
                ),
                
                ft.Row([
                    ft.Text("-80", size=cls.FONT_SIZES["xs"], color=cls.COLORS["grey_400"]),
                    ft.Text(f"{spirit_value}", size=cls.FONT_SIZES["lg"], weight=ft.FontWeight.BOLD, color=style["color"]),
                    ft.Text("200", size=cls.FONT_SIZES["xs"], color=cls.COLORS["grey_400"]),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=cls.SPACING["xs"]),
            
            padding=cls.SPACING["lg"],
            border_radius=cls.RADIUS["lg"],
            bgcolor=style["bg"],
            border=ft.border.all(1, style["color"] + "20"),
        )


# 新增图表组件样式
class ChartStyles:
    """图表样式"""
    
    @classmethod
    def create_line_chart_style(cls) -> Dict:
        """创建折线图样式"""
        return {
            "border": ft.Border(
                bottom=ft.BorderSide(2, EnhancedStyles.COLORS["grey_300"]),
                left=ft.BorderSide(2, EnhancedStyles.COLORS["grey_300"]),
            ),
            "grid_color": EnhancedStyles.COLORS["grey_200"],
            "line_color": EnhancedStyles.COLORS["primary"],
            "dot_color": EnhancedStyles.COLORS["primary_dark"],
        }
    
    @classmethod
    def create_bar_chart_style(cls) -> Dict:
        """创建柱状图样式"""
        return {
            "bar_colors": [
                EnhancedStyles.COLORS["primary"],
                EnhancedStyles.COLORS["success"],
                EnhancedStyles.COLORS["warning"],
                EnhancedStyles.COLORS["error"],
                EnhancedStyles.COLORS["info"],
            ],
            "grid_color": EnhancedStyles.COLORS["grey_200"],
        }


# 主题管理器
class ThemeManager:
    """主题管理器"""
    
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": self._get_light_theme(),
            "dark": self._get_dark_theme(),
            "spirit": self._get_spirit_theme(),
        }
    
    def _get_light_theme(self) -> Dict:
        """浅色主题"""
        return {
            "name": "light",
            "background": "#ffffff",
            "surface": "#f8f9fa",
            "primary": EnhancedStyles.COLORS["primary"],
            "text_primary": EnhancedStyles.COLORS["grey_800"],
            "text_secondary": EnhancedStyles.COLORS["grey_600"],
        }
    
    def _get_dark_theme(self) -> Dict:
        """深色主题"""
        return {
            "name": "dark",
            "background": "#121212",
            "surface": "#1e1e1e",
            "primary": EnhancedStyles.COLORS["primary_light"],
            "text_primary": "#ffffff",
            "text_secondary": "#b0b0b0",
        }
    
    def _get_spirit_theme(self) -> Dict:
        """修仙主题"""
        return {
            "name": "spirit",
            "background": "#0f0f23",
            "surface": "#1a1a2e",
            "primary": EnhancedStyles.COLORS["spirit_purple"],
            "text_primary": "#e0e0e0",
            "text_secondary": "#a0a0a0",
        }
    
    def get_current_theme(self) -> Dict:
        """获取当前主题"""
        return self.themes[self.current_theme]
    
    def switch_theme(self, theme_name: str):
        """切换主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name 