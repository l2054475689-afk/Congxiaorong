import flet as ft
from database.db_manager import DatabaseManager
from database.models import FamilyMember, FamilyEvent, Friend, FriendRelation, FriendTask, InteractionRecord
from config import ThemeConfig
from datetime import datetime
from typing import List, Dict, Optional

class TongyuSystem:
    """统御系统 - 人际关系管理（完整功能版）"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.current_tab_index = 0  # 保持当前标签页状态
        self.tabs_ref = None  # 标签页引用
        
    def create_tongyu_view(self, refresh_callback=None) -> ft.Column:
        """创建统御视图"""
        self.refresh_callback = refresh_callback
        
        # 创建标签页控件
        self.tabs_ref = ft.Tabs(
            selected_index=self.current_tab_index,
            animation_duration=300,
            on_change=self._on_tab_change,
            tabs=[
                ft.Tab(
                    text="家族",
                    icon=ft.icons.HOME,
                    content=self._create_family_view(),
                ),
                ft.Tab(
                    text="朋友",
                    icon=ft.icons.PEOPLE,
                    content=self._create_friends_view(),
                ),
                ft.Tab(
                    text="关系网",
                    icon=ft.icons.ACCOUNT_TREE,
                    content=self._create_network_view(),
                ),
            ],
        )
        
        return ft.Column(
            controls=[
                # 标题栏
                ft.Container(
                    content=ft.Text("统御系统", size=20, weight=ft.FontWeight.BOLD),
                    padding=20,
                ),
                
                # 标签页
                ft.Container(
                    content=self.tabs_ref,
                    padding=ft.padding.symmetric(horizontal=20),
                    expand=True,
                ),
            ],
            expand=True,
        )
    
    def _on_tab_change(self, e):
        """标签页切换事件"""
        self.current_tab_index = e.control.selected_index
    
    def _refresh_current_tab(self):
        """刷新当前标签页内容，保持标签页状态"""
        if self.tabs_ref is None:
            return
            
        try:
            current_index = self.current_tab_index
            
            # 重新创建对应标签页的内容
            if current_index == 0:  # 家族标签页
                new_content = self._create_family_view()
                self.tabs_ref.tabs[0].content = new_content
            elif current_index == 1:  # 朋友标签页
                new_content = self._create_friends_view()
                self.tabs_ref.tabs[1].content = new_content
            elif current_index == 2:  # 关系网标签页
                new_content = self._create_network_view()
                self.tabs_ref.tabs[2].content = new_content
            
            # 保持当前标签页选中状态
            self.tabs_ref.selected_index = current_index
            
            # 更新页面
            if hasattr(self.tabs_ref, 'page') and self.tabs_ref.page:
                self.tabs_ref.page.update()
        except Exception as e:
            print(f"刷新标签页错误: {e}")
    
    def _create_family_view(self) -> ft.Column:
        """创建家族视图"""
        family_members = self.db.get_family_members()
        family_cards = []
        
        for member in family_members:
            # 获取该成员的事件
            events = self.db.get_family_events(member.id)
            family_cards.append(self._create_family_card(member, events))
        
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("家族成员", size=16, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.ADD,
                                bgcolor=ThemeConfig.PRIMARY_COLOR,
                                icon_color="white",
                                on_click=self._add_family_member,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(bottom=10),
                ),
                *family_cards,
                
                # 家族事件提醒
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("【即将到来的事件】", size=14, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=1),
                            *self._get_upcoming_family_events(),
                        ],
                        spacing=8,
                    ),
                    bgcolor=ThemeConfig.CARD_COLOR,
                    padding=15,
                    border_radius=10,
                    margin=ft.margin.only(top=20),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
        )
    
    def _create_family_card(self, member: FamilyMember, events: List[FamilyEvent]) -> ft.Container:
        """创建家族成员卡片"""
        # 计算年龄
        birth_year = int(member.birthday.split("-")[0])
        age = datetime.now().year - birth_year
        
        # 事件列表组件
        event_controls = []
        for event in events[:3]:  # 只显示前3个事件
            event_controls.append(
                ft.Row(
                    controls=[
                        ft.Checkbox(
                            value=event.completed,
                            scale=0.8,
                            on_change=lambda e, ev=event: self._toggle_family_event(e, ev),
                        ),
                        ft.Text(event.event_date, size=12, color=ThemeConfig.TEXT_SECONDARY),
                        ft.Text(event.event_name, size=13),
                    ],
                )
            )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(member.name, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{age}岁 | {member.phone}", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                ],
                                spacing=5,
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                icon_size=18,
                                on_click=lambda e, m=member: self._edit_family_member(e, m),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    
                    ft.Container(
                        content=ft.Text(member.notes, size=13, color=ThemeConfig.TEXT_SECONDARY),
                        padding=ft.padding.only(top=5),
                    ),
                    
                    # 事件列表
                    ft.Container(
                        content=ft.Column(
                            controls=event_controls,
                            spacing=5,
                        ),
                        padding=ft.padding.only(top=5),
                    ) if event_controls else ft.Container(),
                ],
                spacing=8,
            ),
            bgcolor=ThemeConfig.CARD_COLOR,
            padding=15,
            border_radius=10,
        )
    
    def _create_friends_view(self) -> ft.Column:
        """创建朋友视图"""
        friends = self.db.get_friends()
        
        # 按类别分组
        friend_groups = {}
        for friend in friends:
            category = friend.category
            if category not in friend_groups:
                friend_groups[category] = []
            friend_groups[category].append(friend)
        
        # 添加密友标识
        close_friends = [f for f in friends if f.is_close_friend]
        if close_friends:
            friend_groups["💝 密友"] = close_friends
        
        friend_sections = []
        for category, friends_in_category in friend_groups.items():
            if category == "💝 密友":
                # 跳过密友分组，因为已经在其他类别中显示了
                continue
                
            friend_sections.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(f"【{category}】", size=14, weight=ft.FontWeight.BOLD),
                            *[self._create_friend_card(friend) for friend in friends_in_category],
                        ],
                        spacing=10,
                    ),
                    margin=ft.margin.only(bottom=15),
                )
            )
        
        # 单独显示密友分组
        if close_friends:
            friend_sections.insert(0,
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("【💝 密友】", size=14, weight=ft.FontWeight.BOLD, color=ThemeConfig.PRIMARY_COLOR),
                            *[self._create_friend_card(friend, is_close=True) for friend in close_friends],
                        ],
                        spacing=10,
                    ),
                    margin=ft.margin.only(bottom=15),
                )
            )
        
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("朋友档案", size=16, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.PERSON_ADD,
                                bgcolor=ThemeConfig.PRIMARY_COLOR,
                                icon_color="white",
                                on_click=self._add_friend,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(bottom=10),
                ),
                *friend_sections,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        )
    
    def _create_friend_card(self, friend: Friend, is_close: bool = False) -> ft.Container:
        """创建朋友卡片"""
        # 计算多久没联系
        if friend.last_contact:
            last_contact = datetime.strptime(friend.last_contact, "%Y-%m-%d")
            days_ago = (datetime.now() - last_contact).days
            contact_text = f"上次联系: {days_ago}天前"
            contact_color = ThemeConfig.DANGER_COLOR if days_ago > 30 else ThemeConfig.TEXT_SECONDARY
        else:
            contact_text = "从未联系"
            contact_color = ThemeConfig.DANGER_COLOR
        
        # 获取朋友任务数量
        friend_tasks = self.db.get_friend_tasks(friend.id)
        task_count = len(friend_tasks)
        completed_tasks = len([t for t in friend_tasks if t.completed])
        
        # 密友标识
        close_friend_indicator = ft.Icon(
            ft.icons.FAVORITE, 
            size=16, 
            color=ThemeConfig.PRIMARY_COLOR
        ) if friend.is_close_friend else ft.Container()
        
        return ft.Container(
            content=ft.ExpansionTile(
                title=ft.Row(
                    controls=[
                        ft.Text(friend.name, size=14, weight=ft.FontWeight.BOLD),
                        close_friend_indicator,
                    ],
                    spacing=5,
                ),
                subtitle=ft.Column(
                    controls=[
                        ft.Text(contact_text, size=12, color=contact_color),
                        ft.Text(f"任务: {completed_tasks}/{task_count}", size=11, color=ThemeConfig.PRIMARY_COLOR) if task_count > 0 else ft.Container(),
                    ],
                    spacing=2,
                ),
                initially_expanded=False,
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row([
                                    ft.Text("性格:", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                    ft.Text(friend.personality, size=12),
                                ]),
                                ft.Row([
                                    ft.Text("爱好:", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                    ft.Text(friend.hobbies, size=12),
                                ]),
                                ft.Row([
                                    ft.Text("备注:", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                    ft.Text(friend.notes, size=12),
                                ]),

                                
                                # 操作按钮
                                ft.Row(
                                    controls=[
                                        ft.TextButton(
                                            "记录互动",
                                            icon=ft.icons.CHAT,
                                            on_click=lambda e, f=friend: self._record_interaction(e, f),
                                        ),
                                        ft.TextButton(
                                            "管理任务",
                                            icon=ft.icons.TASK_ALT,
                                            on_click=lambda e, f=friend: self._manage_friend_tasks(e, f),
                                        ),

                                        ft.TextButton(
                                            "编辑",
                                            icon=ft.icons.EDIT,
                                            on_click=lambda e, f=friend: self._edit_friend(e, f),
                                        ),
                                    ],
                                    wrap=True,
                                ),
                            ],
                            spacing=8,
                        ),
                        padding=ft.padding.symmetric(horizontal=15),
                    ),
                ],
            ),
            bgcolor=ThemeConfig.CARD_COLOR,
            border_radius=10,
            border=ft.border.all(2, ThemeConfig.PRIMARY_COLOR) if is_close else None,
        )
    
    def _create_network_view(self) -> ft.Column:
        """创建关系网视图"""
        friends = self.db.get_friends()
        family_members = self.db.get_family_members()
        
        # 统计数据
        total_family = len(family_members)
        total_friends = len(friends)
        close_friends = len([f for f in friends if f.is_close_friend])
        
        # 关系分类统计
        friend_categories = {}
        for friend in friends:
            category = friend.category
            friend_categories[category] = friend_categories.get(category, 0) + 1
        
        # 互动活跃度分析
        active_friends = 0
        inactive_friends = 0
        for friend in friends:
            if friend.last_contact:
                last_contact = datetime.strptime(friend.last_contact, "%Y-%m-%d")
                days_ago = (datetime.now() - last_contact).days
                if days_ago <= 30:
                    active_friends += 1
                else:
                    inactive_friends += 1
            else:
                inactive_friends += 1
        
        return ft.Column(
            controls=[
                # 统计卡片
                ft.Row(
                    controls=[
                        self._create_stat_card("家族成员", str(total_family), ft.icons.HOME),
                        self._create_stat_card("朋友总数", str(total_friends), ft.icons.PEOPLE),
                        self._create_stat_card("密友数量", str(close_friends), ft.icons.FAVORITE),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                ),
                
                # 朋友分类统计
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("【朋友分类】", size=14, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=1),
                            *[
                                ft.Row(
                                    controls=[
                                        ft.Text(category, size=13),
                                        ft.Text(f"{count}人", size=13, color=ThemeConfig.PRIMARY_COLOR),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                )
                                for category, count in friend_categories.items()
                            ],
                        ],
                        spacing=10,
                    ),
                    bgcolor=ThemeConfig.CARD_COLOR,
                    padding=15,
                    border_radius=10,
                    margin=ft.margin.only(top=20),
                ),
                
                # 互动活跃度
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("【互动活跃度】", size=14, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=1),
                            ft.Row(
                                controls=[
                                    ft.Text("近期活跃", size=13),
                                    ft.Text(f"{active_friends}人", size=13, color="#4CAF50"),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text("需要联系", size=13),
                                    ft.Text(f"{inactive_friends}人", size=13, color=ThemeConfig.DANGER_COLOR),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor=ThemeConfig.CARD_COLOR,
                    padding=15,
                    border_radius=10,
                    margin=ft.margin.only(top=15),
                ),
                
                # 关系维护建议
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("【维护建议】", size=14, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=1),
                            ft.Text(f"• 超过30天未联系的朋友有{inactive_friends}人", size=13),
                            ft.Text(f"• 密友数量: {close_friends}人（任务>10个自动标注）", size=13),
                            ft.Text("• 建议每月至少与挚友联系一次", size=13),
                            ft.Text("• 定期添加朋友互动任务增进关系", size=13),
                        ],
                        spacing=8,
                    ),
                    bgcolor="#FFF9E6",
                    padding=15,
                    border_radius=10,
                    margin=ft.margin.only(top=15),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
        )
    
    def _create_stat_card(self, title: str, value: str, icon) -> ft.Container:
        """创建统计卡片"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=30, color=ThemeConfig.PRIMARY_COLOR),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(title, size=12, color=ThemeConfig.TEXT_SECONDARY),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ThemeConfig.CARD_COLOR,
            padding=20,
            border_radius=10,
            width=110,
        )
    
    def _get_upcoming_family_events(self) -> list:
        """获取即将到来的家族事件"""
        all_events = self.db.get_family_events()
        family_members = {m.id: m.name for m in self.db.get_family_members()}
        
        events = []
        for event in all_events:
            if not event.completed:
                member_name = family_members.get(event.member_id, "未知")
                events.append(
                    ft.Row(
                        controls=[
                            ft.Text(event.event_date, size=12, color=ThemeConfig.TEXT_SECONDARY),
                            ft.Text(f"{member_name}的{event.event_name}", size=13),
                        ],
                    )
                )
        
        return events[:5] if events else [ft.Text("暂无待办事件", size=13, color=ThemeConfig.TEXT_SECONDARY)]
    

    
    # =================== 家族成员操作方法 ===================
    
    def _add_family_member(self, e):
        """添加家族成员"""
        page = e.page
        
        name_field = ft.TextField(label="姓名", width=300)
        birthday_field = ft.TextField(
            label="生日", 
            hint_text="YYYY-MM-DD",
            width=300
        )
        phone_field = ft.TextField(label="电话", width=300)
        notes_field = ft.TextField(
            label="备注",
            multiline=True,
            width=300
        )
        event_field = ft.TextField(label="初始事件（可选）", width=300)
        event_date_field = ft.TextField(
            label="事件日期", 
            hint_text="YYYY-MM-DD",
            width=300
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_member(e):
            if name_field.value and birthday_field.value:
                # 添加家族成员
                success = self.db.add_family_member(
                    name=name_field.value,
                    birthday=birthday_field.value,
                    phone=phone_field.value or "",
                    notes=notes_field.value or ""
                )
                
                if success:
                    print(f"成功添加家族成员: {name_field.value}")
                    
                    # 如果有初始事件，也添加进去
                    if event_field.value and event_date_field.value:
                        # 获取刚添加的成员ID（通过名字查找）
                        members = self.db.get_family_members()
                        new_member = next((m for m in members if m.name == name_field.value), None)
                        if new_member:
                            self.db.add_family_event(
                                member_id=new_member.id,
                                event_name=event_field.value,
                                event_date=event_date_field.value
                            )
                    
                    close_dialog(e)
                    self._refresh_current_tab()
                else:
                    print("添加家族成员失败")
        
        dialog = ft.AlertDialog(
            title=ft.Text("添加家族成员"),
            content=ft.Column(
                controls=[
                    name_field,
                    birthday_field,
                    phone_field,
                    notes_field,
                    event_field,
                    event_date_field,
                ],
                height=350,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_member),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _edit_family_member(self, e, member: FamilyMember):
        """编辑家族成员"""
        page = e.page
        
        name_field = ft.TextField(label="姓名", value=member.name, width=300)
        birthday_field = ft.TextField(
            label="生日",
            value=member.birthday,
            hint_text="YYYY-MM-DD",
            width=300
        )
        phone_field = ft.TextField(label="电话", value=member.phone, width=300)
        notes_field = ft.TextField(
            label="备注",
            value=member.notes,
            multiline=True,
            width=300
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_changes(e):
            if name_field.value and birthday_field.value:
                success = self.db.update_family_member(
                    member_id=member.id,
                    name=name_field.value,
                    birthday=birthday_field.value,
                    phone=phone_field.value or "",
                    notes=notes_field.value or ""
                )
                
                if success:
                    print(f"成功编辑家族成员: {name_field.value}")
                    close_dialog(e)
                    self._refresh_current_tab()
                else:
                    print("编辑家族成员失败")
        
        def delete_member(e):
            success = self.db.delete_family_member(member.id)
            if success:
                print(f"成功删除家族成员: {member.name}")
                close_dialog(e)
                self._refresh_current_tab()
            else:
                print("删除家族成员失败")
        
        dialog = ft.AlertDialog(
            title=ft.Text("编辑家族成员"),
            content=ft.Column(
                controls=[
                    name_field,
                    birthday_field,
                    phone_field,
                    notes_field,
                ],
                height=250,
            ),
            actions=[
                ft.TextButton("删除", on_click=delete_member,
                            style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR)),
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_changes),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _toggle_family_event(self, e, event: FamilyEvent):
        """切换家族事件完成状态"""
        success = self.db.toggle_family_event(event.id, e.control.value)
        if success:
            print(f"{'完成' if e.control.value else '取消'}事件: {event.event_name}")
            # 不需要刷新整个页面，只更新当前控件即可
        else:
            print("更新事件状态失败")
            # 回滚UI状态
            e.control.value = not e.control.value
        e.page.update()
    
    # =================== 朋友操作方法 ===================
    
    def _add_friend(self, e):
        """添加朋友"""
        page = e.page
        
        name_field = ft.TextField(label="姓名", width=300)
        category_dropdown = ft.Dropdown(
            label="关系类型",
            width=300,
            options=[
                ft.dropdown.Option("挚友"),
                ft.dropdown.Option("同事"),
                ft.dropdown.Option("同学"),
                ft.dropdown.Option("邻居"),
                ft.dropdown.Option("合作伙伴"),
                ft.dropdown.Option("其他"),
            ],
            value="朋友",
        )
        personality_field = ft.TextField(label="性格特点", width=300)
        hobbies_field = ft.TextField(label="兴趣爱好", width=300)
        notes_field = ft.TextField(
            label="备注",
            multiline=True,
            width=300
        )
        
        # 朋友关联选择
        existing_friends = self.db.get_friends()
        relation_checkboxes = []
        if existing_friends:
            relation_checkboxes = [
                ft.Checkbox(
                    label=friend.name,
                    value=False,
                    data=friend.id
                )
                for friend in existing_friends
            ]
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_friend(e):
            if name_field.value:
                # 添加朋友
                friend_id = self.db.add_friend(
                    name=name_field.value,
                    category=category_dropdown.value,
                    personality=personality_field.value or "",
                    hobbies=hobbies_field.value or "",
                    notes=notes_field.value or ""
                )
                
                if friend_id:
                    print(f"成功添加朋友: {name_field.value}")
                    
                    # 添加朋友关系
                    for checkbox in relation_checkboxes:
                        if checkbox.value:
                            self.db.add_friend_relation(friend_id, checkbox.data, "acquaintance")
                    
                    close_dialog(e)
                    self._refresh_current_tab()
                else:
                    print("添加朋友失败")
        
        # 构建对话框内容
        dialog_controls = [
            name_field,
            category_dropdown,
            personality_field,
            hobbies_field,
            notes_field,
        ]
        
        if relation_checkboxes:
            dialog_controls.extend([
                ft.Divider(),
                ft.Text("选择认识的朋友:", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column(
                        controls=relation_checkboxes,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    height=100,
                ),
            ])
        
        dialog = ft.AlertDialog(
            title=ft.Text("添加朋友"),
            content=ft.Column(
                controls=dialog_controls,
                height=400 if relation_checkboxes else 300,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_friend),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _edit_friend(self, e, friend: Friend):
        """编辑朋友信息"""
        page = e.page
        
        name_field = ft.TextField(label="姓名", value=friend.name, width=300)
        category_dropdown = ft.Dropdown(
            label="关系类型",
            width=300,
            options=[
                ft.dropdown.Option("挚友"),
                ft.dropdown.Option("同事"),
                ft.dropdown.Option("同学"),
                ft.dropdown.Option("邻居"),
                ft.dropdown.Option("合作伙伴"),
                ft.dropdown.Option("其他"),
            ],
            value=friend.category,
        )
        personality_field = ft.TextField(label="性格特点", value=friend.personality, width=300)
        hobbies_field = ft.TextField(label="兴趣爱好", value=friend.hobbies, width=300)
        notes_field = ft.TextField(
            label="备注",
            value=friend.notes,
            multiline=True,
            width=300
        )

        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_changes(e):
            if name_field.value:
                success = self.db.update_friend(
                    friend_id=friend.id,
                    name=name_field.value,
                    category=category_dropdown.value,
                    personality=personality_field.value or "",
                    hobbies=hobbies_field.value or "",
                    notes=notes_field.value or "",
                    ai_analysis=None
                )
                
                if success:
                    print(f"成功编辑朋友: {name_field.value}")
                    close_dialog(e)
                    self._refresh_current_tab()
                else:
                    print("编辑朋友失败")
        
        def delete_friend(e):
            success = self.db.delete_friend(friend.id)
            if success:
                print(f"成功删除朋友: {friend.name}")
                close_dialog(e)
                self._refresh_current_tab()
            else:
                print("删除朋友失败")
        
        dialog = ft.AlertDialog(
            title=ft.Text("编辑朋友信息"),
            content=ft.Column(
                controls=[
                    name_field,
                    category_dropdown,
                    personality_field,
                    hobbies_field,
                    notes_field,
                ],
                height=300,
            ),
            actions=[
                ft.TextButton("删除", on_click=delete_friend,
                            style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR)),
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_changes),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _record_interaction(self, e, friend: Friend):
        """记录互动"""
        page = e.page
        
        interaction_field = ft.TextField(
            label="互动内容",
            multiline=True,
            width=300,
            height=100
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_interaction(e):
            if interaction_field.value:
                today = datetime.now().strftime("%Y-%m-%d")
                success = self.db.add_interaction_record(
                    friend_id=friend.id,
                    content=interaction_field.value,
                    interaction_date=today
                )
                
                if success:
                    print(f"成功记录与{friend.name}的互动")
                    close_dialog(e)
                    self._refresh_current_tab()
                else:
                    print("记录互动失败")
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"记录与{friend.name}的互动"),
            content=ft.Column(
                controls=[
                    ft.Text("记录今天的互动内容："),
                    interaction_field,
                ],
                height=150,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_interaction),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _manage_friend_tasks(self, e, friend: Friend):
        """管理朋友任务"""
        page = e.page
        
        # 获取朋友任务列表
        friend_tasks = self.db.get_friend_tasks(friend.id)
        
        # 创建任务列表
        task_controls = []
        for task in friend_tasks:
            reward_text = f"{task.reward_amount}"
            if task.reward_type == "spirit":
                reward_text += " 心境"
            elif task.reward_type == "blood":
                reward_text += " 血量"
            elif task.reward_type == "money":
                reward_text += " 灵石"
            
            task_controls.append(
                ft.Row(
                    controls=[
                        ft.Checkbox(
                            value=task.completed,
                            on_change=lambda e, t=task: self._toggle_friend_task(e, t),
                        ),
                        ft.Text(task.task_name, size=13, expand=True),
                        ft.Text(f"奖励: {reward_text}", size=12, color="#4CAF50"),
                    ],
                )
            )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def add_new_task(e):
            self._add_friend_task(e, friend)
            close_dialog(e)
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"{friend.name}的任务管理"),
            content=ft.Column(
                controls=[
                    ft.Text(f"任务总数: {len(friend_tasks)}, 已完成: {len([t for t in friend_tasks if t.completed])}", 
                           size=14, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Column(
                            controls=task_controls if task_controls else [
                                ft.Text("暂无任务", size=13, color=ThemeConfig.TEXT_SECONDARY)
                            ],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        height=200,
                    ),
                ],
                height=250,
            ),
            actions=[
                ft.TextButton("添加任务", on_click=add_new_task),
                ft.TextButton("关闭", on_click=close_dialog),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _add_friend_task(self, e, friend: Friend):
        """添加朋友任务"""
        page = e.page
        
        task_name_field = ft.TextField(label="任务名称", width=300)
        reward_type_dropdown = ft.Dropdown(
            label="奖励类型",
            width=300,
            options=[
                ft.dropdown.Option("spirit", "心境"),
                ft.dropdown.Option("blood", "血量"),
                ft.dropdown.Option("money", "灵石"),
            ],
            value="spirit",
        )
        reward_amount_field = ft.TextField(
            label="奖励数量",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_task(e):
            if task_name_field.value and reward_amount_field.value:
                try:
                    reward_amount = int(reward_amount_field.value)
                    success = self.db.add_friend_task(
                        friend_id=friend.id,
                        task_name=task_name_field.value,
                        reward_type=reward_type_dropdown.value,
                        reward_amount=reward_amount
                    )
                    
                    if success:
                        print(f"成功为{friend.name}添加任务: {task_name_field.value}")
                        close_dialog(e)
                        self._refresh_current_tab()
                    else:
                        print("添加任务失败")
                except ValueError:
                    print("奖励数量必须是数字")
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"为{friend.name}添加任务"),
            content=ft.Column(
                controls=[
                    task_name_field,
                    reward_type_dropdown,
                    reward_amount_field,
                    ft.Text("提示：任务数量超过10个将自动标注为密友", 
                           size=12, color=ThemeConfig.TEXT_SECONDARY),
                ],
                height=200,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_task),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _toggle_friend_task(self, e, task: FriendTask):
        """切换朋友任务完成状态"""
        if e.control.value and not task.completed:
            # 完成任务
            success = self.db.complete_friend_task(task.id)
            if success:
                print(f"完成朋友任务: {task.task_name}")
                # 刷新当前页面以更新密友状态
                self._refresh_current_tab()
            else:
                print("完成任务失败")
                e.control.value = False
        elif not e.control.value and task.completed:
            # 取消完成（这里可以根据需要实现逆向操作）
            print("任务已完成，无法取消")
            e.control.value = True
        
        e.page.update() 