import flet as ft
from database.db_manager import DatabaseManager
from database.models import Task
from ui.styles import Styles
from ui.task_widgets import TaskWidget
from config import ThemeConfig

class PanelSystem:
    """个人面板系统"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_panel_view(self) -> ft.Column:
        """创建面板视图"""
        user_data = self.db.get_user_data()
        tasks = self.db.get_tasks()
        
        # 统计数据
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.completed_today)
        # 只获取已完成的任务
        completed_task_list = [t for t in tasks if t.completed_today]
        
        # 获取心境等级
        spirit_level, spirit_color = Styles.get_spirit_level_info(user_data.current_spirit)
        
        # 获取真实的境界信息
        from systems.jingjie import JingjieSystem
        jingjie_system = JingjieSystem(self.db)
        current_realm = jingjie_system.get_highest_realm()
        
        # 计算目标达成时间预测
        target_stats = self._calculate_target_achievement(user_data)
        
        # 获取今日真实收支数据
        daily_stats = self._get_daily_stats()
        
        return ft.Column(
            controls=[
                # 标题
                ft.Container(
                    content=ft.Text("个人面板", size=20, weight=ft.FontWeight.BOLD),
                    padding=20,
                ),
                
                # 生命倒计时卡片（改为血量显示）
                self._create_life_card(user_data.current_blood),
                
                # 状态卡片组
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self._create_status_card(
                                f"心境: {user_data.current_spirit}", 
                                spirit_level,
                                spirit_color
                            ),
                            self._create_status_card(
                                "境界", 
                                current_realm,
                                ThemeConfig.PRIMARY_COLOR
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=ft.margin.symmetric(horizontal=20, vertical=10),
                ),
                
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self._create_status_card(
                                "任务", 
                                f"{completed_tasks}/{total_tasks}",
                                ThemeConfig.SUCCESS_COLOR
                            ),
                            self._create_status_card(
                                "灵石", 
                                f"{user_data.current_money/10000:.1f}万",
                                "#f6d365"
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=ft.margin.symmetric(horizontal=20),
                ),
                
                # 目标预测和净收入卡片
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self._create_target_card(target_stats),
                            self._create_status_card(
                                "月净收入", 
                                f"{target_stats['net_income']:+,.0f}",
                                ThemeConfig.SUCCESS_COLOR if target_stats['net_income'] > 0 else ThemeConfig.DANGER_COLOR
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=ft.margin.symmetric(horizontal=20, vertical=10),
                ),
                
                # 今日收支卡片
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self._create_status_card(
                                "今日收入", 
                                f"+¥{daily_stats['income']}",
                                ThemeConfig.SUCCESS_COLOR
                            ),
                            self._create_status_card(
                                "今日支出", 
                                f"-¥{daily_stats['expense']}",
                                ThemeConfig.DANGER_COLOR
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    margin=ft.margin.symmetric(horizontal=20, vertical=10),
                ),
                
                # 今日修炼标题
                ft.Container(
                    content=ft.Text("今日已完成修炼", size=18, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.only(left=20, top=20, bottom=10),
                ),
                
                # 任务列表 - 只显示已完成的任务
                ft.Container(
                    content=ft.Column(
                        controls=[
                            TaskWidget.create_task_item(task, lambda t, v: None, None, False) 
                            for task in completed_task_list[:10]  # 显示最多10个已完成的任务
                        ] if completed_task_list else [
                            ft.Text("今日还没有完成任何修炼任务", 
                                   size=14, 
                                   color=ThemeConfig.TEXT_SECONDARY,
                                   text_align=ft.TextAlign.CENTER)
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.symmetric(horizontal=20),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _create_life_card(self, blood: int) -> ft.Container:
        """创建生命卡片（显示血量）"""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("剩余血量", size=14, color="white"),  # 改为血量
                    ft.Text(
                        f"{blood:,}",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color="white"
                    ),
                    ft.Text("点", size=14, color="white"),  # 单位改为"点"
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=30,
            border_radius=20,
            gradient=Styles.get_gradient(ThemeConfig.LIFE_GRADIENT),
            margin=ft.margin.symmetric(horizontal=20),
        )
    
    def _create_status_card(self, title: str, value: str, color: str) -> ft.Container:
        """创建状态卡片"""
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
            width=150,
            shadow=Styles.get_card_shadow(),
        )
    
    def _calculate_target_achievement(self, user_data) -> dict:
        """计算目标达成时间预测"""
        try:
            # 获取固定收支项
            fixed_items = self.db.get_fixed_items()
            fixed_income_total = sum(fixed_items['income'].values())
            fixed_expense_total = sum(fixed_items['expense'].values())
            
            # 获取负债和资产数据
            debt_summary = self.db.get_debt_summary()
            asset_summary = self.db.get_asset_summary()
            
            # 计算总收入：固定收入 + 资产月收入
            total_income = fixed_income_total + asset_summary['monthly_income']
            
            # 计算总支出：固定支出 + 负债月还款
            total_expense = fixed_expense_total + debt_summary['monthly_payment']
            
            # 计算月净收入
            monthly_net_income = total_income - total_expense
            
            # 计算达到目标需要的时间
            current_money = user_data.current_money
            target_money = user_data.target_money
            remaining_amount = target_money - current_money
            
            if monthly_net_income > 0 and remaining_amount > 0:
                months_needed = remaining_amount / monthly_net_income
                days_needed = int(months_needed * 30)
                years_needed = months_needed / 12
                
                return {
                    'net_income': monthly_net_income,
                    'days_to_target': days_needed,
                    'years_to_target': years_needed,
                    'remaining_amount': remaining_amount,
                    'can_achieve': True
                }
            else:
                return {
                    'net_income': monthly_net_income,
                    'days_to_target': -1,
                    'years_to_target': -1,
                    'remaining_amount': remaining_amount,
                    'can_achieve': False
                }
                
        except Exception as e:
            print(f"计算目标达成时间错误: {e}")
            return {
                'net_income': 0,
                'days_to_target': -1,
                'years_to_target': -1,
                'remaining_amount': 0,
                'can_achieve': False
            }
    
    def _create_target_card(self, target_stats: dict) -> ft.Container:
        """创建目标达成时间卡片"""
        days_to_target = target_stats['days_to_target']
        years_to_target = target_stats['years_to_target']
        remaining_amount = target_stats['remaining_amount']
        net_income = target_stats['net_income']
        can_achieve = target_stats['can_achieve']
        
        # 根据情况确定显示内容和颜色
        if remaining_amount <= 0:
            title = "目标状态"
            value = "已达成"
            color = ThemeConfig.SUCCESS_COLOR
        elif not can_achieve or net_income <= 0:
            title = "目标预测"
            value = "无法达成"
            color = ThemeConfig.DANGER_COLOR
        elif days_to_target > 0:
            title = "达成预测"
            if years_to_target >= 1:
                value = f"{years_to_target:.1f}年"
            else:
                months = days_to_target // 30
                if months > 0:
                    value = f"{months}个月"
                else:
                    value = f"{days_to_target}天"
            color = "#4169E1"
        else:
            title = "目标预测"
            value = "计算中..."
            color = ThemeConfig.TEXT_SECONDARY
        
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
            width=150,
            shadow=Styles.get_card_shadow(),
        )

    def _get_daily_stats(self) -> dict:
        """获取今日真实收支数据"""
        try:
            from datetime import date
            today = date.today().isoformat()
            
            # 获取今日所有财务记录
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # 获取今日收入总额
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM finance_records 
                WHERE type = 'income' AND DATE(created_at) = ?
            ''', (today,))
            daily_income = cursor.fetchone()[0]
            
            # 获取今日支出总额
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM finance_records 
                WHERE type = 'expense' AND DATE(created_at) = ?
            ''', (today,))
            daily_expense = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'income': float(daily_income),
                'expense': float(daily_expense)
            }
            
        except Exception as e:
            print(f"获取今日收支数据错误: {e}")
            return {
                'income': 0.0,
                'expense': 0.0
            }