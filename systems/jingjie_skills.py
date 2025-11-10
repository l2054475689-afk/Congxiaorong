# systems/jingjie_skills.py - 技能管理
import flet as ft
from database.db_manager import DatabaseManager
from config import ThemeConfig

class JingjieSkillManager:
    """境界技能管理器"""
    
    def __init__(self, db: DatabaseManager, jingjie_system):
        self.db = db
        self.jingjie = jingjie_system
    
    def show_add_skill_dialog(self, page: ft.Page, category: str):
        """显示添加技能对话框"""
        name_field = ft.TextField(label="技能名称", width=300)
        nodes_field = ft.TextField(
            label="技能节点（用逗号分隔）", 
            width=300,
            multiline=True,
            hint_text="例如：基础，进阶，高级，精通"
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_skill(e):
            if name_field.value and nodes_field.value:
                nodes = [n.strip() for n in nodes_field.value.split(",")]
                # 添加到技能树
                self.jingjie.skill_trees[category][name_field.value] = {
                    "nodes": nodes,
                    "completed": [],
                    "realm": "练气期"
                }
                # 保存到数据库
                self.jingjie._save_progress(category, name_field.value)
                close_dialog(e)
                # 刷新界面
                if self.jingjie.refresh_callback:
                    self.jingjie.refresh_callback()
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"添加{category}技能"),
            content=ft.Column(
                controls=[
                    name_field,
                    nodes_field,
                ],
                height=150,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_skill),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def show_edit_skill_dialog(self, page: ft.Page, category: str, skill_name: str):
        """显示编辑技能对话框"""
        skill_data = self.jingjie.skill_trees[category][skill_name]
        
        name_field = ft.TextField(label="技能名称", value=skill_name, width=300)
        nodes_field = ft.TextField(
            label="技能节点（用逗号分隔）", 
            value=", ".join(skill_data["nodes"]),
            width=300,
            multiline=True,
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_changes(e):
            if name_field.value and nodes_field.value:
                # 如果名称改变了，删除旧的
                if name_field.value != skill_name:
                    del self.jingjie.skill_trees[category][skill_name]
                
                nodes = [n.strip() for n in nodes_field.value.split(",")]
                # 更新技能树
                self.jingjie.skill_trees[category][name_field.value] = {
                    "nodes": nodes,
                    "completed": skill_data["completed"],
                    "realm": skill_data["realm"]
                }
                # 保存到数据库
                self.jingjie._save_progress(category, name_field.value)
                close_dialog(e)
                # 刷新界面
                if self.jingjie.refresh_callback:
                    self.jingjie.refresh_callback()
        
        def delete_skill(e):
            del self.jingjie.skill_trees[category][skill_name]
            close_dialog(e)
            if self.jingjie.refresh_callback:
                self.jingjie.refresh_callback()
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"编辑{category}技能"),
            content=ft.Column(
                controls=[
                    name_field,
                    nodes_field,
                ],
                height=150,
            ),
            actions=[
                ft.TextButton("删除", on_click=delete_skill, 
                             style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR)),
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_changes),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()