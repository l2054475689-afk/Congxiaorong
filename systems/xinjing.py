import flet as ft
from typing import Callable
from database.db_manager import DatabaseManager
from ui.styles import Styles
from ui.task_widgets import TaskWidget
from config import ThemeConfig, GameConfig

class XinjingSystem():
    """心境系统"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_xinjing_view(self, on_task_toggle: Callable, on_task_delete: Callable = None) -> ft.Column:
        """创建心境视图 - 支持删除功能"""
        user_data = self.db.get_user_data()
        positive_tasks = self.db.get_tasks("positive")
        negative_tasks = self.db.get_tasks("negative")
        
        spirit_level, spirit_color = Styles.get_spirit_level_info(user_data.current_spirit)
        
        return ft.Column(
            controls=[
                # 标题
                ft.Container(
                    content=ft.Text("心境系统", size=20, weight=ft.FontWeight.BOLD),
                    padding=20,
                ),
                
                # 心境值显示
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(f"当前心境值: {user_data.current_spirit}", size=18),
                            ft.Text(spirit_level, size=16, color=spirit_color),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                    alignment=ft.alignment.center,
                ),
                
                # 心境状态条
                ft.Container(
                    content=self._create_spirit_bar(user_data.current_spirit),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                
                # 正面修炼
                ft.Container(
                    content=ft.Text("【正面修炼】", size=16, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.only(left=20, top=20, bottom=10),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            TaskWidget.create_task_item(task, on_task_toggle, on_task_delete)
                            for task in positive_tasks
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
                
                # 心魔记录
                ft.Container(
                    content=ft.Text("【心魔记录】", size=16, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.only(left=20, top=20, bottom=10),
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            TaskWidget.create_task_item(task, on_task_toggle, on_task_delete)
                            for task in negative_tasks
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _create_spirit_bar(self, value: int) -> ft.Container:
        """创建心境状态条"""
        min_val = -80
        max_val = 200
        percentage = (value - min_val) / (max_val - min_val)
        percentage = max(0, min(1, percentage))
        
        return ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Container(
                        height=8,
                        border_radius=4,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.center_left,
                            end=ft.alignment.center_right,
                            colors=["#ff0000", "#ffa500", "#90ee90", "#4169e1", "#9370db"],
                        ),
                    ),
                    ft.Container(
                        width=20,
                        height=20,
                        border_radius=10,
                        bgcolor="white",
                        border=ft.border.all(3, "#667eea"),
                        left=percentage * 280,
                        top=-6,
                    ),
                ],
            ),
            width=300,
            height=20,
        )