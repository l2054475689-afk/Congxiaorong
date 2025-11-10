import flet as ft
from typing import List, Dict, Any, Optional, Union, Tuple
from enum import Enum
from ui.enhanced_styles import EnhancedStyles


class LayoutType(Enum):
    """布局类型枚举"""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    GRID = "grid"
    STACK = "stack"
    FLEX = "flex"


class ResponsiveBreakpoint(Enum):
    """响应式断点"""
    MOBILE = "mobile"      # < 768px
    TABLET = "tablet"      # 768px - 1024px
    DESKTOP = "desktop"    # > 1024px


class TypographyScale:
    """排版比例系统"""
    
    # 字体大小系统 - 基于 1.2 比例
    SIZES = {
        "caption": 10,      # 说明文字
        "body2": 12,        # 辅助文字
        "body1": 14,        # 正文
        "subtitle2": 16,    # 副标题
        "subtitle1": 18,    # 小标题
        "h6": 20,          # 标题6
        "h5": 24,          # 标题5
        "h4": 28,          # 标题4
        "h3": 32,          # 标题3
        "h2": 36,          # 标题2
        "h1": 40,          # 标题1
        "display": 48,      # 显示文字
    }
    
    # 字重系统
    WEIGHTS = {
        "light": ft.FontWeight.W300,
        "regular": ft.FontWeight.W400,
        "medium": ft.FontWeight.W500,
        "semibold": ft.FontWeight.W600,
        "bold": ft.FontWeight.W700,
    }
    
    # 行高比例
    LINE_HEIGHTS = {
        "tight": 1.2,
        "normal": 1.4,
        "relaxed": 1.6,
        "loose": 1.8,
    }


class SpacingSystem:
    """间距系统"""
    
    # 基础间距单位 (4px 的倍数)
    BASE_UNIT = 4
    
    # 间距规模
    SCALE = {
        "0": 0,
        "1": BASE_UNIT * 1,      # 4px
        "2": BASE_UNIT * 2,      # 8px
        "3": BASE_UNIT * 3,      # 12px
        "4": BASE_UNIT * 4,      # 16px
        "5": BASE_UNIT * 5,      # 20px
        "6": BASE_UNIT * 6,      # 24px
        "8": BASE_UNIT * 8,      # 32px
        "10": BASE_UNIT * 10,    # 40px
        "12": BASE_UNIT * 12,    # 48px
        "16": BASE_UNIT * 16,    # 64px
        "20": BASE_UNIT * 20,    # 80px
        "24": BASE_UNIT * 24,    # 96px
        "32": BASE_UNIT * 32,    # 128px
    }
    
    # 语义化间距
    SEMANTIC = {
        "xs": SCALE["1"],        # 4px
        "sm": SCALE["2"],        # 8px
        "md": SCALE["4"],        # 16px
        "lg": SCALE["6"],        # 24px
        "xl": SCALE["8"],        # 32px
        "2xl": SCALE["10"],      # 40px
        "3xl": SCALE["12"],      # 48px
    }


