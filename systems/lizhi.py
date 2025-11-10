# systems/lizhi.py - 励志库系统
import flet as ft
from database.db_manager import DatabaseManager
from config import ThemeConfig
from typing import List

class LizhiSystem:
    """励志库系统 - 管理励志诗句"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def create_lizhi_view(self, refresh_callback=None) -> ft.Column:
        """创建励志库视图"""
        self.refresh_callback = refresh_callback

        return ft.Column(
            controls=[
                # 标题栏
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("励志库", size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text("诗句名言", size=12, color="white"),
                                bgcolor=ThemeConfig.PRIMARY_COLOR,
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                border_radius=20,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=20,
                ),

                # 说明和添加按钮
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "在这里管理你的励志诗句，每次启动应用时会随机显示一条",
                                size=14,
                                color=ThemeConfig.TEXT_SECONDARY,
                            ),
                            ft.ElevatedButton(
                                "添加励志语录",
                                icon=ft.icons.ADD_CIRCLE,
                                bgcolor=ThemeConfig.PRIMARY_COLOR,
                                color="white",
                                on_click=self._add_quote_dialog,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                    bgcolor="#F8F9FA",
                    margin=ft.margin.symmetric(horizontal=20),
                    border_radius=10,
                ),

                # 励志语录列表
                ft.Container(
                    content=self._create_quotes_list(),
                    padding=ft.padding.symmetric(horizontal=20),
                    expand=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _create_quotes_list(self) -> ft.Column:
        """创建励志语录列表"""
        quotes = self.db.get_all_quotes()

        if not quotes:
            return ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.icons.FORMAT_QUOTE, size=50, color=ThemeConfig.TEXT_DISABLED),
                                ft.Text(
                                    "还没有添加任何励志语录",
                                    size=16,
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
                ],
            )

        quote_cards = []
        for quote in quotes:
            quote_id, content, author, category, created_at = quote
            quote_cards.append(self._create_quote_card(quote_id, content, author))

        return ft.Column(
            controls=quote_cards,
            spacing=10,
        )

    def _create_quote_card(self, quote_id: int, content: str, author: str) -> ft.Container:
        """创建单条语录卡片"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.icons.FORMAT_QUOTE, size=20, color=ThemeConfig.PRIMARY_COLOR),
                            ft.Text(
                                content,
                                size=15,
                                weight=ft.FontWeight.W_500,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"—— {author}",
                                size=12,
                                color=ThemeConfig.TEXT_SECONDARY,
                                italic=True,
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                icon_color=ThemeConfig.DANGER_COLOR,
                                tooltip="删除",
                                on_click=lambda e, qid=quote_id: self._delete_quote(e, qid),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=5,
            ),
            bgcolor=ThemeConfig.CARD_COLOR,
            padding=15,
            border_radius=10,
            border=ft.border.all(1, "#E0E0E0"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=3,
                color="#1A000000",
            ),
        )

    def _add_quote_dialog(self, e):
        """显示添加励志语录对话框"""
        page = e.page

        content_input = ft.TextField(
            label="励志诗句/名言",
            hint_text="例如：大鹏一日同风起，扶摇直上九万里",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )

        author_input = ft.TextField(
            label="作者",
            hint_text="例如：李白",
        )

        def close_dialog(e):
            dialog.open = False
            page.update()

        def save_quote(e):
            content = content_input.value.strip()
            author = author_input.value.strip()

            if not content:
                return

            # 添加到数据库
            success = self.db.add_quote(content, author)

            if success:
                close_dialog(e)
                # 刷新界面
                if self.refresh_callback:
                    self.refresh_callback()

        dialog = ft.AlertDialog(
            title=ft.Text("添加励志语录"),
            content=ft.Column(
                controls=[
                    content_input,
                    author_input,
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_quote),
            ],
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def _delete_quote(self, e, quote_id: int):
        """删除励志语录"""
        page = e.page

        def close_dialog(e):
            dialog.open = False
            page.update()

        def confirm_delete(e):
            success = self.db.delete_quote(quote_id)

            if success:
                close_dialog(e)
                # 刷新界面
                if self.refresh_callback:
                    self.refresh_callback()

        dialog = ft.AlertDialog(
            title=ft.Text("确认删除", color=ThemeConfig.DANGER_COLOR),
            content=ft.Text("确定要删除这条励志语录吗？"),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton(
                    "删除",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR)
                ),
            ],
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    @staticmethod
    def show_daily_quote(page: ft.Page, db_manager: DatabaseManager):
        """显示每日励志语录弹窗"""
        quote = db_manager.get_random_quote()

        if not quote:
            return

        quote_id, content, author, category = quote

        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Icon(ft.icons.WB_SUNNY, color="#FF9800", size=24),
                    ft.Text("今日励志", size=18, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                content,
                                size=16,
                                weight=ft.FontWeight.W_500,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            padding=ft.padding.symmetric(vertical=20, horizontal=10),
                        ),
                        ft.Text(
                            f"—— {author}",
                            size=14,
                            color=ThemeConfig.TEXT_SECONDARY,
                            italic=True,
                            text_align=ft.TextAlign.RIGHT,
                        ),
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=350,
            ),
            actions=[
                ft.TextButton(
                    "开始今日修炼",
                    on_click=close_dialog,
                    style=ft.ButtonStyle(
                        color=ThemeConfig.PRIMARY_COLOR,
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        page.dialog = dialog
        dialog.open = True
        page.update()
