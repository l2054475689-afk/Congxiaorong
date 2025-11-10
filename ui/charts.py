import flet as ft
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
from ui.enhanced_styles import EnhancedStyles


class ChartComponents:
    """图表组件库"""
    
    @classmethod
    def create_line_chart(
        cls,
        data: List[Dict[str, Any]],
        x_key: str = "date",
        y_key: str = "value",
        title: str = "",
        height: float = 200,
        width: Optional[float] = None,
        color: str = "#667eea",
        show_grid: bool = True,
        show_dots: bool = True
    ) -> ft.Container:
        """创建折线图"""
        
        if not data:
            return cls._create_empty_chart("暂无数据", height, width)
        
        # 处理数据
        max_value = max(item[y_key] for item in data)
        min_value = min(item[y_key] for item in data)
        value_range = max_value - min_value if max_value != min_value else 1
        
        # 创建数据点
        data_points = []
        for i, item in enumerate(data):
            x_pos = (i / (len(data) - 1) if len(data) > 1 else 0.5) * 100
            y_pos = 100 - ((item[y_key] - min_value) / value_range * 80 + 10)
            data_points.append(ft.LineChartDataPoint(x_pos, y_pos))
        
        # 创建折线图
        line_chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=data_points,
                    stroke_width=3,
                    color=color,
                    curved=True,
                    stroke_cap_round=True,
                    prevent_curve_over_shooting=True,
                )
            ],
            border=ft.Border(
                bottom=ft.BorderSide(1, EnhancedStyles.COLORS["grey_300"]),
                left=ft.BorderSide(1, EnhancedStyles.COLORS["grey_300"]),
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=20,
                color=EnhancedStyles.COLORS["grey_200"],
                width=0.5,
            ) if show_grid else None,
            vertical_grid_lines=ft.ChartGridLines(
                interval=25,
                color=EnhancedStyles.COLORS["grey_200"],
                width=0.5,
            ) if show_grid else None,
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=min_value + (max_value - min_value) * (1 - i / 4),
                        label=ft.Text(f"{min_value + (max_value - min_value) * (1 - i / 4):.0f}")
                    ) for i in range(5)
                ]
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i * 25,
                        label=ft.Text(data[min(i * len(data) // 4, len(data) - 1)][x_key][:5])
                    ) for i in range(5)
                ] if len(data) >= 4 else []
            ),
            tooltip_bgcolor="#ffffff",
            min_x=0,
            max_x=100,
            min_y=0,
            max_y=100,
        )
        
        # 创建容器
        chart_container = ft.Column([
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD) if title else ft.Container(),
            ft.Container(
                content=line_chart,
                height=height,
                width=width,
                padding=ft.padding.all(10),
                border_radius=12,
                bgcolor="#ffffff",
                shadow=EnhancedStyles.get_shadow(1),
            )
        ], spacing=8 if title else 0)
        
        return chart_container
    
    @classmethod
    def create_bar_chart(
        cls,
        data: List[Dict[str, Any]],
        x_key: str = "category",
        y_key: str = "value",
        title: str = "",
        height: float = 200,
        width: Optional[float] = None,
        colors: Optional[List[str]] = None
    ) -> ft.Container:
        """创建柱状图"""
        
        if not data:
            return cls._create_empty_chart("暂无数据", height, width)
        
        # 默认颜色
        if colors is None:
            colors = [
                EnhancedStyles.COLORS["primary"],
                EnhancedStyles.COLORS["success"],
                EnhancedStyles.COLORS["warning"],
                EnhancedStyles.COLORS["error"],
                EnhancedStyles.COLORS["info"],
            ]
        
        # 处理数据
        max_value = max(item[y_key] for item in data)
        
        # 创建柱状图组
        bar_groups = []
        for i, item in enumerate(data):
            color = colors[i % len(colors)]
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=item[y_key],
                            width=20,
                            color=color,
                            tooltip=f"{item[x_key]}: {item[y_key]}",
                            border_radius=4,
                        )
                    ],
                )
            )
        
        # 创建柱状图
        bar_chart = ft.BarChart(
            bar_groups=bar_groups,
            border=ft.Border(
                bottom=ft.BorderSide(1, EnhancedStyles.COLORS["grey_300"]),
                left=ft.BorderSide(1, EnhancedStyles.COLORS["grey_300"]),
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                color=EnhancedStyles.COLORS["grey_200"],
                width=0.5,
            ),
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=max_value * i / 4,
                        label=ft.Text(f"{max_value * i / 4:.0f}")
                    ) for i in range(5)
                ]
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Text(data[i][x_key][:8])
                    ) for i in range(len(data))
                ]
            ),
            tooltip_bgcolor="#ffffff",
            max_y=max_value * 1.1,
        )
        
        # 创建容器
        chart_container = ft.Column([
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD) if title else ft.Container(),
            ft.Container(
                content=bar_chart,
                height=height,
                width=width,
                padding=ft.padding.all(10),
                border_radius=12,
                bgcolor="#ffffff",
                shadow=EnhancedStyles.get_shadow(1),
            )
        ], spacing=8 if title else 0)
        
        return chart_container
    
    @classmethod
    def create_pie_chart(
        cls,
        data: List[Dict[str, Any]],
        label_key: str = "label",
        value_key: str = "value",
        title: str = "",
        size: float = 200,
        colors: Optional[List[str]] = None,
        show_legend: bool = True
    ) -> ft.Container:
        """创建饼图"""
        
        if not data:
            return cls._create_empty_chart("暂无数据", size, size)
        
        # 默认颜色
        if colors is None:
            colors = [
                EnhancedStyles.COLORS["primary"],
                EnhancedStyles.COLORS["success"],
                EnhancedStyles.COLORS["warning"],
                EnhancedStyles.COLORS["error"],
                EnhancedStyles.COLORS["info"],
                EnhancedStyles.COLORS["spirit_purple"],
                EnhancedStyles.COLORS["spirit_gold"],
            ]
        
        # 计算总值和百分比
        total_value = sum(item[value_key] for item in data)
        
        # 创建饼图段
        sections = []
        for i, item in enumerate(data):
            percentage = (item[value_key] / total_value) * 100
            color = colors[i % len(colors)]
            
            sections.append(
                ft.PieChartSection(
                    value=percentage,
                    title=f"{percentage:.1f}%",
                    title_style=ft.TextStyle(
                        size=12,
                        color="#ffffff",
                        weight=ft.FontWeight.BOLD
                    ),
                    color=color,
                    radius=80,
                )
            )
        
        # 创建饼图
        pie_chart = ft.PieChart(
            sections=sections,
            sections_space=2,
            center_space_radius=30,
        )
        
        # 创建图例
        legend_items = []
        if show_legend:
            for i, item in enumerate(data):
                color = colors[i % len(colors)]
                legend_items.append(
                    ft.Row([
                        ft.Container(
                            width=12,
                            height=12,
                            bgcolor=color,
                            border_radius=2,
                        ),
                        ft.Text(
                            f"{item[label_key]} ({item[value_key]})",
                            size=12,
                            color=EnhancedStyles.COLORS["grey_700"],
                        )
                    ], spacing=8)
                )
        
        # 组合内容
        content = []
        if title:
            content.append(ft.Text(title, size=16, weight=ft.FontWeight.BOLD))
        
        chart_row = [
            ft.Container(
                content=pie_chart,
                width=size,
                height=size,
            )
        ]
        
        if legend_items:
            chart_row.append(
                ft.Container(
                    content=ft.Column(legend_items, spacing=4),
                    padding=ft.padding.only(left=20),
                )
            )
        
        content.append(ft.Row(chart_row, alignment=ft.MainAxisAlignment.CENTER))
        
        return ft.Container(
            content=ft.Column(content, spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(16),
            border_radius=12,
            bgcolor="#ffffff",
            shadow=EnhancedStyles.get_shadow(1),
        )
    
    @classmethod
    def create_progress_chart(
        cls,
        current: float,
        target: float,
        title: str = "",
        subtitle: str = "",
        size: float = 120,
        stroke_width: float = 8,
        color: str = "#667eea",
        background_color: str = "#e0e0e0"
    ) -> ft.Container:
        """创建进度环形图"""
        
        percentage = min(100, (current / target * 100)) if target > 0 else 0
        
        # 创建进度环（使用Stack模拟）
        progress_ring = ft.Stack([
            # 背景环
            ft.Container(
                width=size,
                height=size,
                border_radius=size / 2,
                border=ft.border.all(stroke_width, background_color),
            ),
            # 进度环（简化实现）
            ft.Container(
                width=size - stroke_width,
                height=size - stroke_width,
                border_radius=(size - stroke_width) / 2,
                margin=ft.margin.all(stroke_width / 2),
                # 这里简化进度显示，实际可能需要自定义画布
            ),
            # 中心文本
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"{percentage:.0f}%",
                        size=size * 0.15,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"{current:.0f}/{target:.0f}",
                        size=size * 0.08,
                        color=EnhancedStyles.COLORS["grey_600"],
                        text_align=ft.TextAlign.CENTER,
                    ) if target > 0 else ft.Container(),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                width=size,
                height=size,
            ),
        ])
        
        # 构建完整组件
        content = []
        if title:
            content.append(
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
            )
        
        content.append(progress_ring)
        
        if subtitle:
            content.append(
                ft.Text(subtitle, size=12, color=EnhancedStyles.COLORS["grey_600"], text_align=ft.TextAlign.CENTER)
            )
        
        return ft.Container(
            content=ft.Column(
                content,
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.all(16),
            border_radius=12,
            bgcolor="#ffffff",
            shadow=EnhancedStyles.get_shadow(1),
        )
    
    @classmethod
    def create_trend_card(
        cls,
        title: str,
        current_value: float,
        previous_value: float,
        format_str: str = "{:.0f}",
        prefix: str = "",
        suffix: str = "",
        width: Optional[float] = None
    ) -> ft.Container:
        """创建趋势卡片"""
        
        # 计算变化
        if previous_value != 0:
            change = current_value - previous_value
            change_percent = (change / abs(previous_value)) * 100
        else:
            change = current_value
            change_percent = 100 if current_value > 0 else 0
        
        # 确定趋势
        if change > 0:
            trend_icon = ft.icons.TRENDING_UP
            trend_color = EnhancedStyles.COLORS["success"]
            trend_text = f"+{change_percent:.1f}%"
        elif change < 0:
            trend_icon = ft.icons.TRENDING_DOWN
            trend_color = EnhancedStyles.COLORS["error"]
            trend_text = f"{change_percent:.1f}%"
        else:
            trend_icon = ft.icons.TRENDING_FLAT
            trend_color = EnhancedStyles.COLORS["grey_500"]
            trend_text = "0%"
        
        # 格式化当前值
        formatted_value = f"{prefix}{format_str.format(current_value)}{suffix}"
        
        return EnhancedStyles.create_elevated_card(
            content=ft.Column([
                ft.Text(title, size=14, color=EnhancedStyles.COLORS["grey_600"]),
                ft.Row([
                    ft.Text(
                        formatted_value,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=EnhancedStyles.COLORS["grey_800"],
                    ),
                    ft.Row([
                        ft.Icon(trend_icon, size=16, color=trend_color),
                        ft.Text(trend_text, size=12, color=trend_color, weight=ft.FontWeight.W500),
                    ], spacing=4),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ], spacing=8),
            width=width,
            padding=16,
        )
    
    @classmethod
    def create_mini_sparkline(
        cls,
        data: List[float],
        width: float = 100,
        height: float = 30,
        color: str = "#667eea",
        show_last_value: bool = True
    ) -> ft.Container:
        """创建迷你趋势线"""
        
        if not data or len(data) < 2:
            return ft.Container(width=width, height=height)
        
        # 归一化数据
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        # 创建路径点
        points = []
        for i, value in enumerate(data):
            x = (i / (len(data) - 1)) * width
            y = height - ((value - min_val) / range_val) * height
            points.append((x, y))
        
        # 创建简化的折线图（使用容器模拟）
        # 在实际实现中，可能需要使用Canvas或自定义Paint
        
        content = [
            ft.Container(
                width=width,
                height=height,
                bgcolor=color + "20",
                border_radius=4,
                # 这里可以添加实际的路径绘制
            )
        ]
        
        if show_last_value and data:
            content.append(
                ft.Text(
                    f"{data[-1]:.0f}",
                    size=10,
                    color=color,
                    weight=ft.FontWeight.BOLD,
                )
            )
        
        return ft.Column(content, spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    @classmethod
    def _create_empty_chart(cls, message: str, height: float, width: Optional[float]) -> ft.Container:
        """创建空图表占位符"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.SHOW_CHART, size=48, color=EnhancedStyles.COLORS["grey_400"]),
                ft.Text(message, size=14, color=EnhancedStyles.COLORS["grey_500"]),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            width=width,
            height=height,
            border_radius=12,
            bgcolor=EnhancedStyles.COLORS["grey_50"],
            border=ft.border.all(1, EnhancedStyles.COLORS["grey_200"]),
        )


class DashboardLayouts:
    """仪表盘布局组件"""
    
    @classmethod
    def create_metrics_grid(
        cls,
        metrics: List[Dict[str, Any]],
        columns: int = 2
    ) -> ft.Container:
        """创建指标网格"""
        
        rows = []
        for i in range(0, len(metrics), columns):
            row_metrics = metrics[i:i + columns]
            row_widgets = []
            
            for metric in row_metrics:
                card = ChartComponents.create_trend_card(
                    title=metric.get("title", ""),
                    current_value=metric.get("current", 0),
                    previous_value=metric.get("previous", 0),
                    format_str=metric.get("format", "{:.0f}"),
                    prefix=metric.get("prefix", ""),
                    suffix=metric.get("suffix", ""),
                )
                row_widgets.append(ft.Expanded(child=card))
            
            # 填充空白位置
            while len(row_widgets) < columns:
                row_widgets.append(ft.Expanded(child=ft.Container()))
            
            rows.append(ft.Row(row_widgets, spacing=12))
        
        return ft.Column(rows, spacing=12)
    
    @classmethod
    def create_chart_section(
        cls,
        title: str,
        charts: List[ft.Control],
        show_border: bool = True
    ) -> ft.Container:
        """创建图表区域"""
        
        content = [
            ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=EnhancedStyles.COLORS["grey_800"]),
            ft.Column(charts, spacing=16),
        ]
        
        container_kwargs = {
            "content": ft.Column(content, spacing=16),
            "padding": ft.padding.all(20),
            "border_radius": 12,
        }
        
        if show_border:
            container_kwargs.update({
                "bgcolor": "#ffffff",
                "shadow": EnhancedStyles.get_shadow(1),
            })
        
        return ft.Container(**container_kwargs) 