class LayoutBuilder:
    """布局构建器"""
    
    def __init__(self, width: Optional[float] = None, height: Optional[float] = None):
        self.width = width
        self.height = height
        self.breakpoint = self._detect_breakpoint(width or 412)
    
    def _detect_breakpoint(self, width: float) -> ResponsiveBreakpoint:
        """检测当前断点"""
        if width < 768:
            return ResponsiveBreakpoint.MOBILE
        elif width < 1024:
            return ResponsiveBreakpoint.TABLET
        else:
            return ResponsiveBreakpoint.DESKTOP
    
    def create_typography(
        self,
        text: str,
        variant: str = "body1",
        weight: str = "regular",
        color: Optional[str] = None,
        line_height: str = "normal",
        text_align: ft.TextAlign = ft.TextAlign.LEFT,
        max_lines: Optional[int] = None,
        overflow: ft.TextOverflow = ft.TextOverflow.CLIP
    ) -> ft.Text:
        """创建排版文字"""
        
        return ft.Text(
            text,
            size=TypographyScale.SIZES.get(variant, 14),
            weight=TypographyScale.WEIGHTS.get(weight, ft.FontWeight.W400),
            color=color or EnhancedStyles.COLORS["grey_800"],
            text_align=text_align,
            max_lines=max_lines,
            overflow=overflow,
            # line_height 在 Flet 中可能需要通过其他方式实现
        )
    
    def create_spacer(self, size: Union[str, int] = "md", direction: str = "vertical") -> ft.Container:
        """创建间距器"""
        
        if isinstance(size, str):
            spacing_value = SpacingSystem.SEMANTIC.get(size, SpacingSystem.SEMANTIC["md"])
        else:
            spacing_value = size
        
        if direction == "vertical":
            return ft.Container(height=spacing_value)
        else:
            return ft.Container(width=spacing_value)
    
    def create_section(
        self,
        title: Optional[str] = None,
        children: List[ft.Control] = None,
        spacing: Union[str, int] = "lg",
        padding: Union[str, int, Dict[str, int]] = "lg",
        background_color: Optional[str] = None,
        border_radius: Union[str, int] = "md",
        shadow: bool = False,
        border: Optional[ft.Border] = None
    ) -> ft.Container:
        """创建内容区域"""
        
        content_controls = []
        
        # 添加标题
        if title:
            title_widget = self.create_typography(
                title,
                variant="h6",
                weight="semibold",
                color=EnhancedStyles.COLORS["grey_800"]
            )
            content_controls.append(title_widget)
            
            # 标题后间距
            content_controls.append(self.create_spacer("md"))
        
        # 添加子组件
        if children:
            content_controls.extend(children)
        
        # 处理间距
        if isinstance(spacing, str):
            spacing_value = SpacingSystem.SEMANTIC.get(spacing, 16)
        else:
            spacing_value = spacing
        
        # 处理内边距
        if isinstance(padding, str):
            padding_value = SpacingSystem.SEMANTIC.get(padding, 16)
        elif isinstance(padding, int):
            padding_value = padding
        else:
            padding_value = ft.padding.only(
                top=padding.get("top", 16),
                right=padding.get("right", 16),
                bottom=padding.get("bottom", 16),
                left=padding.get("left", 16),
            )
        
        # 处理圆角
        if isinstance(border_radius, str):
            radius_value = EnhancedStyles.RADIUS.get(border_radius, 8)
        else:
            radius_value = border_radius
        
        return ft.Container(
            content=ft.Column(
                content_controls,
                spacing=spacing_value,
                tight=True,
            ),
            padding=padding_value,
            bgcolor=background_color,
            border_radius=radius_value,
            border=border,
            shadow=EnhancedStyles.get_shadow(2) if shadow else None,
        )
    
    def create_grid(
        self,
        items: List[ft.Control],
        columns: int = 2,
        spacing: Union[str, int] = "md",
        item_aspect_ratio: Optional[float] = None
    ) -> ft.Column:
        """创建网格布局"""
        
        if isinstance(spacing, str):
            spacing_value = SpacingSystem.SEMANTIC.get(spacing, 16)
        else:
            spacing_value = spacing
        
        rows = []
        for i in range(0, len(items), columns):
            row_items = items[i:i + columns]
            
            # 补齐行的空位
            while len(row_items) < columns:
                row_items.append(ft.Container())
            
            # 创建行
            row_controls = []
            for item in row_items:
                if item_aspect_ratio and hasattr(item, 'height') and not item.height:
                    # 根据宽高比设置高度
                    item_width = (self.width or 400) / columns - spacing_value
                    item.height = item_width / item_aspect_ratio
                
                row_controls.append(ft.Expanded(child=item))
            
            rows.append(ft.Row(row_controls, spacing=spacing_value))
        
        return ft.Column(rows, spacing=spacing_value)
    
    def create_flex_layout(
        self,
        children: List[Tuple[ft.Control, int]],  # (control, flex_value)
        direction: str = "horizontal",
        spacing: Union[str, int] = "md",
        alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START,
        cross_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.CENTER
    ) -> Union[ft.Row, ft.Column]:
        """创建弹性布局"""
        
        if isinstance(spacing, str):
            spacing_value = SpacingSystem.SEMANTIC.get(spacing, 16)
        else:
            spacing_value = spacing
        
        flex_controls = []
        for control, flex_value in children:
            if flex_value > 0:
                flex_controls.append(ft.Expanded(child=control, flex=flex_value))
            else:
                flex_controls.append(control)
        
        if direction == "horizontal":
            return ft.Row(
                flex_controls,
                spacing=spacing_value,
                alignment=alignment,
                vertical_alignment=cross_alignment,
            )
        else:
            return ft.Column(
                flex_controls,
                spacing=spacing_value,
                alignment=alignment,
                horizontal_alignment=cross_alignment,
            )
    
    def create_card_layout(
        self,
        children: List[ft.Control],
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        actions: Optional[List[ft.Control]] = None,
        elevation: int = 1,
        padding: Union[str, int] = "lg"
    ) -> ft.Container:
        """创建卡片布局"""
        
        content_controls = []
        
        # 头部区域
        if title or subtitle or actions:
            header_controls = []
            
            # 标题区域
            if title or subtitle:
                title_column = []
                
                if title:
                    title_column.append(
                        self.create_typography(title, variant="subtitle1", weight="semibold")
                    )
                
                if subtitle:
                    title_column.append(
                        self.create_typography(subtitle, variant="body2", color=EnhancedStyles.COLORS["grey_600"])
                    )
                
                header_controls.append(
                    ft.Expanded(child=ft.Column(title_column, spacing=4, tight=True))
                )
            
            # 操作区域
            if actions:
                header_controls.append(ft.Row(actions, spacing=8))
            
            content_controls.append(ft.Row(header_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
            content_controls.append(self.create_spacer("md"))
        
        # 内容区域
        content_controls.extend(children)
        
        return EnhancedStyles.create_elevated_card(
            content=ft.Column(content_controls, spacing=SpacingSystem.SEMANTIC["md"], tight=True),
            padding=SpacingSystem.SEMANTIC.get(padding if isinstance(padding, str) else "lg", 20),
            elevation=elevation,
        )
    
    def create_list_layout(
        self,
        items: List[Dict[str, Any]],
        item_builder: callable,
        spacing: Union[str, int] = "sm",
        dividers: bool = False,
        padding: Union[str, int] = "md"
    ) -> ft.Container:
        """创建列表布局"""
        
        if isinstance(spacing, str):
            spacing_value = SpacingSystem.SEMANTIC.get(spacing, 8)
        else:
            spacing_value = spacing
        
        if isinstance(padding, str):
            padding_value = SpacingSystem.SEMANTIC.get(padding, 16)
        else:
            padding_value = padding
        
        list_controls = []
        
        for i, item in enumerate(items):
            # 创建列表项
            list_item = item_builder(item, i)
            list_controls.append(list_item)
            
            # 添加分割线
            if dividers and i < len(items) - 1:
                list_controls.append(
                    ft.Container(
                        height=1,
                        bgcolor=EnhancedStyles.COLORS["grey_200"],
                        margin=ft.margin.symmetric(vertical=spacing_value // 2),
                    )
                )
        
        return ft.Container(
            content=ft.Column(list_controls, spacing=spacing_value if not dividers else 0, tight=True),
            padding=padding_value,
        )
    
    def create_responsive_layout(
        self,
        mobile_layout: ft.Control,
        tablet_layout: Optional[ft.Control] = None,
        desktop_layout: Optional[ft.Control] = None
    ) -> ft.Control:
        """创建响应式布局"""
        
        if self.breakpoint == ResponsiveBreakpoint.MOBILE:
            return mobile_layout
        elif self.breakpoint == ResponsiveBreakpoint.TABLET:
            return tablet_layout or mobile_layout
        else:
            return desktop_layout or tablet_layout or mobile_layout


class ComponentBuilder:
    """组件构建器"""
    
    def __init__(self, layout_builder: LayoutBuilder):
        self.layout = layout_builder
    
    def create_info_card(
        self,
        title: str,
        value: str,
        subtitle: Optional[str] = None,
        icon: Optional[str] = None,
        color_scheme: str = "default",
        trend: Optional[str] = None
    ) -> ft.Container:
        """创建信息卡片"""
        
        # 颜色主题
        color_schemes = {
            "default": {"primary": EnhancedStyles.COLORS["primary"], "bg": "#ffffff"},
            "success": {"primary": EnhancedStyles.COLORS["success"], "bg": "#f0fdf4"},
            "warning": {"primary": EnhancedStyles.COLORS["warning"], "bg": "#fffbeb"},
            "error": {"primary": EnhancedStyles.COLORS["error"], "bg": "#fef2f2"},
        }
        
        scheme = color_schemes.get(color_scheme, color_schemes["default"])
        
        # 构建内容
        content_controls = []
        
        # 标题行
        title_row = [
            self.layout.create_typography(title, variant="body2", color=EnhancedStyles.COLORS["grey_600"])
        ]
        if icon:
            title_row.insert(0, ft.Icon(icon, size=16, color=scheme["primary"]))
        
        content_controls.append(ft.Row(title_row, spacing=8))
        
        # 数值行
        value_controls = [
            self.layout.create_typography(value, variant="h5", weight="bold", color=scheme["primary"])
        ]
        
        # 趋势指示器
        if trend:
            trend_icons = {"up": ft.icons.TRENDING_UP, "down": ft.icons.TRENDING_DOWN, "stable": ft.icons.TRENDING_FLAT}
            trend_colors = {"up": EnhancedStyles.COLORS["success"], "down": EnhancedStyles.COLORS["error"], "stable": EnhancedStyles.COLORS["grey_500"]}
            
            value_controls.append(
                ft.Icon(trend_icons.get(trend, ft.icons.TRENDING_FLAT), size=20, color=trend_colors.get(trend, EnhancedStyles.COLORS["grey_500"]))
            )
        
        content_controls.append(ft.Row(value_controls, spacing=8))
        
        # 副标题
        if subtitle:
            content_controls.append(
                self.layout.create_typography(subtitle, variant="caption", color=EnhancedStyles.COLORS["grey_500"])
            )
        
        return EnhancedStyles.create_elevated_card(
            content=ft.Column(content_controls, spacing=SpacingSystem.SEMANTIC["xs"], tight=True),
            padding=SpacingSystem.SEMANTIC["lg"],
            bgcolor=scheme["bg"],
            elevation=1,
        )
    
    def create_action_button(
        self,
        text: str,
        icon: Optional[str] = None,
        on_click: Optional[callable] = None,
        style: str = "primary",
        size: str = "md",
        full_width: bool = False
    ) -> ft.Container:
        """创建操作按钮"""
        
        style_configs = {
            "primary": {"colors": [EnhancedStyles.COLORS["primary"], EnhancedStyles.COLORS["primary_dark"]], "text_color": "#ffffff"},
            "secondary": {"colors": [EnhancedStyles.COLORS["grey_100"], EnhancedStyles.COLORS["grey_200"]], "text_color": EnhancedStyles.COLORS["grey_800"]},
            "success": {"colors": [EnhancedStyles.COLORS["success"], EnhancedStyles.COLORS["success_dark"]], "text_color": "#ffffff"},
            "warning": {"colors": [EnhancedStyles.COLORS["warning"], EnhancedStyles.COLORS["warning_dark"]], "text_color": "#ffffff"},
            "error": {"colors": [EnhancedStyles.COLORS["error"], EnhancedStyles.COLORS["error_dark"]], "text_color": "#ffffff"},
        }
        
        size_configs = {
            "sm": {"height": 36, "font_size": TypographyScale.SIZES["body2"], "padding": SpacingSystem.SEMANTIC["sm"]},
            "md": {"height": 44, "font_size": TypographyScale.SIZES["body1"], "padding": SpacingSystem.SEMANTIC["md"]},
            "lg": {"height": 52, "font_size": TypographyScale.SIZES["subtitle2"], "padding": SpacingSystem.SEMANTIC["lg"]},
        }
        
        config = style_configs.get(style, style_configs["primary"])
        size_config = size_configs.get(size, size_configs["md"])
        
        # 按钮内容
        button_controls = []
        if icon:
            button_controls.append(ft.Icon(icon, color=config["text_color"], size=size_config["font_size"]))
        
        button_controls.append(
            self.layout.create_typography(text, variant="body1", weight="medium", color=config["text_color"])
        )
        
        content = ft.Row(
            button_controls,
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        return ft.Container(
            content=content,
            width=None if not full_width else None,  # TODO: 处理全宽
            height=size_config["height"],
            padding=ft.padding.symmetric(horizontal=size_config["padding"]),
            border_radius=EnhancedStyles.RADIUS["md"],
            gradient=EnhancedStyles.get_gradient(config["colors"]),
            shadow=EnhancedStyles.get_shadow(2),
            on_click=on_click,
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            ink=True,
        )


# 预设布局模板
class LayoutTemplates:
    """布局模板"""
    
    @staticmethod
    def create_dashboard_layout(
        header: ft.Control,
        metrics: List[ft.Control],
        charts: List[ft.Control],
        recent_activity: ft.Control,
        quick_actions: ft.Control,
        layout_builder: LayoutBuilder
    ) -> ft.Column:
        """创建仪表盘布局"""
        
        content = [
            # 头部
            header,
            layout_builder.create_spacer("lg"),
            
            # 指标网格
            layout_builder.create_grid(metrics, columns=2, spacing="md"),
            layout_builder.create_spacer("lg"),
            
            # 图表区域
            layout_builder.create_section("数据趋势", charts, spacing="lg"),
            layout_builder.create_spacer("lg"),
            
            # 最近活动和快速操作
            layout_builder.create_flex_layout([
                (recent_activity, 2),
                (quick_actions, 1),
            ], spacing="lg"),
        ]
        
        return ft.Column(content, spacing=0, expand=True)
    
    @staticmethod
    def create_list_detail_layout(
        title: str,
        items: List[ft.Control],
        actions: List[ft.Control],
        layout_builder: LayoutBuilder
    ) -> ft.Column:
        """创建列表详情布局"""
        
        content = [
            # 头部
            layout_builder.create_flex_layout([
                (layout_builder.create_typography(title, variant="h5", weight="bold"), 1),
                (ft.Row(actions, spacing=8), 0),
            ]),
            layout_builder.create_spacer("lg"),
            
            # 列表内容
            layout_builder.create_section(children=items, padding="md"),
        ]
        
        return ft.Column(content, spacing=0, expand=True)


# 使用示例
def create_sample_layout():
    """创建示例布局"""
    layout = LayoutBuilder(width=412, height=915)
    component = ComponentBuilder(layout)
    
    # 创建示例组件
    info_cards = [
        component.create_info_card("剩余生命", "28,382 天", icon=ft.icons.FAVORITE, color_scheme="error", trend="down"),
        component.create_info_card("当前灵石", "¥125,840", icon=ft.icons.MONETIZATION_ON, color_scheme="warning", trend="up"),
        component.create_info_card("心境等级", "心平气和", icon=ft.icons.SPA, color_scheme="success"),
        component.create_info_card("修炼进度", "75%", icon=ft.icons.SCHOOL, color_scheme="default", trend="up"),
    ]
    
    # 创建按钮
    buttons = [
        component.create_action_button("导出报告", icon=ft.icons.DOWNLOAD, style="primary"),
        component.create_action_button("备份数据", icon=ft.icons.BACKUP, style="secondary"),
    ]
    
    # 创建仪表盘
    dashboard = LayoutTemplates.create_dashboard_layout(
        header=layout.create_typography("凡人修仙3w天", variant="h4", weight="bold"),
        metrics=info_cards,
        charts=[ft.Container(height=200, bgcolor=EnhancedStyles.COLORS["grey_100"])],  # 占位图表
        recent_activity=layout.create_section("最近活动", [ft.Text("暂无活动")]),
        quick_actions=layout.create_section("快速操作", buttons),
        layout_builder=layout,
    )
    
    return dashboard 