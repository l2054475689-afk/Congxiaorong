# ui/main_window.py - 修正版
import flet as ft
import threading
import time
from database.db_manager import DatabaseManager
from database.models import Task
from systems.panel import PanelSystem
from systems.xinjing import XinjingSystem
from systems.jingjie import JingjieSystem
from systems.lingshi import LingshiSystem
from systems.tongyu import TongyuSystem
from systems.settings import SettingsSystem
from systems.lizhi import LizhiSystem
from ui.task_widgets import TaskWidget
from config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, ThemeConfig, GameConfig

class MainWindow:
    """主窗口类 - 修正版"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = DatabaseManager()
        self.current_page = "panel"
        self.blood_timer = None
        self.is_running = True
        
        # 初始化各个系统
        self.panel_system = PanelSystem(self.db)
        self.xinjing_system = XinjingSystem(self.db)
        self.jingjie_system = JingjieSystem(self.db)
        self.lingshi_system = LingshiSystem(self.db)
        self.tongyu_system = TongyuSystem(self.db)
        self.lizhi_system = LizhiSystem(self.db)
        self.settings_system = SettingsSystem(self.db)
    
    def setup(self):
        """设置主窗口"""
        # 创建主内容容器
        self.main_content = ft.Column(expand=True)
        
        # 创建悬浮按钮 - 优化版
        self.fab = ft.FloatingActionButton(
            icon=ft.icons.ADD_ROUNDED,
            bgcolor=ThemeConfig.PRIMARY_COLOR,
            on_click=self.show_add_dialog,
            visible=False,
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        # 创建底部导航
        self.bottom_nav = self._create_bottom_nav()
        
        # 添加到页面
        self.page.add(
            ft.Column(
                controls=[
                    ft.Container(
                        content=self.main_content,
                        expand=True,
                    ),
                ],
                expand=True,
            )
        )
        
        # 添加悬浮按钮到overlay
        self.page.overlay.append(
            ft.Container(
                content=self.fab,
                bottom=80,
                right=20,
            )
        )
        
        # 设置底部导航栏
        self.page.bottom_appbar = self.bottom_nav
        
        # 启动血量自动减少定时器
        self.start_blood_timer()
        
        # 页面关闭时停止定时器
        self.page.on_disconnect = self.stop_blood_timer
        
        # 显示每日励志语录
        LizhiSystem.show_daily_quote(self.page, self.db)

        # 显示默认页面
        self.show_panel()
    
    def start_blood_timer(self):
        """启动血量自动减少定时器 - 性能优化版"""
        def decrease_blood():
            update_counter = 0  # 更新计数器
            while self.is_running:
                time.sleep(60)  # 每60秒执行一次
                if self.is_running:
                    try:
                        # 减少1点血量
                        success = self.db.decrease_blood_by_time(1)

                        # 只在面板页面且每5分钟更新一次UI（减少刷新频率）
                        if success:
                            update_counter += 1
                            if self.current_page == "panel" and update_counter % 5 == 0:
                                # 使用page.run_task确保在主线程更新UI
                                def update_ui():
                                    self.refresh_current_page()

                                try:
                                    self.page.run_task(update_ui)
                                except:
                                    pass  # 页面可能已关闭
                    except Exception as e:
                        print(f"血量更新异常: {e}")

        self.blood_timer = threading.Thread(target=decrease_blood, daemon=True)
        self.blood_timer.start()
        print("血量定时器已启动（优化模式：每5分钟刷新UI）")
    
    def stop_blood_timer(self, e=None):
        """停止血量定时器"""
        self.is_running = False
        print("血量定时器已停止")
    
    def _create_bottom_nav(self) -> ft.BottomAppBar:
        """创建底部导航栏 - 优化版"""
        nav_items = [
            ("面板", ft.icons.HOME_ROUNDED, "panel"),
            ("心境", ft.icons.SELF_IMPROVEMENT_ROUNDED, "xinjing"),
            ("境界", ft.icons.MENU_BOOK_ROUNDED, "jingjie"),
            ("灵石", ft.icons.DIAMOND_ROUNDED, "lingshi"),
            ("统御", ft.icons.PEOPLE_ROUNDED, "tongyu"),
            ("设置", ft.icons.SETTINGS_ROUNDED, "settings"),
        ]

        nav_row = ft.Row(
            controls=[],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )

        for label, icon, page_name in nav_items:
            is_active = self.current_page == page_name
            nav_row.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    icon,
                                    color=ThemeConfig.TEXT_INVERSE if is_active else ThemeConfig.TEXT_DISABLED,
                                    size=24,
                                ),
                                bgcolor=ThemeConfig.PRIMARY_COLOR if is_active else None,
                                border_radius=12,
                                padding=8,
                            ),
                            ft.Text(
                                label,
                                size=11,
                                weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.NORMAL,
                                color=ThemeConfig.PRIMARY_COLOR if is_active else ThemeConfig.TEXT_DISABLED,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    on_click=lambda e, pn=page_name: self.navigate_to(pn),
                    ink=True,
                )
            )

        return ft.BottomAppBar(
            bgcolor=ThemeConfig.CARD_COLOR,
            content=ft.Container(
                content=nav_row,
                padding=ft.padding.symmetric(vertical=8),
            ),
            shadow_color=ft.colors.with_opacity(0.1, "#000000"),
            elevation=8,
        )
    
    def navigate_to(self, page_name: str):
        """导航到指定页面"""
        navigation_map = {
            "panel": self.show_panel,
            "xinjing": self.show_xinjing,
            "jingjie": self.show_jingjie,
            "lingshi": self.show_lingshi,
            "tongyu": self.show_tongyu,
            "settings": self.show_settings,
        }

        if page_name in navigation_map:
            navigation_map[page_name]()
    
    def show_panel(self):
        """显示个人面板"""
        self.current_page = "panel"
        # 重新创建面板系统实例以获取最新数据
        self.panel_system = PanelSystem(self.db)
        self.main_content.controls = [self.panel_system.create_panel_view()]
        self.fab.visible = False
        self._update_nav_and_page()
    
    def show_xinjing(self):
        """显示心境系统"""
        self.current_page = "xinjing"
        self.main_content.controls = [
            self.xinjing_system.create_xinjing_view(self.toggle_task, self.delete_task)
        ]
        self.fab.visible = True
        self._update_nav_and_page()
    
    def show_jingjie(self):
        """显示境界系统"""
        self.current_page = "jingjie"
        # 重新创建实例以刷新数据
        self.jingjie_system = JingjieSystem(self.db)
        self.main_content.controls = [
            self.jingjie_system.create_jingjie_view(self.refresh_current_page)
        ]
        self.fab.visible = False
        self._update_nav_and_page()
    
    def show_lingshi(self):
        """显示灵石系统"""
        self.current_page = "lingshi"
        # 重新创建实例以刷新数据
        self.lingshi_system = LingshiSystem(self.db)
        self.main_content.controls = [
            self.lingshi_system.create_lingshi_view(self.refresh_current_page)
        ]
        self.fab.visible = False
        self._update_nav_and_page()
    
    def show_tongyu(self):
        """显示统御系统"""
        self.current_page = "tongyu"
        # 重新创建统御系统实例以获取最新数据
        self.tongyu_system = TongyuSystem(self.db)
        self.main_content.controls = [self.tongyu_system.create_tongyu_view(self.refresh_current_page)]
        self.fab.visible = False
        self._update_nav_and_page()

    def show_settings(self):
        """显示设置"""
        self.current_page = "settings"
        # 重新创建设置系统实例
        self.settings_system = SettingsSystem(self.db)
        self.main_content.controls = [self.settings_system.create_settings_view(self.refresh_current_page)]
        self.fab.visible = False
        self._update_nav_and_page()
    
    def _update_nav_and_page(self):
        """更新导航栏和页面"""
        # 更新底部导航栏
        self.page.bottom_appbar = self._create_bottom_nav()
        # 更新页面内容
        self.page.update()
    
    def toggle_task(self, task: Task, completed: bool):
        """切换任务完成状态"""
        try:
            if completed:
                self.db.complete_task(task.id, task.spirit_effect, task.blood_effect)
                print(f"完成任务: {task.name} (心境{task.spirit_effect:+d}, 血量{task.blood_effect:+d})")
            else:
                self.db.uncomplete_task(task.id, task.spirit_effect, task.blood_effect)
                print(f"取消任务: {task.name}")
            
            # 刷新当前页面
            self.refresh_current_page()
        except Exception as e:
            print(f"切换任务状态错误: {e}")
            self.show_error_dialog(f"操作失败: {str(e)}")
    
    def delete_task(self, task: Task):
        """删除任务"""
        def confirm_delete(e):
            try:
                self.db.delete_task(task.id)
                print(f"删除任务成功: {task.name}")
                dialog.open = False
                self.page.update()
                self.refresh_current_page()
            except Exception as ex:
                print(f"删除任务失败: {ex}")
                self.show_error_dialog(f"删除失败: {str(ex)}")
        
        def cancel_delete(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("确认删除", color=ThemeConfig.DANGER_COLOR),
            content=ft.Text(f"确定要删除任务「{task.name}」吗？此操作不可恢复。"),
            actions=[
                ft.TextButton("取消", on_click=cancel_delete),
                ft.TextButton(
                    "删除", 
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR)
                ),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def refresh_current_page(self):
        """刷新当前页面"""
        self.navigate_to(self.current_page)
    
    def show_add_dialog(self, e):
        """显示添加对话框"""
        if self.current_page == "xinjing":
            self.show_add_task_dialog()
    
    def show_add_task_dialog(self):
        """显示添加任务对话框"""
        def on_save(name: str, category: str, spirit_effect: int, blood_effect: int):
            try:
                self.db.add_task(name, category, spirit_effect, blood_effect)
                print(f"添加任务成功: {name}")
                self.refresh_current_page()
            except Exception as ex:
                print(f"添加任务失败: {ex}")
                self.show_error_dialog(f"添加失败: {str(ex)}")
        
        dialog = TaskWidget.create_add_task_dialog(self.page, on_save)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_error_dialog(self, message: str):
        """显示错误对话框"""
        def close_dialog(e):
            error_dialog.open = False
            self.page.update()
        
        error_dialog = ft.AlertDialog(
            title=ft.Text("错误", color=ThemeConfig.DANGER_COLOR),
            content=ft.Text(message),
            actions=[
                ft.TextButton("确定", on_click=close_dialog),
            ],
        )
        
        self.page.dialog = error_dialog
        error_dialog.open = True
        self.page.update()