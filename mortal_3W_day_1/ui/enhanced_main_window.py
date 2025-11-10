import flet as ft
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from database.db_manager import DatabaseManager
from database.models import Task
from systems.panel import PanelSystem
from systems.xinjing import XinjingSystem
from systems.jingjie import JingjieSystem
from systems.lingshi import LingshiSystem
from systems.tongyu import TongyuSystem
from systems.settings import SettingsSystem
from ui.enhanced_styles import EnhancedStyles, ThemeManager
from ui.charts import ChartComponents, DashboardLayouts
from ui.task_widgets import TaskWidget
from utils.export import ReportExporter
from utils.backup import BackupManager
from ai_providers.ai_manager import ai_manager
from systems.poetry_system import PoetrySystem
from config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, ThemeConfig, GameConfig


class EnhancedMainWindow:
    """增强版主窗口 - 精美UI设计"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = DatabaseManager()
        self.current_page = "panel"
        self.blood_timer = None
        self.is_running = True
        
        # 主题管理器
        self.theme_manager = ThemeManager()
        
        # 工具管理器
        self.report_exporter = ReportExporter(str(self.db.db_path))
        self.backup_manager = BackupManager(str(self.db.db_path))
        
        # 初始化各个系统
        self.panel_system = PanelSystem(self.db)
        self.xinjing_system = XinjingSystem(self.db)
        self.jingjie_system = JingjieSystem(self.db)
        self.lingshi_system = LingshiSystem(self.db)
        self.tongyu_system = TongyuSystem(self.db)
        self.settings_system = SettingsSystem(self.db)
        self.poetry_system = PoetrySystem(self.db)
        
        # 页面容器
        self.main_content = None
        self.fab = None
        self.bottom_nav = None
    
    def setup(self):
        """设置主窗口"""
        # 设置页面基本属性
        self._setup_page_properties()
        
        # 创建主要组件
        self._create_components()
        
        # 构建页面布局
        self._build_layout()
        
        # 启动后台服务
        self._start_background_services()
        
        # 显示默认页面
        self.show_panel()
        
        # 检查每日诗句弹窗
        self._check_daily_poetry()
    
    def _setup_page_properties(self):
        """设置页面属性"""
        theme = self.theme_manager.get_current_theme()
        
        self.page.title = APP_NAME
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = theme["background"]
        self.page.padding = 0
        self.page.spacing = 0
        
        # 设置窗口大小
        self.page.window_width = WINDOW_WIDTH
        self.page.window_height = WINDOW_HEIGHT
        self.page.window_resizable = False
        
        # 设置自定义字体和主题
        self.page.theme = ft.Theme(
            color_scheme_seed=EnhancedStyles.COLORS["primary"],
            use_material3=True,
        )
    
    def _create_components(self):
        """创建主要组件"""
        # 创建主内容容器
        self.main_content = ft.Column(
            expand=True,
            spacing=0,
            controls=[],
        )
        
        # 创建精美的悬浮按钮
        self.fab = self._create_floating_action_button()
        
        # 创建美化的底部导航
        self.bottom_nav = self._create_enhanced_bottom_nav()
    
    def _create_floating_action_button(self) -> ft.Container:
        """创建增强的悬浮按钮"""
        return ft.Container(
            content=ft.IconButton(
                icon=ft.icons.ADD,
                icon_color="#ffffff",
                bgcolor=EnhancedStyles.COLORS["primary"],
                on_click=self.show_add_dialog,
                tooltip="添加任务",
            ),
            width=56,
            height=56,
            border_radius=28,
            gradient=EnhancedStyles.get_gradient([
                EnhancedStyles.COLORS["primary"],
                EnhancedStyles.COLORS["primary_dark"]
            ]),
            shadow=EnhancedStyles.get_shadow(4, EnhancedStyles.COLORS["primary"], 0.3),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
    
    def _create_enhanced_bottom_nav(self) -> ft.Container:
        """创建增强的底部导航栏"""
        nav_items = [
            {"icon": ft.icons.DASHBOARD_ROUNDED, "label": "面板", "key": "panel"},
            {"icon": ft.icons.SPA_ROUNDED, "label": "心境", "key": "xinjing"},
            {"icon": ft.icons.SCHOOL_ROUNDED, "label": "境界", "key": "jingjie"},
            {"icon": ft.icons.MONETIZATION_ON_ROUNDED, "label": "灵石", "key": "lingshi"},
            {"icon": ft.icons.SETTINGS_ROUNDED, "label": "设置", "key": "settings"},
        ]
        
        nav_buttons = []
        for item in nav_items:
            is_active = self.current_page == item["key"]
            
            button = ft.Container(
                content=ft.Column([
                    ft.Icon(
                        item["icon"],
                        size=24,
                        color=EnhancedStyles.COLORS["primary"] if is_active else EnhancedStyles.COLORS["grey_500"],
                    ),
                    ft.Text(
                        item["label"],
                        size=10,
                        color=EnhancedStyles.COLORS["primary"] if is_active else EnhancedStyles.COLORS["grey_500"],
                        weight=ft.FontWeight.W500 if is_active else ft.FontWeight.NORMAL,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                padding=ft.padding.symmetric(vertical=8, horizontal=12),
                border_radius=12,
                bgcolor=EnhancedStyles.COLORS["primary"] + "15" if is_active else "transparent",
                on_click=lambda e, key=item["key"]: self._navigate_to_page(key),
                animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
                ink=True,
            )
            nav_buttons.append(ft.Expanded(child=button))
        
        return ft.Container(
            content=ft.Row(nav_buttons, spacing=0),
            height=72,
            padding=ft.padding.only(top=8, bottom=8, left=16, right=16),
            bgcolor="#ffffff",
            border=ft.border.only(top=ft.BorderSide(1, EnhancedStyles.COLORS["grey_200"])),
            shadow=EnhancedStyles.get_shadow(3, "#000000", 0.08),
        )
    
    def _build_layout(self):
        """构建页面布局"""
        # 主要内容区域
        main_container = ft.Container(
            content=self.main_content,
            expand=True,
            bgcolor=EnhancedStyles.COLORS["grey_50"],
        )
        
        # 整体布局
        layout = ft.Column([
            main_container,
            self.bottom_nav,
        ], spacing=0, expand=True)
        
        self.page.add(layout)
        
        # 添加悬浮按钮到overlay
        self.page.overlay.append(
            ft.Container(
                content=self.fab,
                bottom=88,  # 在底部导航栏之上
                right=20,
            )
        )
    
    def _start_background_services(self):
        """启动后台服务"""
        self.start_blood_timer()
        self.page.on_disconnect = self.stop_blood_timer
    
    def _navigate_to_page(self, page_key: str):
        """导航到指定页面"""
        self.current_page = page_key
        
        # 更新导航栏状态
        self.bottom_nav = self._create_enhanced_bottom_nav()
        self.page.controls[0].controls[1] = self.bottom_nav
        
        # 显示对应页面
        if page_key == "panel":
            self.show_panel()
        elif page_key == "xinjing":
            self.show_xinjing()
        elif page_key == "jingjie":
            self.show_jingjie()
        elif page_key == "lingshi":
            self.show_lingshi()
        elif page_key == "settings":
            self.show_settings()
        
        self.page.update()
    
    def show_panel(self):
        """显示个人面板页面 - 增强版"""
        # 获取用户数据
        user_stats = self.db.get_user_stats()
        blood_value = user_stats.get('blood_value', 0) if user_stats else 0
        spirit_value = user_stats.get('spirit_value', 0) if user_stats else 0
        
        # 获取财务数据
        finance_stats = self.db.get_finance_summary()
        total_money = finance_stats.get('total_income', 0) - finance_stats.get('total_expense', 0)
        
        # 获取今日任务
        today_tasks = self.db.get_today_tasks()
        
        # 构建页面内容
        content = []
        
        # 顶部状态卡片
        content.append(self._create_status_overview(blood_value, spirit_value, total_money))
        
        # 数据趋势图表
        content.append(self._create_trend_charts())
        
        # 今日任务区域
        content.append(self._create_today_tasks_section(today_tasks))
        
        # 快速操作区域
        content.append(self._create_quick_actions())
        
        # 更新主内容
        self.main_content.controls = [
            ft.Container(
                content=ft.Column(content, spacing=EnhancedStyles.SPACING["lg"]),
                padding=EnhancedStyles.SPACING["lg"],
                expand=True,
            )
        ]
        
        # 显示悬浮按钮
        self.fab.visible = True
        self.page.update()
    
    def _create_status_overview(self, blood_value: int, spirit_value: int, total_money: float) -> ft.Container:
        """创建状态概览卡片"""
        
        # 生命倒计时卡片
        days_left = blood_value // (24 * 60) if blood_value > 0 else 0
        life_card = EnhancedStyles.create_gradient_card(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.FAVORITE, color="#ffffff", size=24),
                    ft.Text("剩余生命", color="#ffffff", size=14, weight=ft.FontWeight.W500),
                ], spacing=8),
                ft.Text(
                    f"{days_left:,}",
                    color="#ffffff",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text("天", color="#ffffff", size=16, opacity=0.9),
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.START),
            gradient_colors=[EnhancedStyles.COLORS["life_gradient_start"], EnhancedStyles.COLORS["life_gradient_end"]],
            width=None,
            padding=20,
            shadow_elevation=3,
        )
        
        # 心境状态卡片
        spirit_style = EnhancedStyles.get_spirit_level_style(spirit_value)
        spirit_card = EnhancedStyles.create_elevated_card(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.SPA, color=spirit_style["color"], size=20),
                    ft.Text("心境状态", color=EnhancedStyles.COLORS["grey_600"], size=12),
                ], spacing=6),
                ft.Text(
                    spirit_style["name"],
                    color=spirit_style["color"],
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
                EnhancedStyles.create_spirit_indicator(spirit_value),
            ], spacing=8),
            padding=16,
            bgcolor=spirit_style["bg"],
        )
        
        # 灵石资产卡片
        money_card = EnhancedStyles.create_gradient_card(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.MONETIZATION_ON, color="#ffffff", size=20),
                    ft.Text("当前资产", color="#ffffff", size=12, opacity=0.9),
                ], spacing=6),
                ft.Text(
                    f"¥{total_money:,.0f}",
                    color="#ffffff",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    f"目标: ¥{GameConfig.DEFAULT_TARGET_MONEY:,}",
                    color="#ffffff",
                    size=10,
                    opacity=0.8,
                ),
            ], spacing=4),
            gradient_colors=[EnhancedStyles.COLORS["money_gradient_start"], EnhancedStyles.COLORS["money_gradient_end"]],
            padding=16,
        )
        
        return ft.Container(
            content=ft.Column([
                life_card,
                ft.Row([
                    ft.Expanded(child=spirit_card),
                    ft.Expanded(child=money_card),
                ], spacing=12),
            ], spacing=12),
        )
    
    def _create_trend_charts(self) -> ft.Container:
        """创建趋势图表区域"""
        # 获取历史数据
        spirit_data = self.db.get_spirit_trend_data(days=7)
        finance_data = self.db.get_finance_trend_data(days=7)
        
        charts = []
        
        # 心境趋势图
        if spirit_data:
            spirit_chart = ChartComponents.create_line_chart(
                data=spirit_data,
                x_key="date",
                y_key="spirit_value",
                title="7日心境趋势",
                height=160,
                color=EnhancedStyles.COLORS["spirit_purple"],
            )
            charts.append(spirit_chart)
        
        # 财务趋势图
        if finance_data:
            finance_chart = ChartComponents.create_bar_chart(
                data=finance_data,
                x_key="date",
                y_key="net_amount",
                title="7日收支概况",
                height=160,
                colors=[EnhancedStyles.COLORS["success"], EnhancedStyles.COLORS["error"]],
            )
            charts.append(finance_chart)
        
        return DashboardLayouts.create_chart_section(
            title="数据趋势",
            charts=charts,
        ) if charts else ft.Container()
    
    def _create_today_tasks_section(self, tasks: List[Task]) -> ft.Container:
        """创建今日任务区域"""
        
        # 任务统计
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.status == 1)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 头部统计
        header = ft.Row([
            ft.Text("今日修炼", size=18, weight=ft.FontWeight.BOLD),
            EnhancedStyles.create_status_chip(
                f"{completed_tasks}/{total_tasks} 完成",
                status="success" if completion_rate == 100 else "default",
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # 进度环
        progress_ring = ChartComponents.create_progress_chart(
            current=completed_tasks,
            target=total_tasks,
            title="完成进度",
            size=80,
            color=EnhancedStyles.COLORS["success"],
        )
        
        # 任务列表
        task_widgets = []
        for task in tasks[:6]:  # 最多显示6个任务
            task_widget = self._create_enhanced_task_widget(task)
            task_widgets.append(task_widget)
        
        if len(tasks) > 6:
            task_widgets.append(
                ft.Container(
                    content=ft.Text(
                        f"还有 {len(tasks) - 6} 个任务...",
                        color=EnhancedStyles.COLORS["grey_500"],
                        size=12,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=8,
                )
            )
        
        return EnhancedStyles.create_elevated_card(
            content=ft.Column([
                header,
                ft.Row([
                    ft.Expanded(
                        child=ft.Column(task_widgets, spacing=8) if task_widgets else 
                        ft.Container(
                            content=ft.Text("暂无任务", color=EnhancedStyles.COLORS["grey_500"]),
                            alignment=ft.alignment.center,
                            height=100,
                        ),
                        flex=3,
                    ),
                    progress_ring if total_tasks > 0 else ft.Container(),
                ], spacing=16),
            ], spacing=16),
            padding=20,
        )
    
    def _create_enhanced_task_widget(self, task: Task) -> ft.Container:
        """创建增强的任务卡片"""
        is_completed = task.status == 1
        
        # 任务效果显示
        effects = []
        if task.spirit_effect and task.spirit_effect != 0:
            effects.append(f"心境{task.spirit_effect:+d}")
        if task.blood_effect and task.blood_effect != 0:
            effects.append(f"血量{task.blood_effect:+d}")
        
        effect_text = " | ".join(effects) if effects else ""
        
        return ft.Container(
            content=ft.Row([
                # 完成状态指示器
                ft.Container(
                    content=ft.Icon(
                        ft.icons.CHECK_CIRCLE if is_completed else ft.icons.RADIO_BUTTON_UNCHECKED,
                        color=EnhancedStyles.COLORS["success"] if is_completed else EnhancedStyles.COLORS["grey_400"],
                        size=20,
                    ),
                    on_click=lambda e, t=task: self._toggle_task(t),
                ),
                
                # 任务信息
                ft.Expanded(
                    child=ft.Column([
                        ft.Text(
                            task.name,
                            size=14,
                            weight=ft.FontWeight.W500,
                            color=EnhancedStyles.COLORS["grey_500"] if is_completed else EnhancedStyles.COLORS["grey_800"],
                            strikethrough=is_completed,
                        ),
                        ft.Text(
                            effect_text,
                            size=11,
                            color=EnhancedStyles.COLORS["primary"] if not is_completed else EnhancedStyles.COLORS["grey_400"],
                        ) if effect_text else ft.Container(),
                    ], spacing=2, tight=True),
                ),
                
                # 分类标签
                EnhancedStyles.create_status_chip(
                    task.category or "其他",
                    status="default",
                    size="xs",
                ) if task.category else ft.Container(),
                
            ], spacing=12, alignment=ft.CrossAxisAlignment.CENTER),
            
            padding=ft.padding.symmetric(horizontal=4, vertical=8),
            border_radius=8,
            bgcolor=EnhancedStyles.COLORS["success"] + "10" if is_completed else "transparent",
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
    
    def _create_quick_actions(self) -> ft.Container:
        """创建快速操作区域"""
        actions = [
            {
                "title": "导出报告",
                "icon": ft.icons.DOWNLOAD,
                "color": EnhancedStyles.COLORS["info"],
                "action": self._export_daily_report,
            },
            {
                "title": "备份数据",
                "icon": ft.icons.BACKUP,
                "color": EnhancedStyles.COLORS["warning"],
                "action": self._create_backup,
            },
            {
                "title": "AI分析",
                "icon": ft.icons.PSYCHOLOGY,
                "color": EnhancedStyles.COLORS["spirit_purple"],
                "action": self._show_ai_analysis,
            },
            {
                "title": "统计报表",
                "icon": ft.icons.ANALYTICS,
                "color": EnhancedStyles.COLORS["success"],
                "action": self._show_statistics,
            },
        ]
        
        action_buttons = []
        for action in actions:
            button = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(action["icon"], color="#ffffff", size=20),
                        width=48,
                        height=48,
                        border_radius=24,
                        bgcolor=action["color"],
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(
                        action["title"],
                        size=12,
                        color=EnhancedStyles.COLORS["grey_700"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                on_click=lambda e, a=action: a["action"](),
                animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
                ink=True,
            )
            action_buttons.append(button)
        
        return EnhancedStyles.create_elevated_card(
            content=ft.Column([
                ft.Text("快速操作", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    action_buttons,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
            ], spacing=16),
            padding=20,
        )
    
    # 事件处理方法
    def _toggle_task(self, task: Task):
        """切换任务状态"""
        # 实现任务状态切换逻辑
        pass
    
    def _export_daily_report(self):
        """导出日报"""
        try:
            report_path = self.report_exporter.export_markdown_report("day")
            self._show_success_message(f"日报导出成功: {report_path}")
        except Exception as e:
            self._show_error_message(f"导出失败: {e}")
    
    def _create_backup(self):
        """创建备份"""
        try:
            backup_path = self.backup_manager.create_backup("manual", "手动备份")
            self._show_success_message(f"备份创建成功: {backup_path}")
        except Exception as e:
            self._show_error_message(f"备份失败: {e}")
    
    def _show_ai_analysis(self):
        """显示AI分析"""
        # TODO: 实现AI分析功能
        self._show_info_message("AI分析功能开发中...")
    
    def _show_statistics(self):
        """显示统计报表"""
        # TODO: 实现统计报表功能
        self._show_info_message("统计报表功能开发中...")
    
    def _show_success_message(self, message: str):
        """显示成功消息"""
        # TODO: 实现消息提示
        print(f"成功: {message}")
    
    def _show_error_message(self, message: str):
        """显示错误消息"""
        # TODO: 实现错误提示
        print(f"错误: {message}")
    
    def _show_info_message(self, message: str):
        """显示信息消息"""
        # TODO: 实现信息提示
        print(f"信息: {message}")
    
    # 其他页面显示方法（简化版）
    def show_xinjing(self):
        """显示心境页面"""
        self.main_content.controls = [
            ft.Container(
                content=ft.Text("心境页面 - 开发中", size=20),
                alignment=ft.alignment.center,
                expand=True,
            )
        ]
        self.fab.visible = True
        self.page.update()
    
    def show_jingjie(self):
        """显示境界页面"""
        self.main_content.controls = [
            ft.Container(
                content=ft.Text("境界页面 - 开发中", size=20),
                alignment=ft.alignment.center,
                expand=True,
            )
        ]
        self.fab.visible = True
        self.page.update()
    
    def show_lingshi(self):
        """显示灵石页面"""
        self.main_content.controls = [
            ft.Container(
                content=ft.Text("灵石页面 - 开发中", size=20),
                alignment=ft.alignment.center,
                expand=True,
            )
        ]
        self.fab.visible = True
        self.page.update()
    
    def show_settings(self):
        """显示设置页面"""
        # 使用设置系统创建设置界面
        settings_view = self.settings_system.create_settings_view()
        
        self.main_content.controls = [
            ft.Container(
                content=settings_view,
                expand=True,
                padding=ft.padding.all(0),
            )
        ]
        self.fab.visible = False
        self.page.update()
    
    def show_add_dialog(self, e=None):
        """显示添加任务对话框"""
        # TODO: 实现添加任务对话框
        self._show_info_message("添加任务功能开发中...")
    
    # 血量定时器相关方法
    def start_blood_timer(self):
        """启动血量自动减少定时器"""
        def decrease_blood():
            while self.is_running:
                time.sleep(60)  # 每60秒执行一次
                if self.is_running:
                    try:
                        # 减少1点血量
                        success = self.db.decrease_blood_by_time(1)
                        if success and self.current_page == "panel":
                            # 使用page.run_task确保在主线程更新UI
                            def update_ui():
                                self.refresh_current_page()
                            
                            try:
                                self.page.run_task(update_ui)
                            except:
                                pass  # 页面可能已经关闭
                    except Exception as e:
                        print(f"血量定时器错误: {e}")
        
        self.blood_timer = threading.Thread(target=decrease_blood, daemon=True)
        self.blood_timer.start()
    
    def stop_blood_timer(self, e=None):
        """停止血量定时器"""
        self.is_running = False
        if self.backup_manager:
            self.backup_manager.stop_scheduler()
    
    def refresh_current_page(self):
        """刷新当前页面"""
        if self.current_page == "panel":
            self.show_panel()
        # 其他页面的刷新逻辑...
    
    def _check_daily_poetry(self):
        """检查是否需要显示每日诗句弹窗"""
        if self.poetry_system.should_show_daily_poetry():
            # 延迟1秒显示弹窗，确保界面已完全加载
            import threading
            def delayed_show():
                import time
                time.sleep(1)
                try:
                    self.page.run_task(self._show_daily_poetry_dialog)
                except:
                    pass  # 页面可能已关闭
            
            threading.Thread(target=delayed_show, daemon=True).start()
    
    def _show_daily_poetry_dialog(self):
        """显示每日诗句弹窗"""
        try:
            # 获取今日诗句
            daily_poetry = self.poetry_system.get_daily_poetry()
            
            # 创建精美的诗句弹窗
            poetry_dialog = ft.AlertDialog(
                title=ft.Row([
                    ft.Icon(ft.icons.AUTO_AWESOME, color=EnhancedStyles.COLORS["spirit_purple"], size=24),
                    ft.Text("今日修炼箴言", size=18, weight=ft.FontWeight.BOLD, color=EnhancedStyles.COLORS["spirit_purple"]),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                
                content=ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text(
                                daily_poetry["text"],
                                size=16,
                                weight=ft.FontWeight.W500,
                                color=EnhancedStyles.COLORS["grey_800"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            padding=ft.padding.all(20),
                            border_radius=12,
                            bgcolor=EnhancedStyles.COLORS["grey_50"],
                        ),
                        ft.Row([
                            ft.Text("—", color=EnhancedStyles.COLORS["grey_500"]),
                            ft.Text(
                                daily_poetry.get("author", "未知"),
                                size=12,
                                color=EnhancedStyles.COLORS["grey_600"],
                                italic=True,
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                        
                        ft.Row([
                            ft.Container(
                                content=ft.Text(
                                    daily_poetry.get("category", "其他"),
                                    size=10,
                                    color="#ffffff",
                                ),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=8,
                                bgcolor=EnhancedStyles.COLORS["spirit_purple"],
                            ),
                            ft.Container(
                                content=ft.Text(
                                    daily_poetry.get("source", "未知"),
                                    size=10,
                                    color=EnhancedStyles.COLORS["grey_600"],
                                ),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=8,
                                bgcolor=EnhancedStyles.COLORS["grey_100"],
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                    ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=300,
                ),
                
                actions=[
                    ft.Row([
                        ft.TextButton(
                            "管理诗句库",
                            on_click=lambda e: self._show_poetry_management_dialog(),
                            style=ft.ButtonStyle(color=EnhancedStyles.COLORS["primary"]),
                        ),
                        ft.ElevatedButton(
                            "开始修炼",
                            on_click=lambda e: self._close_daily_poetry_dialog(daily_poetry),
                            style=ft.ButtonStyle(
                                bgcolor=EnhancedStyles.COLORS["primary"],
                                color="#ffffff",
                            ),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ],
                
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                shape=ft.RoundedRectangleBorder(radius=16),
            )
            
            self.page.dialog = poetry_dialog
            poetry_dialog.open = True
            self.page.update()
            
        except Exception as e:
            print(f"显示每日诗句弹窗失败: {e}")
    
    def _close_daily_poetry_dialog(self, poetry):
        """关闭每日诗句弹窗"""
        # 标记今日诗句已显示
        self.poetry_system.mark_daily_poetry_shown(poetry)
        
        # 关闭弹窗
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def _show_poetry_management_dialog(self):
        """显示诗句管理对话框"""
        # 关闭当前弹窗
        if self.page.dialog:
            self.page.dialog.open = False
        
        # 创建诗句管理界面
        poetry_stats = self.poetry_system.get_poetry_statistics()
        categories = self.poetry_system.get_categories()
        
        # 搜索框
        search_field = ft.TextField(
            label="搜索诗句",
            hint_text="输入关键词搜索...",
            prefix_icon=ft.icons.SEARCH,
            on_change=lambda e: self._filter_poetry_list(e.control.value),
            width=300,
        )
        
        # 分类筛选
        category_dropdown = ft.Dropdown(
            label="分类筛选",
            hint_text="选择分类",
            options=[ft.dropdown.Option("全部")] + [ft.dropdown.Option(cat) for cat in categories],
            on_change=lambda e: self._filter_poetry_by_category(e.control.value),
            width=150,
        )
        
        # 诗句列表
        self.poetry_list_view = ft.ListView(
            controls=self._create_poetry_list_items(),
            height=300,
            spacing=8,
        )
        
        # 添加诗句表单
        self.new_poetry_text = ft.TextField(
            label="诗句内容",
            hint_text="输入诗句或名言...",
            multiline=True,
            max_lines=3,
            width=300,
        )
        
        self.new_poetry_author = ft.TextField(
            label="作者",
            hint_text="作者姓名（可选）",
            width=150,
        )
        
        self.new_poetry_category = ft.Dropdown(
            label="分类",
            hint_text="选择分类",
            options=[ft.dropdown.Option(cat) for cat in categories] + [ft.dropdown.Option("自定义")],
            width=150,
        )
        
        poetry_management_dialog = ft.AlertDialog(
            title=ft.Text("诗句库管理", size=18, weight=ft.FontWeight.BOLD),
            
            content=ft.Container(
                content=ft.Column([
                    # 统计信息
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"总诗句数: {poetry_stats['total_poetry']}", size=12),
                            ft.Text(f"自定义: {poetry_stats['custom_poetry']} | 内置: {poetry_stats['builtin_poetry']}", size=12),
                        ]),
                        padding=ft.padding.all(12),
                        border_radius=8,
                        bgcolor=EnhancedStyles.COLORS["grey_50"],
                    ),
                    
                    # 搜索和筛选
                    ft.Row([search_field, category_dropdown], spacing=12),
                    
                    # 诗句列表
                    ft.Text("诗句列表", weight=ft.FontWeight.W500),
                    self.poetry_list_view,
                    
                    # 添加新诗句
                    ft.Text("添加新诗句", weight=ft.FontWeight.W500),
                    self.new_poetry_text,
                    ft.Row([self.new_poetry_author, self.new_poetry_category], spacing=12),
                    
                ], spacing=12, scroll=ft.ScrollMode.AUTO),
                width=500,
                height=600,
            ),
            
            actions=[
                ft.Row([
                    ft.TextButton("导入诗句", on_click=lambda e: self._import_poetry()),
                    ft.TextButton("导出诗句", on_click=lambda e: self._export_poetry()),
                    ft.ElevatedButton(
                        "添加诗句",
                        on_click=lambda e: self._add_custom_poetry(),
                        style=ft.ButtonStyle(bgcolor=EnhancedStyles.COLORS["success"], color="#ffffff"),
                    ),
                    ft.TextButton("关闭", on_click=lambda e: self._close_poetry_dialog()),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ],
            
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        
        self.page.dialog = poetry_management_dialog
        poetry_management_dialog.open = True
        self.page.update()
    
    def _create_poetry_list_items(self, poetry_list=None):
        """创建诗句列表项"""
        if poetry_list is None:
            poetry_list = self.poetry_system.poetry_library
        
        items = []
        for poetry in poetry_list[:50]:  # 最多显示50条
            is_custom = poetry.get('source') == '自定义'
            
            item = ft.Container(
                content=ft.Row([
                    ft.Expanded(
                        child=ft.Column([
                            ft.Text(
                                poetry['text'],
                                size=14,
                                weight=ft.FontWeight.W500,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Row([
                                ft.Text(f"—{poetry.get('author', '未知')}", size=10, color=EnhancedStyles.COLORS["grey_600"]),
                                ft.Container(
                                    content=ft.Text(
                                        poetry.get('category', '其他'),
                                        size=8,
                                        color="#ffffff",
                                    ),
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=4,
                                    bgcolor=EnhancedStyles.COLORS["primary"] if is_custom else EnhancedStyles.COLORS["grey_400"],
                                ),
                            ], spacing=8),
                        ], spacing=4, tight=True),
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        icon_color=EnhancedStyles.COLORS["error"],
                        on_click=lambda e, text=poetry['text']: self._remove_poetry(text),
                        tooltip="删除诗句",
                        disabled=not is_custom,
                    ) if is_custom else ft.Container(width=40),
                ], alignment=ft.CrossAxisAlignment.START),
                
                padding=ft.padding.all(12),
                border_radius=8,
                bgcolor="#ffffff" if is_custom else EnhancedStyles.COLORS["grey_50"],
                border=ft.border.all(1, EnhancedStyles.COLORS["grey_200"]),
            )
            items.append(item)
        
        return items
    
    def _filter_poetry_list(self, keyword: str):
        """筛选诗句列表"""
        filtered_poetry = self.poetry_system.search_poetry(keyword)
        self.poetry_list_view.controls = self._create_poetry_list_items(filtered_poetry)
        self.page.update()
    
    def _filter_poetry_by_category(self, category: str):
        """按分类筛选诗句"""
        if category == "全部":
            filtered_poetry = self.poetry_system.poetry_library
        else:
            filtered_poetry = self.poetry_system.get_poetry_by_category(category)
        
        self.poetry_list_view.controls = self._create_poetry_list_items(filtered_poetry)
        self.page.update()
    
    def _add_custom_poetry(self):
        """添加自定义诗句"""
        text = self.new_poetry_text.value.strip()
        author = self.new_poetry_author.value.strip()
        category = self.new_poetry_category.value or "自定义"
        
        if not text:
            self._show_message("请输入诗句内容", "warning")
            return
        
        success = self.poetry_system.add_custom_poetry(text, author, category)
        
        if success:
            self._show_message("诗句添加成功！", "success")
            # 清空表单
            self.new_poetry_text.value = ""
            self.new_poetry_author.value = ""
            self.new_poetry_category.value = None
            # 刷新列表
            self.poetry_list_view.controls = self._create_poetry_list_items()
            self.page.update()
        else:
            self._show_message("诗句已存在或添加失败", "error")
    
    def _remove_poetry(self, text: str):
        """移除诗句"""
        success = self.poetry_system.remove_custom_poetry(text)
        
        if success:
            self._show_message("诗句删除成功", "success")
            # 刷新列表
            self.poetry_list_view.controls = self._create_poetry_list_items()
            self.page.update()
        else:
            self._show_message("删除失败", "error")
    
    def _import_poetry(self):
        """导入诗句库"""
        # TODO: 实现文件选择和导入功能
        self._show_message("导入功能开发中...", "info")
    
    def _export_poetry(self):
        """导出诗句库"""
        try:
            export_path = self.poetry_system.export_poetry_library()
            if export_path:
                self._show_message(f"诗句库已导出: {export_path}", "success")
            else:
                self._show_message("导出失败", "error")
        except Exception as e:
            self._show_message(f"导出失败: {e}", "error")
    
    def _close_poetry_dialog(self):
        """关闭诗句管理对话框"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def _show_message(self, message: str, msg_type: str = "info"):
        """显示消息提示"""
        colors = {
            "success": EnhancedStyles.COLORS["success"],
            "error": EnhancedStyles.COLORS["error"],
            "warning": EnhancedStyles.COLORS["warning"],
            "info": EnhancedStyles.COLORS["info"],
        }
        
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message, color="#ffffff"),
                bgcolor=colors.get(msg_type, colors["info"]),
                action="确定",
                action_color="#ffffff",
            )
        ) 