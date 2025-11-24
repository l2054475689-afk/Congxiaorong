# systems/lingshi.py - 修正版（修改方法签名）
import flet as ft
from database.db_manager import DatabaseManager
from ui.styles import Styles
from config import ThemeConfig, GameConfig
from datetime import datetime, timedelta
from typing import List, Tuple

class LingshiSystem:
    """灵石系统 - 财务管理"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # 从数据库获取固定收支项
        fixed_items = self.db.get_fixed_items()
        self.fixed_income = fixed_items['income']
        self.fixed_expense = fixed_items['expense']
        self.fixed_items_raw = fixed_items['raw_items']  # 保存完整数据用于编辑
    
    # 修正：接受可选的刷新回调参数
    def create_lingshi_view(self, refresh_callback=None) -> ft.Column:
        """创建灵石视图"""
        # 保存回调供内部使用
        self.refresh_callback = refresh_callback
        
        user_data = self.db.get_user_data()
        initial_money = user_data.current_money if user_data else 0  # 初始余额
        current_money = self._calculate_actual_balance()  # 实际当前余额
        target_money = user_data.target_money if user_data else 5000000
        progress = (current_money / target_money) * 100 if target_money > 0 else 0
        
        # 获取本月收支统计
        monthly_stats = self._get_monthly_stats()
        
        # 获取负债和资产汇总
        debt_summary = self.db.get_debt_summary()
        asset_summary = self.db.get_asset_summary()
        
        # 获取最近交易记录
        recent_records = self.db.get_finance_records(limit=10)
        
        return ft.Column(
            controls=[
                # 标题栏
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("灵石系统", size=20, weight=ft.FontWeight.BOLD),
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        "设置初始余额",
                                        icon=ft.icons.ACCOUNT_BALANCE_WALLET,
                                        bgcolor=ThemeConfig.WARNING_COLOR,
                                        color="white",
                                        on_click=self._show_set_balance_dialog,
                                    ),
                                    ft.ElevatedButton(
                                        "记账",
                                        icon=ft.icons.ADD,
                                        bgcolor=ThemeConfig.PRIMARY_COLOR,
                                        color="white",
                                        on_click=self._show_add_record_dialog,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=20,
                ),
                
                # 当前灵石卡片
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text("当前灵石余额", size=14, color="white"),
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        icon_color="white",
                                        icon_size=16,
                                        tooltip="点击设置初始余额",
                                        on_click=self._show_set_balance_dialog,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=5,
                            ),
                            ft.Text(
                                f"¥{self._calculate_actual_balance():,.0f}",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color="white"
                            ),
                            ft.Text(f"(初始余额: ¥{initial_money:,.0f})", size=11, color="#FFFFFF80", italic=True),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(f"目标: {target_money/10000:.0f}万", size=12, color="white"),
                                        ft.Text(f"还需: ¥{max(0, target_money - current_money):,.0f}", size=11, color="white"),
                                        ft.ProgressBar(
                                            value=min(progress/100, 1.0),
                                            color="white",
                                            bgcolor="#FFFFFF30",
                                            height=6,
                                        ),
                                        ft.Text(f"进度: {progress:.1f}%", size=12, color="white"),
                                    ],
                                    spacing=3,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=30,
                    border_radius=20,
                    gradient=Styles.get_gradient(["#f6d365", "#fda085"]),
                    margin=ft.margin.symmetric(horizontal=20),
                ),
                
                # 本月统计卡片组
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self._create_stat_card("本月收入", f"+{monthly_stats['income']:,.0f}", ThemeConfig.SUCCESS_COLOR),
                            self._create_stat_card("本月支出", f"-{monthly_stats['expense']:,.0f}", ThemeConfig.DANGER_COLOR),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=ft.margin.symmetric(horizontal=20, vertical=10),
                ),
                
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self._create_stat_card("被动收入", f"+{monthly_stats['passive']:,.0f}", "#9370DB"),
                            self._create_stat_card("本月结余", 
                                                  f"{monthly_stats['income'] - monthly_stats['expense']:+,.0f}", 
                                                  "#4169E1"),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=ft.margin.symmetric(horizontal=20),
                ),
                
                # 负债和资产统计卡片组
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self._create_stat_card("总负债", f"-{debt_summary['total_debt']:,.0f}", ThemeConfig.DANGER_COLOR),
                            self._create_stat_card("总资产", f"+{asset_summary['total_value']:,.0f}", ThemeConfig.SUCCESS_COLOR),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=ft.margin.symmetric(horizontal=20, vertical=10),
                ),
                
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self._create_stat_card("月还款", f"-{debt_summary['monthly_payment']:,.0f}", "#FF6B6B"),
                            self._create_stat_card("月收入", f"+{asset_summary['monthly_income']:,.0f}", "#4ECDC4"),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=ft.margin.symmetric(horizontal=20),
                ),
                
                # 目标达成预测卡片组
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self._create_target_achievement_card(monthly_stats),
                            self._create_stat_card("月净收入", 
                                                  f"{monthly_stats['net_income']:+,.0f}", 
                                                  ThemeConfig.SUCCESS_COLOR if monthly_stats['net_income'] > 0 else ThemeConfig.DANGER_COLOR),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=ft.margin.symmetric(horizontal=20, vertical=10),
                ),
                
                # 固定收支配置
                ft.Container(
                    content=ft.ExpansionTile(
                        title=ft.Text("固定收支配置", size=16, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text("每月自动记录", size=12, color=ThemeConfig.TEXT_SECONDARY),
                        initially_expanded=False,
                        controls=[
                            self._create_fixed_items_list(),
                        ],
                    ),
                    margin=ft.margin.symmetric(horizontal=20, vertical=10),
                    bgcolor=ThemeConfig.CARD_COLOR,
                    border_radius=10,
                    padding=10,
                ),
                
                # 负债管理
                ft.Container(
                    content=ft.ExpansionTile(
                        title=ft.Text("负债管理", size=16, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(f"共{debt_summary['debt_count']}项负债，月还款¥{debt_summary['monthly_payment']:,.0f}", 
                                       size=12, color=ThemeConfig.TEXT_SECONDARY),
                        initially_expanded=False,
                        controls=[
                            self._create_debt_list(),
                        ],
                    ),
                    margin=ft.margin.symmetric(horizontal=20, vertical=10),
                    bgcolor=ThemeConfig.CARD_COLOR,
                    border_radius=10,
                    padding=10,
                ),
                
                # 资产管理
                ft.Container(
                    content=ft.ExpansionTile(
                        title=ft.Text("资产管理", size=16, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(f"共{asset_summary['asset_count']}项资产，月收入¥{asset_summary['monthly_income']:,.0f}", 
                                       size=12, color=ThemeConfig.TEXT_SECONDARY),
                        initially_expanded=False,
                        controls=[
                            self._create_asset_list(),
                        ],
                    ),
                    margin=ft.margin.symmetric(horizontal=20, vertical=10),
                    bgcolor=ThemeConfig.CARD_COLOR,
                    border_radius=10,
                    padding=10,
                ),
                
                # 最近交易记录
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text("【最近交易】", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=ft.Text(
                                            "基于设定余额计算",
                                            size=11,
                                            color=ThemeConfig.TEXT_SECONDARY,
                                            italic=True
                                        ),
                                        padding=ft.padding.only(left=10),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=1, color="#E0E0E0"),
                            *self._create_record_list(recent_records),
                        ],
                        spacing=10,
                    ),
                    padding=20,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _calculate_actual_balance(self) -> float:
        """计算基于初始余额和所有财务记录的实际当前余额"""
        user_data = self.db.get_user_data()
        initial_balance = user_data.current_money if user_data else 0
        
        # 获取所有财务记录
        all_records = self.db.get_finance_records(limit=999999)  # 获取所有记录
        
        total_change = 0
        for record in all_records:
            record_type, amount, category, description, created_at = record
            if record_type == "income":
                total_change += amount
            elif record_type == "expense":
                total_change -= amount
        
        return initial_balance + total_change
    
    def _get_monthly_stats(self) -> dict:
        """获取本月统计数据"""
        # 获取固定收支
        fixed_income_total = sum(self.fixed_income.values())
        fixed_expense_total = sum(self.fixed_expense.values())
        
        # 获取负债和资产数据
        debt_summary = self.db.get_debt_summary()
        asset_summary = self.db.get_asset_summary()
        
        # 计算总收入：固定收入 + 资产月收入
        total_income = fixed_income_total + asset_summary['monthly_income']
        
        # 计算总支出：固定支出 + 负债月还款
        total_expense = fixed_expense_total + debt_summary['monthly_payment']
        
        # 被动收入就是资产的月收入
        passive_income = asset_summary['monthly_income']
        
        # 计算月净收入
        monthly_net_income = total_income - total_expense
        
        # 计算达到目标需要的天数
        user_data = self.db.get_user_data()
        if user_data:
            current_money = self._calculate_actual_balance()  # 使用实际余额
            target_money = user_data.target_money
            remaining_amount = target_money - current_money
            
            if monthly_net_income > 0 and remaining_amount > 0:
                months_needed = remaining_amount / monthly_net_income
                days_needed = int(months_needed * 30)
                years_needed = months_needed / 12
            else:
                days_needed = -1  # 表示无法达到目标
                years_needed = -1
        else:
            days_needed = -1
            years_needed = -1
            remaining_amount = 0
        
        return {
            "income": total_income,
            "expense": total_expense,
            "passive": passive_income,
            "fixed_income": fixed_income_total,
            "fixed_expense": fixed_expense_total,
            "net_income": monthly_net_income,
            "days_to_target": days_needed,
            "years_to_target": years_needed,
            "remaining_amount": remaining_amount,
        }
    
    def _create_stat_card(self, title: str, value: str, color: str) -> ft.Container:
        """创建统计卡片"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=12, color=ThemeConfig.TEXT_SECONDARY),
                    ft.Text(
                        value,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=color
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ThemeConfig.CARD_COLOR,
            padding=15,
            border_radius=10,
            width=160,
            shadow=Styles.get_card_shadow(),
        )
    
    def _create_target_achievement_card(self, monthly_stats: dict) -> ft.Container:
        """创建目标达成预测卡片"""
        days_to_target = monthly_stats['days_to_target']
        years_to_target = monthly_stats['years_to_target']
        remaining_amount = monthly_stats['remaining_amount']
        net_income = monthly_stats['net_income']
        
        # 根据情况确定显示内容和颜色
        if remaining_amount <= 0:
            title = "目标状态"
            value = "已达成"
            color = ThemeConfig.SUCCESS_COLOR
            subtitle = "🎉 恭喜达成目标！"
        elif net_income <= 0:
            title = "目标预测"
            value = "无法达成"
            color = ThemeConfig.DANGER_COLOR
            subtitle = "月支出大于收入"
        elif days_to_target > 0:
            title = "达成预测"
            if years_to_target >= 1:
                value = f"{years_to_target:.1f}年"
                subtitle = f"约{days_to_target:,}天"
            else:
                months = days_to_target // 30
                days = days_to_target % 30
                if months > 0:
                    value = f"{months}个月"
                    subtitle = f"约{days_to_target:,}天"
                else:
                    value = f"{days_to_target}天"
                    subtitle = "即将达成！"
            color = "#4169E1"
        else:
            title = "目标预测"
            value = "计算中..."
            color = ThemeConfig.TEXT_SECONDARY
            subtitle = "数据加载中"
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=12, color=ThemeConfig.TEXT_SECONDARY),
                    ft.Text(
                        value,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=color
                    ),
                    ft.Text(
                        subtitle,
                        size=10,
                        color=ThemeConfig.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER
                    ) if subtitle else ft.Container(),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=ThemeConfig.CARD_COLOR,
            padding=15,
            border_radius=10,
            width=160,
            shadow=Styles.get_card_shadow(),
        )
    
    def _create_fixed_items_list(self) -> ft.Column:
        """创建固定收支项目列表"""
        items = []
        
        # 固定收入项
        items.append(ft.Text("固定收入", size=14, weight=ft.FontWeight.BOLD, color=ThemeConfig.SUCCESS_COLOR))
        for name, amount in self.fixed_income.items():
            # 找到对应的数据库记录ID
            item_id = None
            for raw_item in self.fixed_items_raw:
                if raw_item[1] == name and raw_item[2] == 'income':  # name和type匹配
                    item_id = raw_item[0]  # id字段
                    break
            
            items.append(
                ft.Row(
                    controls=[
                        ft.Text(name, size=14),
                        ft.Text(f"+¥{amount:,.0f}", size=14, color=ThemeConfig.SUCCESS_COLOR),
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            icon_size=16,
                            on_click=lambda e, n=name, a=amount, i=item_id: self._edit_fixed_item(e, "income", n, a, i),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
        
        items.append(ft.Divider(height=20))
        
        # 固定支出项
        items.append(ft.Text("固定支出", size=14, weight=ft.FontWeight.BOLD, color=ThemeConfig.DANGER_COLOR))
        for name, amount in self.fixed_expense.items():
            # 找到对应的数据库记录ID
            item_id = None
            for raw_item in self.fixed_items_raw:
                if raw_item[1] == name and raw_item[2] == 'expense':  # name和type匹配
                    item_id = raw_item[0]  # id字段
                    break
                    
            items.append(
                ft.Row(
                    controls=[
                        ft.Text(name, size=14),
                        ft.Text(f"-¥{amount:,.0f}", size=14, color=ThemeConfig.DANGER_COLOR),
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            icon_size=16,
                            on_click=lambda e, n=name, a=amount, i=item_id: self._edit_fixed_item(e, "expense", n, a, i),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
        
        # 添加按钮
        items.append(
            ft.Row(
                controls=[
                    ft.TextButton(
                        "添加固定收入",
                        icon=ft.icons.ADD,
                        on_click=lambda e: self._add_fixed_item(e, "income"),
                    ),
                    ft.TextButton(
                        "添加固定支出",
                        icon=ft.icons.ADD,
                        on_click=lambda e: self._add_fixed_item(e, "expense"),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
            )
        )
        
        return ft.Column(controls=items, spacing=8)
    
    def _create_record_list(self, records: list) -> List[ft.Container]:
        """创建交易记录列表"""
        if not records:
            return [ft.Text("暂无交易记录", size=14, color=ThemeConfig.TEXT_SECONDARY)]
        
        record_items = []
        for record in records:
            record_type, amount, category, description, created_at = record
            
            # 解析时间
            if isinstance(created_at, str):
                record_time = datetime.fromisoformat(created_at)
                time_str = record_time.strftime("%m-%d %H:%M")
            else:
                time_str = "未知时间"
            
            # 确定颜色和符号
            if record_type == "income":
                color = ThemeConfig.SUCCESS_COLOR
                sign = "+"
            else:
                color = ThemeConfig.DANGER_COLOR
                sign = "-"
            
            # 构建显示文本：优先显示分类，备注作为副标题
            display_title = category or "未分类"
            display_controls = [
                ft.Text(display_title, size=14, weight=ft.FontWeight.W_500),
            ]

            # 如果有备注，添加到下方
            if description:
                display_controls.append(
                    ft.Text(description, size=12, color=ThemeConfig.TEXT_SECONDARY)
                )

            # 添加时间
            display_controls.append(
                ft.Text(time_str, size=11, color=ThemeConfig.TEXT_SECONDARY, italic=True)
            )

            record_items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=display_controls,
                                spacing=2,
                                expand=True,
                            ),
                            ft.Text(
                                f"{sign}¥{amount:,.0f}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=color,
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_color=ThemeConfig.DANGER_COLOR,
                                icon_size=16,
                                on_click=lambda e, rec=record: self._delete_record(e, rec),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor=ThemeConfig.CARD_COLOR,
                    padding=10,
                    border_radius=8,
                )
            )
        
        return record_items
    
    def _show_add_record_dialog(self, e):
        """显示添加记录对话框"""
        page = e.page

        # 货币选择下拉框
        currency_dropdown = ft.Dropdown(
            label="货币类型",
            width=300,
            options=[
                ft.dropdown.Option("CNY", "人民币 (¥)"),
                ft.dropdown.Option("USD", "美元 ($)"),
            ],
            value="CNY",
        )

        # 金额输入框 - 前缀会根据货币类型动态更新
        amount_field = ft.TextField(
            label="金额",
            prefix_text="¥",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )

        # 汇率提示文本
        rate_hint = ft.Text(
            f"当前汇率: 1 USD = {GameConfig.USD_TO_CNY_RATE} CNY",
            size=12,
            color=ThemeConfig.TEXT_SECONDARY,
            visible=False,
        )

        # 换算预览文本
        conversion_preview = ft.Text(
            "",
            size=12,
            color=ThemeConfig.INFO_COLOR,
            visible=False,
        )

        def on_currency_change(e):
            """货币类型变化时更新UI"""
            if currency_dropdown.value == "USD":
                amount_field.prefix_text = "$"
                rate_hint.visible = True
                update_conversion_preview(None)
            else:
                amount_field.prefix_text = "¥"
                rate_hint.visible = False
                conversion_preview.visible = False
            page.update()

        def update_conversion_preview(e):
            """更新换算预览"""
            if currency_dropdown.value == "USD" and amount_field.value:
                try:
                    usd_amount = float(amount_field.value)
                    cny_amount = usd_amount * GameConfig.USD_TO_CNY_RATE
                    conversion_preview.value = f"≈ ¥{cny_amount:,.2f} 人民币"
                    conversion_preview.visible = True
                except ValueError:
                    conversion_preview.visible = False
            else:
                conversion_preview.visible = False
            page.update()

        currency_dropdown.on_change = on_currency_change
        amount_field.on_change = update_conversion_preview

        type_dropdown = ft.Dropdown(
            label="类型",
            width=300,
            options=[
                ft.dropdown.Option("income", "收入"),
                ft.dropdown.Option("expense", "支出"),
            ],
            value="expense",
        )

        category_dropdown = ft.Dropdown(
            label="分类",
            width=300,
            options=[
                ft.dropdown.Option("餐饮", "餐饮"),
                ft.dropdown.Option("交通", "交通"),
                ft.dropdown.Option("购物", "购物"),
                ft.dropdown.Option("娱乐", "娱乐"),
                ft.dropdown.Option("医疗", "医疗"),
                ft.dropdown.Option("教育", "教育"),
                ft.dropdown.Option("工资", "工资"),
                ft.dropdown.Option("投资", "投资"),
                ft.dropdown.Option("房租", "房租"),
                ft.dropdown.Option("水电费", "水电费"),
                ft.dropdown.Option("自定义", "自定义"),
                ft.dropdown.Option("其他", "其他"),
            ],
            value="其他",
        )

        custom_category_field = ft.TextField(
            label="自定义分类（选择自定义或其他时填写）",
            width=300,
            hint_text="请输入自定义分类名称",
        )

        description_field = ft.TextField(
            label="备注（可选）",
            multiline=True,
            width=300,
            max_lines=3,
        )

        def close_dialog(e):
            dialog.open = False
            page.update()

        def save_record(e):
            if amount_field.value:
                try:
                    amount = float(amount_field.value)

                    # 如果是美元，自动转换为人民币
                    original_amount = amount
                    original_currency = currency_dropdown.value
                    if currency_dropdown.value == "USD":
                        amount = amount * GameConfig.USD_TO_CNY_RATE

                    # 处理自定义分类
                    final_category = category_dropdown.value
                    if (category_dropdown.value == "自定义" or category_dropdown.value == "其他") and custom_category_field.value:
                        final_category = custom_category_field.value

                    # 在备注中添加原始货币信息（如果是美元）
                    final_description = description_field.value or ""
                    if original_currency == "USD":
                        currency_note = f"[原始: ${original_amount:,.2f} USD]"
                        if final_description:
                            final_description = f"{final_description} {currency_note}"
                        else:
                            final_description = currency_note

                    self.db.add_finance_record(
                        record_type=type_dropdown.value,
                        amount=amount,
                        category=final_category,
                        description=final_description or None,
                    )

                    # 显示记账成功信息
                    sign = "+" if type_dropdown.value == "income" else "-"
                    if original_currency == "USD":
                        print(f"记账成功：{sign}${original_amount:,.2f} USD → ¥{amount:,.2f} CNY ({final_category})")
                    else:
                        print(f"记账成功：{sign}¥{amount:,.0f} ({final_category})")

                    close_dialog(e)
                    # 刷新页面
                    if self.refresh_callback:
                        self.refresh_callback()
                except ValueError:
                    pass

        dialog = ft.AlertDialog(
            title=ft.Text("记一笔"),
            content=ft.Column(
                controls=[
                    currency_dropdown,
                    amount_field,
                    rate_hint,
                    conversion_preview,
                    type_dropdown,
                    category_dropdown,
                    custom_category_field,
                    description_field,
                ],
                height=400,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_record),
            ],
        )

        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _add_fixed_item(self, e, item_type: str):
        """添加固定收支项"""
        page = e.page
        
        name_field = ft.TextField(label="项目名称", width=300)
        amount_field = ft.TextField(
            label="金额",
            prefix_text="¥",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_item(e):
            if name_field.value and amount_field.value:
                try:
                    amount = float(amount_field.value)
                    
                    # 保存到数据库
                    success = self.db.add_fixed_item(
                        name=name_field.value,
                        item_type=item_type,
                        amount=amount,
                        description=None
                    )
                    
                    if success:
                        # 更新本地数据
                        if item_type == "income":
                            self.fixed_income[name_field.value] = amount
                        else:
                            self.fixed_expense[name_field.value] = amount
                        
                        print(f"添加固定{'收入' if item_type == 'income' else '支出'}成功: {name_field.value} ¥{amount:,.0f}")
                    else:
                        print("保存到数据库失败")
                    
                    close_dialog(e)
                    if self.refresh_callback:
                        self.refresh_callback()
                except ValueError:
                    print("请输入有效的数字")
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"添加固定{'收入' if item_type == 'income' else '支出'}"),
            content=ft.Column(
                controls=[
                    name_field,
                    amount_field,
                ],
                height=120,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_item),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
        
    def _edit_fixed_item(self, e, item_type: str, name: str, amount: float, item_id: int = None):
        """编辑固定收支项"""
        page = e.page
        
        name_field = ft.TextField(label="项目名称", value=name, width=300)
        amount_field = ft.TextField(
            label="金额",
            value=str(amount),
            prefix_text="¥",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_changes(e):
            if name_field.value and amount_field.value:
                try:
                    new_amount = float(amount_field.value)
                    
                    if item_id:
                        # 如果有ID，直接更新数据库记录
                        success = self.db.update_fixed_item(
                            item_id=item_id,
                            name=name_field.value,
                            amount=new_amount,
                            description=None
                        )
                        
                        if success:
                            # 更新本地数据
                            if item_type == "income":
                                if name != name_field.value and name in self.fixed_income:
                                    del self.fixed_income[name]
                                self.fixed_income[name_field.value] = new_amount
                            else:
                                if name != name_field.value and name in self.fixed_expense:
                                    del self.fixed_expense[name]
                                self.fixed_expense[name_field.value] = new_amount
                            
                            print(f"更新固定{'收入' if item_type == 'income' else '支出'}成功: {name_field.value}")
                        else:
                            print("更新数据库失败")
                    
                    close_dialog(e)
                    # 刷新页面
                    if self.refresh_callback:
                        self.refresh_callback()
                except ValueError:
                    print("请输入有效的数字")
        
        def delete_item(e):
            if item_id:
                # 使用ID直接删除数据库记录
                success = self.db.delete_fixed_item(item_id)
                
                if success:
                    # 从本地数据中删除
                    if item_type == "income" and name in self.fixed_income:
                        del self.fixed_income[name]
                    elif item_type == "expense" and name in self.fixed_expense:
                        del self.fixed_expense[name]
                    
                    print(f"删除固定{'收入' if item_type == 'income' else '支出'}成功: {name}")
                else:
                    print("删除数据库记录失败")
            
            close_dialog(e)
            if self.refresh_callback:
                self.refresh_callback()
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"编辑固定{'收入' if item_type == 'income' else '支出'}"),
            content=ft.Column(
                controls=[
                    name_field,
                    amount_field,
                ],
                height=120,
            ),
            actions=[
                ft.TextButton("删除", on_click=delete_item,
                            style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR)),
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_changes),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _delete_record(self, e, record):
        """删除交易记录"""
        page = e.page
        record_type, amount, category, description, created_at = record
        
        def confirm_delete(e):
            try:
                # 调用数据库删除方法
                # 根据交易的创建时间和金额来删除记录（因为没有直接的ID）
                success = self.db.delete_finance_record_by_details(
                    record_type=record_type,
                    amount=amount, 
                    category=category,
                    description=description,
                    created_at=created_at
                )
                
                if success:
                    print(f"成功删除交易记录: {description or category} ¥{amount:,.0f}")
                else:
                    print(f"删除失败：未找到匹配的交易记录")
                
                # 关闭对话框
                dialog.open = False
                page.update()
                
                # 强制刷新页面
                if self.refresh_callback:
                    self.refresh_callback()
                else:
                    # 如果没有回调，尝试直接更新页面
                    page.update()
                    
            except Exception as ex:
                print(f"删除记录失败: {ex}")
        
        def cancel_delete(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("确认删除", color=ThemeConfig.DANGER_COLOR),
            content=ft.Text(f"确定要删除这条交易记录吗？\n{description or category} ¥{amount:,.0f}"),
            actions=[
                ft.TextButton("取消", on_click=cancel_delete),
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
    
    def _show_set_balance_dialog(self, e):
        """显示设置余额对话框"""
        page = e.page
        user_data = self.db.get_user_data()
        current_balance = user_data.current_money if user_data else 0
        
        # 创建输入控件
        balance_field = ft.TextField(
            label="初始余额",
            prefix_text="¥",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            value=str(current_balance),
            autofocus=True,
            hint_text="请输入初始灵石余额"
        )
        
        target_field = ft.TextField(
            label="目标金额",
            prefix_text="¥",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            value=str(user_data.target_money if user_data else 5000000),
            hint_text="请输入目标金额（默认500万）"
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_balance(e):
            if balance_field.value:
                try:
                    new_balance = float(balance_field.value)
                    target_money = float(target_field.value) if target_field.value else 5000000
                    
                    # 更新数据库中的余额和目标金额
                    self.db.set_money(new_balance)
                    self.db.set_target_money(target_money)
                    
                    print(f"已设置初始灵石余额：¥{new_balance:,.0f}")
                    print(f"已设置目标金额：¥{target_money:,.0f}")
                    
                    close_dialog(e)
                    # 刷新页面
                    if self.refresh_callback:
                        self.refresh_callback()
                except ValueError:
                    print("请输入有效的数字")
        
        dialog = ft.AlertDialog(
            title=ft.Text("设置初始灵石余额"),
            content=ft.Column(
                controls=[
                    ft.Text("设置初始灵石余额和目标金额", size=14, color=ThemeConfig.TEXT_SECONDARY),
                    balance_field,
                    target_field,
                    ft.Divider(),
                    ft.Text(
                        "提示：这是初始余额，实际余额 = 初始余额 + 所有收支记录", 
                        size=12, 
                        color=ThemeConfig.TEXT_SECONDARY,
                        italic=True
                    ),
                ],
                height=250,
                spacing=15,
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton(
                    "确认设置", 
                    on_click=save_balance,
                    style=ft.ButtonStyle(color=ThemeConfig.WARNING_COLOR)
                ),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _create_debt_list(self) -> ft.Column:
        """创建负债列表"""
        debts = self.db.get_debts()
        items = []
        
        if not debts:
            items.append(ft.Text("暂无负债记录", size=14, color=ThemeConfig.TEXT_SECONDARY))
        else:
            for debt in debts:
                debt_id, name, monthly_payment, remaining_months, total_amount, description, created_at = debt
                items.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(name, size=14, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"总额: ¥{total_amount:,.0f}", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                        ft.Text(description or "无描述", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(f"¥{monthly_payment:,.0f}/月", size=14, weight=ft.FontWeight.BOLD, color=ThemeConfig.DANGER_COLOR),
                                        ft.Text(f"还需{remaining_months}个月", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    spacing=2,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            icon_size=16,
                                            tooltip="编辑",
                                            on_click=lambda e, d=debt: self._edit_debt(e, d),
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            icon_color=ThemeConfig.DANGER_COLOR,
                                            icon_size=16,
                                            tooltip="删除",
                                            on_click=lambda e, d=debt: self._delete_debt(e, d),
                                        ),
                                    ],
                                    spacing=5,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor="#FFF1F1",
                        padding=10,
                        border_radius=8,
                        margin=ft.margin.symmetric(vertical=2),
                    )
                )
        
        # 添加按钮
        items.append(
            ft.Container(
                content=ft.ElevatedButton(
                    "添加负债",
                    icon=ft.icons.ADD,
                    bgcolor=ThemeConfig.DANGER_COLOR,
                    color="white",
                    on_click=self._show_add_debt_dialog,
                ),
                margin=ft.margin.only(top=10),
                alignment=ft.alignment.center,
            )
        )
        
        return ft.Column(controls=items, spacing=8)
    
    def _create_asset_list(self) -> ft.Column:
        """创建资产列表"""
        assets = self.db.get_assets()
        items = []
        
        if not assets:
            items.append(ft.Text("暂无资产记录", size=14, color=ThemeConfig.TEXT_SECONDARY))
        else:
            for asset in assets:
                asset_id, name, monthly_income, duration_months, total_value, description, created_at = asset
                items.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(name, size=14, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"总价值: ¥{total_value:,.0f}", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                        ft.Text(description or "无描述", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(f"¥{monthly_income:,.0f}/月", size=14, weight=ft.FontWeight.BOLD, color=ThemeConfig.SUCCESS_COLOR),
                                        ft.Text(f"持续{duration_months}个月", size=12, color=ThemeConfig.TEXT_SECONDARY),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    spacing=2,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            icon_size=16,
                                            tooltip="编辑",
                                            on_click=lambda e, a=asset: self._edit_asset(e, a),
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            icon_color=ThemeConfig.DANGER_COLOR,
                                            icon_size=16,
                                            tooltip="删除",
                                            on_click=lambda e, a=asset: self._delete_asset(e, a),
                                        ),
                                    ],
                                    spacing=5,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor="#F1FFF1",
                        padding=10,
                        border_radius=8,
                        margin=ft.margin.symmetric(vertical=2),
                    )
                )
        
        # 添加按钮
        items.append(
            ft.Container(
                content=ft.ElevatedButton(
                    "添加资产",
                    icon=ft.icons.ADD,
                    bgcolor=ThemeConfig.SUCCESS_COLOR,
                    color="white",
                    on_click=self._show_add_asset_dialog,
                ),
                margin=ft.margin.only(top=10),
                alignment=ft.alignment.center,
            )
        )
        
        return ft.Column(controls=items, spacing=8)
    
    def _show_add_debt_dialog(self, e):
        """显示添加负债对话框"""
        page = e.page
        
        name_field = ft.TextField(label="负债名称", width=300, hint_text="如：房贷、车贷、信用卡等")
        monthly_payment_field = ft.TextField(
            label="月还款额",
            prefix_text="¥",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            hint_text="每月需要还款的金额"
        )
        remaining_months_field = ft.TextField(
            label="剩余月数",
            suffix_text="个月",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            hint_text="还需要还几个月"
        )
        description_field = ft.TextField(
            label="描述（可选）",
            multiline=True,
            width=300,
            max_lines=2,
            hint_text="负债的详细说明"
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_debt(e):
            if name_field.value and monthly_payment_field.value and remaining_months_field.value:
                try:
                    monthly_payment = float(monthly_payment_field.value)
                    remaining_months = int(remaining_months_field.value)
                    
                    success = self.db.add_debt(
                        name=name_field.value,
                        monthly_payment=monthly_payment,
                        remaining_months=remaining_months,
                        description=description_field.value or None
                    )
                    
                    if success:
                        print(f"添加负债成功：{name_field.value}，月还款¥{monthly_payment:,.0f}，剩余{remaining_months}个月")
                    
                    close_dialog(e)
                    if self.refresh_callback:
                        self.refresh_callback()
                except ValueError:
                    print("请输入有效的数字")
        
        dialog = ft.AlertDialog(
            title=ft.Text("添加负债"),
            content=ft.Column(
                controls=[
                    name_field,
                    monthly_payment_field,
                    remaining_months_field,
                    description_field,
                ],
                height=280,
                spacing=15,
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton(
                    "保存", 
                    on_click=save_debt,
                    style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR)
                ),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _show_add_asset_dialog(self, e):
        """显示添加资产对话框"""
        page = e.page
        
        name_field = ft.TextField(label="资产名称", width=300, hint_text="如：定期存款、股票、基金等")
        monthly_income_field = ft.TextField(
            label="月收入额",
            prefix_text="¥",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            hint_text="每月产生的收入金额"
        )
        duration_months_field = ft.TextField(
            label="持续月数",
            suffix_text="个月",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            hint_text="预计能持续产生收入的月数"
        )
        description_field = ft.TextField(
            label="描述（可选）",
            multiline=True,
            width=300,
            max_lines=2,
            hint_text="资产的详细说明"
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_asset(e):
            if name_field.value and monthly_income_field.value and duration_months_field.value:
                try:
                    monthly_income = float(monthly_income_field.value)
                    duration_months = int(duration_months_field.value)
                    
                    success = self.db.add_asset(
                        name=name_field.value,
                        monthly_income=monthly_income,
                        duration_months=duration_months,
                        description=description_field.value or None
                    )
                    
                    if success:
                        print(f"添加资产成功：{name_field.value}，月收入¥{monthly_income:,.0f}，持续{duration_months}个月")
                    
                    close_dialog(e)
                    if self.refresh_callback:
                        self.refresh_callback()
                except ValueError:
                    print("请输入有效的数字")
        
        dialog = ft.AlertDialog(
            title=ft.Text("添加资产"),
            content=ft.Column(
                controls=[
                    name_field,
                    monthly_income_field,
                    duration_months_field,
                    description_field,
                ],
                height=280,
                spacing=15,
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton(
                    "保存", 
                    on_click=save_asset,
                    style=ft.ButtonStyle(color=ThemeConfig.SUCCESS_COLOR)
                ),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _edit_debt(self, e, debt):
        """编辑负债"""
        page = e.page
        debt_id, name, monthly_payment, remaining_months, total_amount, description, created_at = debt
        
        name_field = ft.TextField(label="负债名称", value=name, width=300)
        monthly_payment_field = ft.TextField(
            label="月还款额",
            prefix_text="¥",
            value=str(monthly_payment),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )
        remaining_months_field = ft.TextField(
            label="剩余月数",
            suffix_text="个月",
            value=str(remaining_months),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )
        description_field = ft.TextField(
            label="描述（可选）",
            value=description or "",
            multiline=True,
            width=300,
            max_lines=2,
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_changes(e):
            if name_field.value and monthly_payment_field.value and remaining_months_field.value:
                try:
                    new_monthly_payment = float(monthly_payment_field.value)
                    new_remaining_months = int(remaining_months_field.value)
                    
                    success = self.db.update_debt(
                        debt_id=debt_id,
                        name=name_field.value,
                        monthly_payment=new_monthly_payment,
                        remaining_months=new_remaining_months,
                        description=description_field.value or None
                    )
                    
                    if success:
                        print(f"更新负债成功：{name_field.value}")
                    
                    close_dialog(e)
                    if self.refresh_callback:
                        self.refresh_callback()
                except ValueError:
                    print("请输入有效的数字")
        
        dialog = ft.AlertDialog(
            title=ft.Text("编辑负债"),
            content=ft.Column(
                controls=[
                    name_field,
                    monthly_payment_field,
                    remaining_months_field,
                    description_field,
                ],
                height=280,
                spacing=15,
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_changes),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _edit_asset(self, e, asset):
        """编辑资产"""
        page = e.page
        asset_id, name, monthly_income, duration_months, total_value, description, created_at = asset
        
        name_field = ft.TextField(label="资产名称", value=name, width=300)
        monthly_income_field = ft.TextField(
            label="月收入额",
            prefix_text="¥",
            value=str(monthly_income),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )
        duration_months_field = ft.TextField(
            label="持续月数",
            suffix_text="个月",
            value=str(duration_months),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
        )
        description_field = ft.TextField(
            label="描述（可选）",
            value=description or "",
            multiline=True,
            width=300,
            max_lines=2,
        )
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_changes(e):
            if name_field.value and monthly_income_field.value and duration_months_field.value:
                try:
                    new_monthly_income = float(monthly_income_field.value)
                    new_duration_months = int(duration_months_field.value)
                    
                    success = self.db.update_asset(
                        asset_id=asset_id,
                        name=name_field.value,
                        monthly_income=new_monthly_income,
                        duration_months=new_duration_months,
                        description=description_field.value or None
                    )
                    
                    if success:
                        print(f"更新资产成功：{name_field.value}")
                    
                    close_dialog(e)
                    if self.refresh_callback:
                        self.refresh_callback()
                except ValueError:
                    print("请输入有效的数字")
        
        dialog = ft.AlertDialog(
            title=ft.Text("编辑资产"),
            content=ft.Column(
                controls=[
                    name_field,
                    monthly_income_field,
                    duration_months_field,
                    description_field,
                ],
                height=280,
                spacing=15,
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_changes),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def _delete_debt(self, e, debt):
        """删除负债"""
        page = e.page
        debt_id, name, monthly_payment, remaining_months, total_amount, description, created_at = debt
        
        def confirm_delete(e):
            success = self.db.delete_debt(debt_id)
            if success:
                print(f"删除负债成功：{name}")
            
            dialog.open = False
            page.update()
            
            if self.refresh_callback:
                self.refresh_callback()
        
        def cancel_delete(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("确认删除", color=ThemeConfig.DANGER_COLOR),
            content=ft.Text(f"确定要删除负债「{name}」吗？\n月还款：¥{monthly_payment:,.0f}，剩余{remaining_months}个月"),
            actions=[
                ft.TextButton("取消", on_click=cancel_delete),
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
    
    def _delete_asset(self, e, asset):
        """删除资产"""
        page = e.page
        asset_id, name, monthly_income, duration_months, total_value, description, created_at = asset
        
        def confirm_delete(e):
            success = self.db.delete_asset(asset_id)
            if success:
                print(f"删除资产成功：{name}")
            
            dialog.open = False
            page.update()
            
            if self.refresh_callback:
                self.refresh_callback()
        
        def cancel_delete(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("确认删除", color=ThemeConfig.DANGER_COLOR),
            content=ft.Text(f"确定要删除资产「{name}」吗？\n月收入：¥{monthly_income:,.0f}，持续{duration_months}个月"),
            actions=[
                ft.TextButton("取消", on_click=cancel_delete),
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