import flet as ft
from typing import Callable
from database.models import Task
from config import ThemeConfig

class TaskWidget:
    """任务组件"""
    
    @staticmethod
    def create_task_item(task: Task, on_toggle: Callable, on_delete: Callable = None, show_details: bool = True):
        """创建任务项组件 - 添加删除功能"""
        # 效果文字
        effects = []
        if task.spirit_effect != 0:
            sign = "+" if task.spirit_effect > 0 else ""
            effects.append(f"心境{sign}{task.spirit_effect}")
        if task.blood_effect != 0:
            sign = "+" if task.blood_effect > 0 else ""
            effects.append(f"血量{sign}{task.blood_effect}")
        effect_text = " ".join(effects)
        
        # 颜色设置
        checkbox_color = ThemeConfig.SUCCESS_COLOR if task.category == "positive" else ThemeConfig.DANGER_COLOR
        
        if show_details:
            task_row = ft.Row(
                controls=[
                    ft.Checkbox(
                        value=task.completed_today,
                        fill_color=checkbox_color,
                        on_change=lambda e, t=task: on_toggle(t, e.control.value),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(task.name, size=14, weight="w500"),
                            ft.Text(f"({effect_text})", size=12, color=ThemeConfig.TEXT_SECONDARY),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
            )
            
            # 添加删除按钮
            if on_delete:
                task_row.controls.append(
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        icon_color=ThemeConfig.DANGER_COLOR,
                        icon_size=18,
                        on_click=lambda e, t=task: on_delete(t),
                    )
                )
            
            return ft.Container(
                content=task_row,
                bgcolor=ThemeConfig.CARD_COLOR,
                padding=10,
                border_radius=8,
            )
        else:
            # 简化版任务项（用于面板）
            return ft.Row(
                controls=[
                    ft.Text("✓ " if task.completed_today else "○ ", color=checkbox_color),
                    ft.Text(task.name, size=14),
                    ft.Text(f"({effect_text})", size=12, color=ThemeConfig.TEXT_DISABLED),
                ],
            )



    @staticmethod
    def create_add_task_dialog(page: ft.Page, on_save: Callable):
        """创建添加任务对话框"""
        name_field = ft.TextField(label="任务名称", width=300)
        category_dropdown = ft.Dropdown(
            label="任务类型",
            width=300,
            options=[
                ft.dropdown.Option("positive", "正面修炼"),
                ft.dropdown.Option("negative", "心魔记录"),
            ],
            value="positive",
        )
        spirit_field = ft.TextField(
            label="心境影响", 
            width=140,
            value="0",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        blood_field = ft.TextField(
            label="血量影响", 
            width=140,
            value="0",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_task(e):
            if name_field.value:
                on_save(
                    name=name_field.value,
                    category=category_dropdown.value,
                    spirit_effect=int(spirit_field.value or 0),
                    blood_effect=int(blood_field.value or 0),
                )
                close_dialog(e)
        
        dialog = ft.AlertDialog(
            title=ft.Text("添加新任务"),
            content=ft.Column(
                controls=[
                    name_field,
                    category_dropdown,
                    ft.Row([spirit_field, blood_field]),
                ],
                height=200,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_task),
            ],
        )
        
        return dialog