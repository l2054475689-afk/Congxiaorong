# systems/jingjie.py - 境界系统
import flet as ft
from database.db_manager import DatabaseManager
from config import GameConfig, ThemeConfig
from typing import List, Dict

class JingjieSystem:
    """境界系统 - 分为功法和秘术两大栏目"""
    
    # 类级别状态数据，所有实例共享
    _current_tab_index = 0  # 保存当前Tab索引：0=功法，1=秘术，2=副本

    # 数据结构
    _realm_data = {
        # 功法系统：用户自定义境界，按顺序解锁
        "gongfa": {
            "realms": [],  # 有序的境界列表 [{"name": "练气期", "skills": {}, "completed": False}, ...]
            "current_realm_index": 0  # 当前境界索引
        },
        # 秘术系统：独立的特长技能
        "secret_arts": {},
        # 副本系统：类似秘术的独立技能系统
        "fuben": {}
    }
        
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # 从数据库加载境界数据
        loaded_data = self.db.load_jingjie_data()
        JingjieSystem._realm_data = loaded_data
        self.realm_data = JingjieSystem._realm_data

    def _save_data(self):
        """保存境界数据到数据库"""
        if hasattr(self, 'db'):
            self.db.save_jingjie_data(self.realm_data)
    
    def get_current_realm(self) -> str:
        """获取当前境界名称"""
        current_index = self.realm_data["gongfa"]["current_realm_index"]
        realms = self.realm_data["gongfa"]["realms"]
        if 0 <= current_index < len(realms):
            return realms[current_index]["name"]
        return "无境界"
    
    def get_highest_realm(self) -> str:
        """获取当前最高境界（兼容旧接口）"""
        return self.get_current_realm()
    
    def _check_realm_completion(self, realm_index: int) -> bool:
        """检查指定境界是否完成"""
        realms = self.realm_data["gongfa"]["realms"]
        if realm_index >= len(realms):
            return False
            
        realm = realms[realm_index]
        skills = realm.get("skills", {})
        
        if not skills:
            return False  # 没有技能则未完成
        
        # 检查所有技能是否100%完成
        for skill_data in skills.values():
            nodes = skill_data.get("nodes", [])
            completed = skill_data.get("completed", [])
            if len(completed) != len(nodes) or len(nodes) == 0:
                return False
        
        return True
    
    def _try_realm_upgrade(self):
        """尝试境界升级"""
        current_index = self.realm_data["gongfa"]["current_realm_index"]
        realms = self.realm_data["gongfa"]["realms"]
        
        if current_index >= len(realms):
            return False
            
        # 检查当前境界是否完成
        if self._check_realm_completion(current_index):
            # 标记当前境界为完成
            realms[current_index]["completed"] = True
            
            # 如果不是最高境界，升级到下一境界
            if current_index < len(realms) - 1:
                self.realm_data["gongfa"]["current_realm_index"] = current_index + 1
                current_realm = realms[current_index]["name"]
                next_realm = realms[current_index + 1]["name"]
                print(f"🎉 恭喜！境界突破：{current_realm} → {next_realm}")
                return True
            else:
                current_realm = realms[current_index]["name"]
                print(f"🌟 已达到最高境界：{current_realm}")
        
        return False
    
    def _calculate_realm_progress(self, realm_index: int) -> float:
        """计算境界完成进度"""
        realms = self.realm_data["gongfa"]["realms"]
        if realm_index >= len(realms):
            return 0.0
            
        realm = realms[realm_index]
        skills = realm.get("skills", {})
        
        if not skills:
            return 0.0
        
        total_nodes = 0
        completed_nodes = 0
        
        for skill_data in skills.values():
            nodes = skill_data.get("nodes", [])
            completed = skill_data.get("completed", [])
            total_nodes += len(nodes)
            completed_nodes += len(completed)
        
        return completed_nodes / total_nodes if total_nodes > 0 else 0.0
    
    def _apply_skill_completion_effects(self, realm_name: str, skill_name: str, node: str, completed: bool):
        """应用技能完成的即时效果"""
        if completed:
            task_name = f"{realm_name}-{skill_name}-{node}"
            spirit_effect = 1  # 每个节点完成都增加1点心境
            blood_effect = 1   # 每个节点完成都增加1点血量
            task_category = "positive"  # 境界修炼都是正面任务
            
            print(f"完成{realm_name}【{skill_name}】节点【{node}】，心境+{spirit_effect}，血量+{blood_effect}")
            self._create_and_complete_task(task_name, task_category, spirit_effect, blood_effect)
    
    def _create_and_complete_task(self, name: str, category: str, spirit_effect: int, blood_effect: int):
        """创建境界任务并立即完成，用于在主页显示"""
        try:
            self.db.add_task(name, category, spirit_effect, blood_effect)
            tasks = self.db.get_tasks()
            if tasks:
                latest_task = max(tasks, key=lambda t: t.id)
                self.db.complete_task(latest_task.id, spirit_effect, blood_effect)
                print(f"境界修炼记录已添加到今日修炼: {name}")
        except Exception as e:
            print(f"创建境界任务记录时出错: {e}")
    
    def _calculate_skill_progress(self, skill_data: dict) -> float:
        """计算单个技能完成进度"""
        nodes = skill_data.get("nodes", [])
        completed = skill_data.get("completed", [])
        return len(completed) / len(nodes) if nodes else 0.0
    
    def _get_realm_color(self, realm_name: str) -> str:
        """获取境界对应颜色"""
        realms = self.realm_data["gongfa"]["realms"]
        colors = ["#9370DB", "#4169E1", "#32CD32", "#FFD700", "#FF6347", "#8A2BE2", "#00CED1"]
        
        for i, realm in enumerate(realms):
            if realm["name"] == realm_name:
                return colors[i % len(colors)]
        return "#999999"
    
    def _on_tab_change(self, e):
        """Tab切换时保存当前索引到类级别变量"""
        JingjieSystem._current_tab_index = e.control.selected_index
    
    def _toggle_node(self, realm_index: int, skill_name: str, node: str):
        """切换功法节点完成状态"""
        realms = self.realm_data["gongfa"]["realms"]
        if realm_index >= len(realms):
            print(f"未找到境界索引: {realm_index}")
            return
            
        realm = realms[realm_index]
        skill_data = realm.get("skills", {}).get(skill_name, {})
        
        if not skill_data:
            print(f"未找到技能数据: {realm['name']}/{skill_name}")
            return
        
        # 记录是否是完成操作
        is_completing = node not in skill_data["completed"]
        
        # 切换节点状态
        if node in skill_data["completed"]:
            skill_data["completed"].remove(node)
        else:
            skill_data["completed"].append(node)
        
        # 应用完成效果（仅当是完成操作时）
        if is_completing:
            self._apply_skill_completion_effects(realm["name"], skill_name, node, True)
        
        # 检查境界升级
        self._try_realm_upgrade()
        
        # 保存数据到数据库
        self._save_data()

    def create_jingjie_view(self, refresh_callback=None) -> ft.Column:
        """创建境界视图 - 功法和秘术两大栏目"""
        self.refresh_callback = refresh_callback
        
        current_realm = self.get_current_realm()
        current_index = self.realm_data["gongfa"]["current_realm_index"]
        current_progress = self._calculate_realm_progress(current_index)
        
        return ft.Column(
            controls=[
                # 标题栏和当前境界
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text("境界系统", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=ft.Text(current_realm, size=14, color="white"),
                                        bgcolor=self._get_realm_color(current_realm),
                                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                        border_radius=20,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            # 当前境界进度
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(f"当前境界：{current_realm}", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"修炼进度：{int(current_progress * 100)}%", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                        ft.ProgressBar(
                                            value=current_progress,
                                            color=ThemeConfig.PRIMARY_COLOR,
                                            bgcolor="#E0E0E0",
                                            height=8,
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                                margin=ft.margin.only(top=10),
                                bgcolor="#F8F9FA",
                                border_radius=8,
                            ),
                        ],
                        spacing=5,
                    ),
                    padding=20,
                ),
                
                # 功法、秘术、副本三大栏目
                ft.Container(
                    content=ft.Tabs(
                        selected_index=JingjieSystem._current_tab_index,
                        animation_duration=300,
                        on_change=self._on_tab_change,
                        tabs=[
                            ft.Tab(
                                text="功法",
                                icon=ft.icons.SCHOOL,
                                content=self._create_gongfa_content(),
                            ),
                            ft.Tab(
                                text="秘术",
                                icon=ft.icons.AUTO_AWESOME,
                                content=self._create_secret_arts_content(),
                            ),
                            ft.Tab(
                                text="副本",
                                icon=ft.icons.SPORTS_ESPORTS,
                                content=self._create_fuben_content(),
                            ),
                        ],
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                    expand=True,
                ),
            ],
            expand=True,
        )
    
    def _create_gongfa_content(self) -> ft.Column:
        """创建功法栏目内容"""
        return ft.Column(
            controls=[
                self._create_realm_management_section(),
                self._create_realm_list(),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
        )
    
    def _create_realm_management_section(self) -> ft.Container:
        """创建境界管理区域"""
        current_index = self.realm_data["gongfa"]["current_realm_index"]
        can_add_realm = (current_index > 0 and 
                        self._check_realm_completion(current_index - 1)) or current_index == 0
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("境界管理", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "添加新境界",
                                icon=ft.icons.ADD_CIRCLE,
                                bgcolor=ThemeConfig.PRIMARY_COLOR,
                                color="white",
                                disabled=not can_add_realm,
                                on_click=self._add_realm,
                            ),
                            ft.Text(
                                "完成当前境界后可添加下一境界" if not can_add_realm else "可以添加新境界",
                                size=12,
                                color=ThemeConfig.TEXT_SECONDARY,
                                italic=True,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=10,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(15),
            bgcolor="#F8F9FA",
            border_radius=10,
        )
    
    def _create_realm_list(self) -> ft.Column:
        """创建境界列表"""
        realms = self.realm_data["gongfa"]["realms"]
        current_index = self.realm_data["gongfa"]["current_realm_index"]
        
        realm_cards = []
        
        for i, realm in enumerate(realms):
            is_current = i == current_index
            is_accessible = i <= current_index
            is_completed = realm.get("completed", False)
            
            realm_cards.append(self._create_realm_card(
                realm, i, is_current, is_accessible, is_completed
            ))
        
        return ft.Column(
            controls=realm_cards,
            spacing=15,
        )
    
    def _create_realm_card(self, realm: dict, index: int, is_current: bool, is_accessible: bool, is_completed: bool) -> ft.Container:
        """创建境界卡片"""
        realm_name = realm["name"]
        skills = realm.get("skills", {})
        progress = self._calculate_realm_progress(index)
        
        # 状态图标
        if is_completed:
            status_icon = ft.Icon(ft.icons.CHECK_CIRCLE, color=ThemeConfig.SUCCESS_COLOR, size=20)
            status_text = "已完成"
        elif is_current:
            status_icon = ft.Icon(ft.icons.RADIO_BUTTON_CHECKED, color=ThemeConfig.PRIMARY_COLOR, size=20)
            status_text = "修炼中"
        elif is_accessible:
            status_icon = ft.Icon(ft.icons.RADIO_BUTTON_UNCHECKED, color=ThemeConfig.TEXT_SECONDARY, size=20)
            status_text = "可修炼"
        else:
            status_icon = ft.Icon(ft.icons.LOCK, color=ThemeConfig.TEXT_DISABLED, size=20)
            status_text = "未解锁"
        
        # 创建技能列表
        skill_widgets = []
        if is_accessible:
            # 添加技能按钮（仅当前境界可添加）
            if is_current:
                skill_widgets.append(
                    ft.Container(
                        content=ft.ElevatedButton(
                            f"添加{realm_name}功法",
                            icon=ft.icons.ADD,
                            bgcolor=ThemeConfig.PRIMARY_COLOR,
                            color="white",
                            on_click=lambda e, idx=index: self._add_skill(e, idx),
                        ),
                        margin=ft.margin.only(bottom=10),
                    )
                )
            
            # 显示技能
            if skills:
                for skill_name, skill_data in skills.items():
                    skill_progress = self._calculate_skill_progress(skill_data)
                    skill_widgets.append(self._create_skill_card_simple(
                        realm_name, skill_name, skill_data, skill_progress, is_current, index
                    ))
            else:
                skill_widgets.append(
                    ft.Container(
                        content=ft.Text(
                            f"暂无{realm_name}功法" if not is_current else f"点击上方按钮添加{realm_name}功法",
                            size=12,
                            color=ThemeConfig.TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER
                        ),
                        padding=10,
                        alignment=ft.alignment.center,
                    )
                )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    # 境界标题栏
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text(realm_name, size=18, weight=ft.FontWeight.BOLD),
                                                status_icon,
                                                ft.Text(status_text, size=12, color=ThemeConfig.TEXT_SECONDARY),
                                            ],
                                            spacing=8,
                                        ),
                                        ft.Text(f"进度：{int(progress * 100)}%", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                    ],
                                    spacing=5,
                                    expand=True,
                                ),
                                # 境界操作按钮
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            icon_size=18,
                                            tooltip="编辑境界名称",
                                            on_click=lambda e, idx=index: self._edit_realm(e, idx),
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            icon_size=18,
                                            icon_color=ThemeConfig.DANGER_COLOR,
                                            tooltip="删除境界",
                                            disabled=is_current or is_completed or len(self.realm_data["gongfa"]["realms"]) == 1,
                                            on_click=lambda e, idx=index: self._delete_realm(e, idx),
                                        ),
                                    ] if len(self.realm_data["gongfa"]["realms"]) > 1 else [],  # 至少保留一个境界
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.padding.only(bottom=10),
                    ),
                    
                    # 进度条
                    ft.ProgressBar(
                        value=progress,
                        color=self._get_realm_color(realm_name),
                        bgcolor="#E0E0E0",
                        height=8,
                    ),
                    
                    # 技能列表
                    ft.Container(
                        content=ft.Column(
                            controls=skill_widgets,
                            spacing=8,
                        ),
                        padding=ft.padding.only(top=10),
                    ),
                ],
                spacing=10,
            ),
            bgcolor=ThemeConfig.CARD_COLOR,
            padding=20,
            border_radius=12,
            border=ft.border.all(2, self._get_realm_color(realm_name)) if is_current else None,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color="#1A000000",
            ),
        )
    
    def _create_skill_card_simple(self, realm_name: str, skill_name: str, skill_data: dict, progress: float, is_current: bool, realm_index: int) -> ft.Container:
        """创建简单的技能卡片"""
        nodes = skill_data.get("nodes", [])
        completed = skill_data.get("completed", [])
        
        # 创建节点复选框列表
        node_widgets = []
        for node in nodes:
            is_completed = node in completed
            node_widgets.append(
                ft.Row(
                    controls=[
                        ft.Checkbox(
                            value=is_completed,
                            fill_color=ThemeConfig.SUCCESS_COLOR if is_completed else None,
                            on_change=lambda e, n=node: self._handle_node_toggle(e, realm_index, skill_name, n),
                            disabled=not is_current,
                        ),
                        ft.Text(
                            node,
                            size=14,
                            color=ThemeConfig.TEXT_PRIMARY if is_completed else ThemeConfig.TEXT_SECONDARY,
                        ),
                    ],
                    spacing=8,
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.icons.AUTO_STORIES_ROUNDED, size=18, color=ThemeConfig.PRIMARY_COLOR),
                                    ft.Text(skill_name, size=16, weight=ft.FontWeight.BOLD, color=ThemeConfig.TEXT_PRIMARY),
                                ],
                                spacing=8,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(f"{int(progress * 100)}%", size=12, color=ThemeConfig.PRIMARY_COLOR, weight=ft.FontWeight.W_500),
                                        bgcolor=ft.colors.with_opacity(0.1, ThemeConfig.PRIMARY_COLOR),
                                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                        border_radius=12,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE_OUTLINE_ROUNDED,
                                        icon_size=18,
                                        icon_color=ThemeConfig.DANGER_COLOR,
                                        tooltip="删除功法",
                                        on_click=lambda e, ri=realm_index, sn=skill_name: self._delete_skill(e, ri, sn),
                                    ),
                                ],
                                spacing=5,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(
                        content=ft.ProgressBar(
                            value=progress,
                            color=ThemeConfig.PRIMARY_COLOR,
                            bgcolor=ft.colors.with_opacity(0.1, ThemeConfig.PRIMARY_COLOR),
                            height=8,
                            border_radius=4,
                        ),
                        margin=ft.margin.only(top=8, bottom=10),
                    ),
                    ft.Column(
                        controls=node_widgets,
                        spacing=8,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=ThemeConfig.CARD_COLOR,
            padding=16,
            border_radius=12,
            border=ft.border.all(1, ThemeConfig.BORDER_LIGHT),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.colors.with_opacity(0.06, "#000000"),
                offset=ft.Offset(0, 2),
            ),
        )
    
    def _handle_node_toggle(self, e, realm_index: int, skill_name: str, node: str):
        """处理节点切换事件"""
        self._toggle_node(realm_index, skill_name, node)
        # 只更新当前控件，保持下拉框展开状态
        e.control.update()
    
    def _add_skill(self, e, realm_index: int):
        """添加技能"""
        try:
            page = e.page
            self._show_add_skill_dialog(page, realm_index)
        except Exception as ex:
            print(f"添加技能时出错: {ex}")
    
    def _show_add_skill_dialog(self, page, realm_index: int):
        """显示添加技能对话框"""
        name_field = ft.TextField(
            label="功法名称",
            width=300,
            autofocus=True,
            hint_text="请输入功法名称，如：数学、英语、跑步等"
        )
        
        nodes_field = ft.TextField(
            label="修炼节点（用逗号分隔）",
            width=300,
            multiline=True,
            value="基础,进阶,高级,精通",
            hint_text="多个节点用逗号分隔，如：函数,微积分,级数"
        )
        
        def close_dialog(e):
            page.dialog.open = False
            page.update()
        
        def save_skill(e):
            skill_name = name_field.value.strip()
            nodes_text = nodes_field.value.strip()
            
            if skill_name and nodes_text:
                skill_nodes = [node.strip() for node in nodes_text.split(',') if node.strip()]
                
                if skill_nodes:
                    realm_data = self.realm_data["gongfa"]["realms"][realm_index]
                    existing_skills = realm_data.get("skills", {})
                    
                    if skill_name in existing_skills:
                        print(f"错误：功法名称 '{skill_name}' 在{realm_data['name']}中已存在")
                        return
                    
                    new_skill = {
                        "nodes": skill_nodes,
                        "completed": [],
                    }
                    
                    if "skills" not in realm_data:
                        realm_data["skills"] = {}
                    
                    realm_data["skills"][skill_name] = new_skill
                    print(f"已添加{realm_data['name']}功法: {skill_name}，包含{len(skill_nodes)}个节点")
                    
                    # 保存数据到数据库
                    self._save_data()
                    
                    close_dialog(e)
                    if self.refresh_callback:
                        self.refresh_callback()
                else:
                    print("至少需要一个修炼节点")
            else:
                print("功法名称和修炼节点都不能为空")
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"添加{self.realm_data['gongfa']['realms'][realm_index]['name']}功法"),
            content=ft.Column(
                controls=[
                    ft.Text(f"为{self.realm_data['gongfa']['realms'][realm_index]['name']}添加新的修炼功法"),
                    name_field,
                    nodes_field,
                    ft.Text("完成此境界所有功法的所有节点后，将自动升级到下一境界", 
                           size=11, color=ThemeConfig.TEXT_SECONDARY, italic=True),
                ],
                height=250,
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("添加", on_click=save_skill),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()

    def _delete_skill(self, e, realm_index: int, skill_name: str):
        """删除功法"""
        try:
            page = e.page
            self._show_delete_skill_dialog(page, realm_index, skill_name)
        except Exception as ex:
            print(f"删除功法时出错: {ex}")

    def _show_delete_skill_dialog(self, page, realm_index: int, skill_name: str):
        """显示删除功法确认对话框"""
        realm_data = self.realm_data["gongfa"]["realms"][realm_index]
        realm_name = realm_data["name"]

        def close_dialog(e):
            page.dialog.open = False
            page.update()

        def confirm_delete(e):
            # 删除功法
            if "skills" in realm_data and skill_name in realm_data["skills"]:
                del realm_data["skills"][skill_name]

                # 保存数据
                self._save_data()

                # 关闭对话框
                close_dialog(e)

                # 刷新界面
                if self.refresh_callback:
                    self.refresh_callback()

                print(f"已从{realm_name}中删除功法：{skill_name}")

        dialog = ft.AlertDialog(
            title=ft.Text("确认删除", color=ThemeConfig.DANGER_COLOR),
            content=ft.Text(f"确定要从{realm_name}中删除功法「{skill_name}」吗？\n此操作不可恢复。"),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton(
                    "删除",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR),
                ),
            ],
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def _add_realm(self, e):
        """添加新境界"""
        try:
            page = e.page
            self._show_add_realm_dialog(page)
        except Exception as ex:
            print(f"添加境界时出错: {ex}")
    
    def _show_add_realm_dialog(self, page):
        """显示添加境界对话框"""
        name_field = ft.TextField(
            label="境界名称",
            width=300,
            autofocus=True,
            hint_text="请输入新境界名称，如：筑基期、结丹期等"
        )
        
        def close_dialog(e):
            page.dialog.open = False
            page.update()
        
        def save_realm(e):
            realm_name = name_field.value.strip()
            
            if realm_name:
                existing_realms = [realm["name"] for realm in self.realm_data["gongfa"]["realms"]]
                
                if realm_name in existing_realms:
                    print(f"错误：境界名称 '{realm_name}' 已存在")
                    return
                
                new_realm = {
                    "name": realm_name,
                    "skills": {},
                    "completed": False
                }
                
                self.realm_data["gongfa"]["realms"].append(new_realm)
                print(f"已添加新境界: {realm_name}")
                
                # 保存数据到数据库
                self._save_data()
                
                close_dialog(e)
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                print("境界名称不能为空")
        
        dialog = ft.AlertDialog(
            title=ft.Text("添加新境界"),
            content=ft.Column(
                controls=[
                    ft.Text("添加下一修炼境界"),
                    name_field,
                    ft.Text("新境界将在完成当前境界后自动解锁", 
                           size=11, color=ThemeConfig.TEXT_SECONDARY, italic=True),
                ],
                height=150,
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("添加", on_click=save_realm),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _create_secret_arts_content(self) -> ft.Column:
        """创建秘术内容"""
        return ft.Column(
            controls=[
                self._create_secret_arts_header(),
                self._create_secret_arts_list(),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
        )
    
    def _create_secret_arts_header(self) -> ft.Container:
        """创建秘术说明区域"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("秘术修炼", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text("特长技能", size=12, color="white"),
                                bgcolor=ThemeConfig.WARNING_COLOR,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                border_radius=10,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Text(
                        "秘术是功法主修之外的特长技能，不影响境界升级，但能提供额外的心境提升",
                        size=12,
                        color=ThemeConfig.TEXT_SECONDARY,
                    ),
                    ft.ElevatedButton(
                        "添加秘术",
                        icon=ft.icons.ADD,
                        bgcolor=ThemeConfig.WARNING_COLOR,
                        color="white",
                        on_click=lambda e: self._add_secret_art(e),
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(15),
            bgcolor="#FFF8E1",
            border_radius=10,
        )
    
    def _create_secret_arts_list(self) -> ft.Column:
        """创建秘术列表"""
        secret_arts = self.realm_data.get("secret_arts", {})
        
        skill_cards = []
        
        if not secret_arts:
            skill_cards.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.icons.AUTO_AWESOME, size=50, color=ThemeConfig.TEXT_DISABLED),
                            ft.Text(
                                "还未添加任何秘术",
                                size=16,
                                color=ThemeConfig.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Text(
                                "秘术是功法之外的特长技能\n点击上方按钮开始添加",
                                size=12,
                                color=ThemeConfig.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for art_name, art_data in secret_arts.items():
                progress = self._calculate_skill_progress(art_data)
                skill_cards.append(self._create_secret_art_card_simple(
                    art_name, art_data, progress
                ))
        
        return ft.Column(
            controls=skill_cards,
            spacing=15,
        )
    
    def _create_secret_art_card_simple(self, art_name: str, art_data: dict, progress: float) -> ft.Container:
        """创建简单的秘术卡片"""
        nodes = art_data.get("nodes", [])
        completed = art_data.get("completed", [])
        
        # 创建节点复选框列表
        node_widgets = []
        for node in nodes:
            is_completed = node in completed
            node_widgets.append(
                ft.Row(
                    controls=[
                        ft.Checkbox(
                            value=is_completed,
                            fill_color=ThemeConfig.SUCCESS_COLOR if is_completed else None,
                            on_change=lambda e, n=node: self._handle_secret_art_toggle(e, art_name, n),
                        ),
                        ft.Text(
                            node,
                            size=14,
                            color=ThemeConfig.TEXT_PRIMARY if is_completed else ThemeConfig.TEXT_SECONDARY,
                        ),
                    ],
                    spacing=8,
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(f"【{art_name}】", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text("秘术", size=11, color="white"),
                                bgcolor=ThemeConfig.WARNING_COLOR,
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                border_radius=10,
                            ),
                            ft.Text(f"{int(progress * 100)}%", size=12, color=ThemeConfig.TEXT_SECONDARY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ProgressBar(
                        value=progress,
                        color=ThemeConfig.WARNING_COLOR,
                        bgcolor="#E0E0E0",
                        height=6,
                    ),
                    ft.Column(
                        controls=node_widgets,
                        spacing=5,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=ThemeConfig.CARD_COLOR,
            padding=15,
            border_radius=10,
            border=ft.border.all(1, ThemeConfig.WARNING_COLOR),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color="#1A000000",
            ),
        )
    
    def _handle_secret_art_toggle(self, e, art_name: str, node: str):
        """处理秘术节点切换事件"""
        self._toggle_secret_art_node(art_name, node)
        e.control.update()
    
    def _toggle_secret_art_node(self, art_name: str, node: str):
        """切换秘术节点完成状态"""
        secret_arts = self.realm_data.get("secret_arts", {})
        art_data = secret_arts.get(art_name, {})
        
        if not art_data:
            print(f"未找到秘术数据: {art_name}")
            return
        
        # 记录是否是完成操作
        is_completing = node not in art_data["completed"]
        
        # 切换节点状态
        if node in art_data["completed"]:
            art_data["completed"].remove(node)
        else:
            art_data["completed"].append(node)
        
        # 应用完成效果（仅当是完成操作时）
        if is_completing:
            self._apply_secret_art_effects(art_name, node, True)
        
        # 保存数据到数据库
        self._save_data()
    
    def _apply_secret_art_effects(self, art_name: str, node: str, completed: bool):
        """应用秘术完成的即时效果"""
        if completed:
            task_name = f"秘术-{art_name}-{node}"
            spirit_effect = 2  # 秘术节点完成增加2点心境（比功法多）
            blood_effect = 0   # 秘术不增加血量
            task_category = "positive"  # 秘术修炼都是正面任务
            
            print(f"完成秘术【{art_name}】节点【{node}】，心境+{spirit_effect}")
            self._create_and_complete_task(task_name, task_category, spirit_effect, blood_effect)
    
    def _add_secret_art(self, e):
        """添加秘术"""
        try:
            page = e.page
            self._show_add_secret_art_dialog(page)
        except Exception as ex:
            print(f"添加秘术时出错: {ex}")
    
    def _show_add_secret_art_dialog(self, page):
        """显示添加秘术对话框"""
        name_field = ft.TextField(
            label="秘术名称",
            width=300,
            autofocus=True,
            hint_text="请输入秘术名称，如：紫微斗数、量化交易、Web开发等"
        )
        
        nodes_field = ft.TextField(
            label="学习节点（用逗号分隔）",
            width=300,
            multiline=True,
            value="基础,进阶,高级,精通",
            hint_text="多个节点用逗号分隔，如：八卦,星宿,命盘"
        )
        
        def close_dialog(e):
            page.dialog.open = False
            page.update()
        
        def save_secret_art(e):
            art_name = name_field.value.strip()
            nodes_text = nodes_field.value.strip()
            
            if art_name and nodes_text:
                art_nodes = [node.strip() for node in nodes_text.split(',') if node.strip()]
                
                if art_nodes:
                    existing_arts = self.realm_data.get("secret_arts", {})
                    
                    if art_name in existing_arts:
                        print(f"错误：秘术名称 '{art_name}' 已存在")
                        return
                    
                    new_art = {
                        "nodes": art_nodes,
                        "completed": [],
                    }
                    
                    if "secret_arts" not in self.realm_data:
                        self.realm_data["secret_arts"] = {}
                    
                    self.realm_data["secret_arts"][art_name] = new_art
                    print(f"已添加秘术: {art_name}，包含{len(art_nodes)}个节点")
                    
                    # 保存数据到数据库
                    self._save_data()
                    
                    close_dialog(e)
                    if self.refresh_callback:
                        self.refresh_callback()
                else:
                    print("至少需要一个学习节点")
            else:
                print("秘术名称和学习节点都不能为空")
        
        dialog = ft.AlertDialog(
            title=ft.Text("添加秘术"),
            content=ft.Column(
                controls=[
                    ft.Text("添加新的秘术特长技能"),
                    name_field,
                    nodes_field,
                    ft.Text("秘术是功法主修之外的特长技能，完成后不影响境界升级", 
                           size=11, color=ThemeConfig.TEXT_SECONDARY, italic=True),
                ],
                height=250,
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("添加", on_click=save_secret_art),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update() 
    
    def _edit_realm(self, e, realm_index: int):
        """编辑境界名称"""
        try:
            page = e.page
            self._show_edit_realm_dialog(page, realm_index)
        except Exception as ex:
            print(f"编辑境界时出错: {ex}")
    
    def _show_edit_realm_dialog(self, page, realm_index: int):
        """显示编辑境界对话框"""
        realms = self.realm_data["gongfa"]["realms"]
        if realm_index >= len(realms):
            print("境界索引错误")
            return
            
        realm = realms[realm_index]
        current_name = realm["name"]
        
        # 创建输入框，预填充当前境界名称
        name_field = ft.TextField(
            label="境界名称",
            value=current_name,
            width=300,
            autofocus=True,
        )
        
        def close_dialog(e):
            page.dialog.open = False
            page.update()
        
        def save_realm(e):
            new_name = name_field.value.strip()
            if new_name and new_name != current_name:
                # 检查新名称是否已存在
                existing_names = [r["name"] for i, r in enumerate(realms) if i != realm_index]
                if new_name in existing_names:
                    print(f"错误：境界名称 '{new_name}' 已存在")
                    return
                
                # 更新境界名称
                realm["name"] = new_name
                print(f"已重命名境界: {current_name} -> {new_name}")
                
                # 保存数据到数据库
                self._save_data()
                
                # 关闭对话框并刷新界面
                close_dialog(e)
                if self.refresh_callback:
                    self.refresh_callback()
            elif not new_name:
                print("境界名称不能为空")
            else:
                # 名称没有变化，直接关闭对话框
                close_dialog(e)
        
        # 创建对话框
        dialog = ft.AlertDialog(
            title=ft.Text("编辑境界"),
            content=ft.Column(
                controls=[
                    ft.Text(f"当前名称：{current_name}"),
                    name_field,
                ],
                height=120,
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_realm),
            ],
        )
        
        # 显示对话框
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _delete_realm(self, e, realm_index: int):
        """删除境界"""
        try:
            page = e.page
            self._show_delete_realm_dialog(page, realm_index)
        except Exception as ex:
            print(f"删除境界时出错: {ex}")
    
    def _show_delete_realm_dialog(self, page, realm_index: int):
        """显示删除境界确认对话框"""
        realms = self.realm_data["gongfa"]["realms"]
        if realm_index >= len(realms):
            print("境界索引错误")
            return
            
        realm = realms[realm_index]
        realm_name = realm["name"]
        
        def close_dialog(e):
            page.dialog.open = False
            page.update()
        
        def confirm_delete(e):
            # 删除境界
            del realms[realm_index]
            
            # 如果删除的是当前境界或之前的境界，需要调整当前境界索引
            current_index = self.realm_data["gongfa"]["current_realm_index"]
            if realm_index <= current_index:
                self.realm_data["gongfa"]["current_realm_index"] = max(0, current_index - 1)
            
            print(f"已删除境界: {realm_name}")
            
            # 保存数据到数据库
            self._save_data()
            
            # 关闭对话框并刷新界面
            close_dialog(e)
            if self.refresh_callback:
                self.refresh_callback()
        
        # 创建确认删除对话框
        dialog = ft.AlertDialog(
            title=ft.Text("确认删除", color=ThemeConfig.DANGER_COLOR),
            content=ft.Text(f"确定要删除境界「{realm_name}」吗？\n此操作将删除该境界下的所有功法，且不可恢复。"),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton(
                    "删除",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR)
                ),
            ],
        )

        # 显示对话框
        page.dialog = dialog
        dialog.open = True
        page.update()

    # =================== 副本系统相关方法 ===================

    def _create_fuben_content(self) -> ft.Column:
        """创建副本内容（类似秘术）"""
        return ft.Column(
            controls=[
                self._create_fuben_header(),
                self._create_fuben_list(),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
        )

    def _create_fuben_header(self) -> ft.Container:
        """创建副本说明区域"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("副本挑战", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text("挑战任务", size=12, color="white"),
                                bgcolor="#FF5722",
                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                border_radius=10,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Text(
                        "副本是类似游戏的挑战任务，完成副本节点可以获得心境和血量提升",
                        size=12,
                        color=ThemeConfig.TEXT_SECONDARY,
                    ),
                    ft.ElevatedButton(
                        "添加副本",
                        icon=ft.icons.ADD,
                        bgcolor="#FF5722",
                        color="white",
                        on_click=lambda e: self._add_fuben(e),
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.all(15),
            bgcolor="#FFEBEE",
            border_radius=10,
        )

    def _create_fuben_list(self) -> ft.Column:
        """创建副本列表"""
        fuben_data = self.realm_data.get("fuben", {})

        fuben_cards = []

        if not fuben_data:
            fuben_cards.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.icons.SPORTS_ESPORTS, size=50, color=ThemeConfig.TEXT_DISABLED),
                            ft.Text(
                                "还未添加任何副本",
                                size=16,
                                color=ThemeConfig.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Text(
                                "副本是挑战任务系统\n点击上方按钮开始添加",
                                size=12,
                                color=ThemeConfig.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        else:
            for fuben_name, fuben_info in fuben_data.items():
                progress = self._calculate_skill_progress(fuben_info)
                fuben_cards.append(self._create_fuben_card(
                    fuben_name, fuben_info, progress
                ))

        return ft.Column(
            controls=fuben_cards,
            spacing=15,
        )

    def _create_fuben_card(self, fuben_name: str, fuben_info: dict, progress: float) -> ft.Container:
        """创建副本卡片"""
        nodes = fuben_info.get("nodes", [])
        completed = fuben_info.get("completed", [])

        # 创建节点复选框列表
        node_widgets = []
        for node in nodes:
            is_completed = node in completed
            node_widgets.append(
                ft.Row(
                    controls=[
                        ft.Checkbox(
                            value=is_completed,
                            fill_color="#FF5722" if is_completed else None,
                            on_change=lambda e, n=node: self._handle_fuben_toggle(e, fuben_name, n),
                        ),
                        ft.Text(
                            node,
                            size=14,
                            color=ThemeConfig.TEXT_PRIMARY if is_completed else ThemeConfig.TEXT_SECONDARY,
                        ),
                    ],
                    spacing=8,
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.icons.SPORTS_ESPORTS_ROUNDED, size=20, color="#FF5722"),
                                    ft.Text(fuben_name, size=17, weight=ft.FontWeight.BOLD, color=ThemeConfig.TEXT_PRIMARY),
                                ],
                                spacing=8,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(f"{int(progress * 100)}%", size=12, color="white", weight=ft.FontWeight.W_500),
                                        bgcolor="#FF5722",
                                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                        border_radius=12,
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE_OUTLINE_ROUNDED,
                                        icon_size=20,
                                        icon_color=ThemeConfig.DANGER_COLOR,
                                        tooltip="删除副本",
                                        on_click=lambda e, fn=fuben_name: self._delete_fuben(e, fn),
                                    ),
                                ],
                                spacing=5,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(
                        content=ft.ProgressBar(
                            value=progress,
                            color="#FF5722",
                            bgcolor="#FFE5E0",
                            height=8,
                            border_radius=4,
                        ),
                        margin=ft.margin.only(top=8, bottom=12),
                    ),
                    ft.Column(
                        controls=node_widgets,
                        spacing=8,
                    ),
                ],
                spacing=0,
            ),
            bgcolor=ThemeConfig.CARD_COLOR,
            padding=20,
            border_radius=ThemeConfig.CARD_RADIUS,
            border=ft.border.all(1.5, "#FFE5E0"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.with_opacity(0.08, "#FF5722"),
                offset=ft.Offset(0, 2),
            ),
        )

    def _handle_fuben_toggle(self, e, fuben_name: str, node: str):
        """处理副本节点切换事件"""
        self._toggle_fuben_node(fuben_name, node)
        if self.refresh_callback:
            self.refresh_callback()

    def _toggle_fuben_node(self, fuben_name: str, node: str):
        """切换副本节点完成状态"""
        fuben_data = self.realm_data.get("fuben", {})
        fuben_info = fuben_data.get(fuben_name, {})

        if not fuben_info:
            print(f"未找到副本数据: {fuben_name}")
            return

        # 记录是否是完成操作
        is_completing = node not in fuben_info["completed"]

        # 切换节点状态
        if node in fuben_info["completed"]:
            fuben_info["completed"].remove(node)
        else:
            fuben_info["completed"].append(node)

        # 应用完成效果（仅当是完成操作时）
        if is_completing:
            self._apply_fuben_effects(fuben_name, node, True)

        # 保存数据到数据库
        self._save_data()

    def _apply_fuben_effects(self, fuben_name: str, node: str, completed: bool):
        """应用副本完成的即时效果"""
        if completed:
            task_name = f"副本-{fuben_name}-{node}"
            spirit_effect = 3  # 副本节点完成增加3点心境（比秘术多）
            blood_effect = 2   # 副本增加2点血量
            task_category = "positive"  # 副本挑战都是正面任务

            print(f"完成副本【{fuben_name}】节点【{node}】，心境+{spirit_effect}，血量+{blood_effect}")
            self._create_and_complete_task(task_name, task_category, spirit_effect, blood_effect)

    def _add_fuben(self, e):
        """添加副本"""
        page = e.page

        fuben_name_input = ft.TextField(label="副本名称", hint_text="例如：100天读书挑战")
        nodes_input = ft.TextField(
            label="挑战节点（用逗号分隔）",
            hint_text="例如：第1天,第10天,第30天,第100天",
            multiline=True,
        )

        def close_dialog(e):
            dialog.open = False
            page.update()

        def save_fuben(e):
            fuben_name = fuben_name_input.value.strip()
            nodes_text = nodes_input.value.strip()

            if not fuben_name or not nodes_text:
                return

            # 解析节点
            nodes = [node.strip() for node in nodes_text.split(",") if node.strip()]

            if not nodes:
                return

            # 添加副本到数据
            if "fuben" not in self.realm_data:
                self.realm_data["fuben"] = {}

            self.realm_data["fuben"][fuben_name] = {
                "nodes": nodes,
                "completed": []
            }

            # 保存数据
            self._save_data()

            # 关闭对话框
            close_dialog(e)

            # 刷新界面
            if self.refresh_callback:
                self.refresh_callback()

        dialog = ft.AlertDialog(
            title=ft.Text("添加副本"),
            content=ft.Column(
                controls=[
                    fuben_name_input,
                    nodes_input,
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_fuben),
            ],
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def _delete_fuben(self, e, fuben_name: str):
        """删除副本"""
        try:
            page = e.page
            self._show_delete_fuben_dialog(page, fuben_name)
        except Exception as ex:
            print(f"删除副本时出错: {ex}")

    def _show_delete_fuben_dialog(self, page, fuben_name: str):
        """显示删除副本确认对话框"""
        def close_dialog(e):
            page.dialog.open = False
            page.update()

        def confirm_delete(e):
            # 删除副本
            if "fuben" in self.realm_data and fuben_name in self.realm_data["fuben"]:
                del self.realm_data["fuben"][fuben_name]

                # 保存数据
                self._save_data()

                # 关闭对话框
                close_dialog(e)

                # 刷新界面
                if self.refresh_callback:
                    self.refresh_callback()

                print(f"已删除副本：{fuben_name}")

        dialog = ft.AlertDialog(
            title=ft.Text("确认删除", color=ThemeConfig.DANGER_COLOR),
            content=ft.Text(f"确定要删除副本「{fuben_name}」吗？此操作不可恢复。"),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton(
                    "删除",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR),
                ),
            ],
        )

        page.dialog = dialog
        dialog.open = True
        page.update() 