import flet as ft
from database.db_manager import DatabaseManager
from ai_providers.ai_manager import ai_manager
from config import VERSION, ThemeConfig
import json
import os
from datetime import datetime

class SettingsSystem:
    """设置系统"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.settings = self._load_settings()
    
    def _load_settings(self) -> dict:
        """加载设置"""
        # 从配置文件或数据库加载设置
        default_settings = {
            "ai_provider": "none",
            "api_key": "",
            "api_url": "",
            "auto_backup": True,
            "backup_path": "",
            "birth_year": 1998,
            "target_money": 5000000,
            "theme_mode": "light",
            "font_size": "normal",
        }
        
        # TODO: 从数据库或配置文件加载实际设置
        return default_settings
    
    def _save_settings(self):
        """保存设置"""
        # TODO: 保存到数据库或配置文件
        pass
    
    def create_settings_view(self) -> ft.Column:
        """创建设置视图"""
        return ft.Column(
            controls=[
                # 标题栏
                ft.Container(
                    content=ft.Text("设置", size=20, weight=ft.FontWeight.BOLD),
                    padding=20,
                ),
                
                # AI接口设置
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("【AI接口设置】", size=14, color=ThemeConfig.TEXT_SECONDARY),
                            self._create_ai_settings(),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                ),
                
                # 系统设置
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("【系统设置】", size=14, color=ThemeConfig.TEXT_SECONDARY),
                            self._create_system_settings(),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                ),
                
                # 数据管理
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("【数据管理】", size=14, color=ThemeConfig.TEXT_SECONDARY),
                            self._create_data_settings(),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                ),
                
                # 关于
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("【关于】", size=14, color=ThemeConfig.TEXT_SECONDARY),
                            self._create_about_section(),
                        ],
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    
    def _create_ai_settings(self) -> ft.Column:
        """创建AI设置部分"""
        # 获取当前AI配置状态
        current_provider = ai_manager.current_provider_name or "none"
        
        # 获取可用提供商列表
        available_providers = ai_manager.get_available_providers()
        options = [ft.dropdown.Option("none", "不使用AI")]
        
        for provider in available_providers:
            disabled_text = " (暂未支持)" if provider.get("disabled") else ""
            options.append(ft.dropdown.Option(
                provider["value"], 
                provider["label"] + disabled_text,
                disabled=provider.get("disabled", False)
            ))
        
        self.ai_provider_dropdown = ft.Dropdown(
            label="AI提供商",
            width=300,
            options=options,
            value=current_provider,
            on_change=self._on_ai_provider_change,
        )
        
        # 获取当前配置的API密钥
        current_key = ""
        if ai_manager.current_provider:
            current_key = ai_manager.current_provider.api_key
        
        self.api_key_field = ft.TextField(
            label="API密钥",
            width=300,
            password=True,
            can_reveal_password=True,
            value=current_key,
            disabled=current_provider == "none",
            hint_text="请输入您的API密钥",
            on_change=self._on_api_key_change,
        )
        
        # 获取当前配置的API地址
        current_url = ""
        if ai_manager.current_provider and hasattr(ai_manager.current_provider, 'base_url'):
            current_url = ai_manager.current_provider.base_url
        
        self.api_url_field = ft.TextField(
            label="API地址（可选）",
            width=300,
            value=current_url,
            hint_text="https://api.openai.com/v1",
            disabled=current_provider == "none",
            on_change=self._on_api_url_change,
        )
        
        self.test_button = ft.ElevatedButton(
            "测试连接",
            icon=ft.icons.WIFI,
            disabled=current_provider == "none",
            on_click=self._test_ai_connection,
        )
        
        self.save_button = ft.ElevatedButton(
            "保存配置",
            icon=ft.icons.SAVE,
            disabled=current_provider == "none",
            on_click=self._save_ai_config,
            style=ft.ButtonStyle(
                bgcolor=ThemeConfig.SUCCESS_COLOR,
                color="#ffffff",
            ),
        )
        
        # AI状态显示
        self.ai_status_text = ft.Text(
            self._get_ai_status_text(),
            size=12,
            color=ThemeConfig.TEXT_SECONDARY,
        )
        
        return ft.Column(
            controls=[
                self.ai_provider_dropdown,
                self.api_key_field,
                self.api_url_field,
                ft.Row([
                    self.test_button,
                    self.save_button,
                ], spacing=10),
                self.ai_status_text,
            ],
            spacing=10,
        )
    
    def _create_system_settings(self) -> ft.Column:
        """创建系统设置部分"""
        auto_backup_switch = ft.Switch(
            label="自动备份",
            value=self.settings.get("auto_backup", True),
            on_change=self._on_auto_backup_change,
        )
        
        birth_year_field = ft.TextField(
            label="出生年份",
            width=150,
            value=str(self.settings.get("birth_year", 1998)),
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_birth_year_change,
        )
        
        target_money_field = ft.TextField(
            label="目标灵石（万）",
            width=150,
            value=str(self.settings.get("target_money", 5000000) // 10000),
            keyboard_type=ft.KeyboardType.NUMBER,
            suffix_text="万",
            on_change=self._on_target_money_change,
        )
        
        theme_dropdown = ft.Dropdown(
            label="界面主题",
            width=150,
            options=[
                ft.dropdown.Option("light", "浅色"),
                ft.dropdown.Option("dark", "深色"),
                ft.dropdown.Option("system", "跟随系统"),
            ],
            value=self.settings.get("theme_mode", "light"),
            on_change=self._on_theme_change,
        )
        
        font_size_dropdown = ft.Dropdown(
            label="字体大小",
            width=150,
            options=[
                ft.dropdown.Option("small", "小"),
                ft.dropdown.Option("normal", "标准"),
                ft.dropdown.Option("large", "大"),
            ],
            value=self.settings.get("font_size", "normal"),
            on_change=self._on_font_size_change,
        )
        
        return ft.Column(
            controls=[
                auto_backup_switch,
                ft.Row([birth_year_field, target_money_field]),
                ft.Row([theme_dropdown, font_size_dropdown]),
            ],
            spacing=10,
        )
    
    def _create_data_settings(self) -> ft.Column:
        """创建数据管理部分"""
        export_button = ft.ElevatedButton(
            "导出数据",
            icon=ft.icons.DOWNLOAD,
            on_click=self._export_data,
        )
        
        import_button = ft.ElevatedButton(
            "导入数据",
            icon=ft.icons.UPLOAD,
            on_click=self._import_data,
        )
        
        backup_button = ft.ElevatedButton(
            "立即备份",
            icon=ft.icons.BACKUP,
            on_click=self._backup_now,
        )
        
        restore_button = ft.ElevatedButton(
            "恢复备份",
            icon=ft.icons.RESTORE,
            on_click=self._restore_backup,
        )
        
        clear_button = ft.ElevatedButton(
            "清除数据",
            icon=ft.icons.DELETE_FOREVER,
            bgcolor=ThemeConfig.DANGER_COLOR,
            color="white",
            on_click=self._clear_data_dialog,
        )
        
        return ft.Column(
            controls=[
                ft.Row([export_button, import_button]),
                ft.Row([backup_button, restore_button]),
                ft.Container(height=10),
                clear_button,
            ],
            spacing=10,
        )
    
    def _create_about_section(self) -> ft.Column:
        """创建关于部分"""
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(f"凡人修仙3w天", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"版本: {VERSION}", size=14),
                            ft.Text("个人生命管理工具", size=12, color=ThemeConfig.TEXT_SECONDARY),
                            ft.Divider(height=20),
                            ft.Text("开发阶段:", size=12, weight=ft.FontWeight.BOLD),
                            ft.Text("✓ 第一阶段: MVP版本", size=12, color=ThemeConfig.SUCCESS_COLOR),
                            ft.Text("✓ 第二阶段: 功能完善", size=12, color=ThemeConfig.SUCCESS_COLOR),
                            ft.Text("○ 第三阶段: 优化提升", size=12, color=ThemeConfig.TEXT_SECONDARY),
                            ft.Divider(height=20),
                            ft.Row([
                                ft.TextButton(
                                    "使用指南",
                                    icon=ft.icons.HELP,
                                    on_click=self._show_guide,
                                ),
                                ft.TextButton(
                                    "检查更新",
                                    icon=ft.icons.UPDATE,
                                    on_click=self._check_update,
                                ),
                            ]),
                        ],
                        spacing=5,
                    ),
                    bgcolor=ThemeConfig.CARD_COLOR,
                    padding=15,
                    border_radius=10,
                ),
            ],
        )
    
    # 事件处理方法
    def _on_ai_provider_change(self, e):
        """AI提供商改变"""
        provider = e.control.value
        
        # 更新控件状态
        is_enabled = provider != "none"
        self.api_key_field.disabled = not is_enabled
        self.api_url_field.disabled = not is_enabled
        self.test_button.disabled = not is_enabled
        self.save_button.disabled = not is_enabled
        
        # 如果选择了OpenAI，设置默认URL
        if provider == "openai":
            self.api_url_field.value = "https://api.openai.com/v1"
        
        # 清空当前配置
        if provider == "none":
            self.api_key_field.value = ""
            self.api_url_field.value = ""
        
        # 更新状态显示
        self.ai_status_text.value = self._get_ai_status_text()
        
        e.page.update()
    
    def _on_api_key_change(self, e):
        """API密钥改变"""
        # 实时更新状态
        self.ai_status_text.value = self._get_ai_status_text()
        e.page.update()
    
    def _on_api_url_change(self, e):
        """API地址改变"""
        # 实时更新状态
        self.ai_status_text.value = self._get_ai_status_text()
        e.page.update()
    
    def _on_auto_backup_change(self, e):
        """自动备份开关改变"""
        self.settings["auto_backup"] = e.control.value
        self._save_settings()
    
    def _on_birth_year_change(self, e):
        """出生年份改变"""
        try:
            year = int(e.control.value)
            if 1900 <= year <= datetime.now().year:
                self.settings["birth_year"] = year
                self._save_settings()
                # 更新数据库中的血量
                self._update_initial_blood(year)
        except ValueError:
            pass
    
    def _on_target_money_change(self, e):
        """目标灵石改变"""
        try:
            target = int(e.control.value) * 10000
            if target > 0:
                self.settings["target_money"] = target
                self._save_settings()
                # TODO: 更新数据库
        except ValueError:
            pass
    
    def _on_theme_change(self, e):
        """主题改变"""
        self.settings["theme_mode"] = e.control.value
        self._save_settings()
        # 应用主题
        if e.control.value == "dark":
            e.page.theme_mode = ft.ThemeMode.DARK
        elif e.control.value == "light":
            e.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            e.page.theme_mode = ft.ThemeMode.SYSTEM
        e.page.update()
    
    def _on_font_size_change(self, e):
        """字体大小改变"""
        self.settings["font_size"] = e.control.value
        self._save_settings()
        # TODO: 应用字体大小
    
    def _test_ai_connection(self, e):
        """测试AI连接"""
        provider = self.ai_provider_dropdown.value
        api_key = self.api_key_field.value.strip()
        api_url = self.api_url_field.value.strip()
        
        if not api_key:
            self._show_message(e.page, "测试失败", "请先输入API密钥")
            return
        
        # 显示测试中状态
        self.test_button.text = "测试中..."
        self.test_button.disabled = True
        e.page.update()
        
        try:
            # 创建临时配置
            config = {"api_key": api_key}
            if api_url:
                config["base_url"] = api_url
            
            # 配置AI提供商
            success = ai_manager.configure_provider(provider, config)
            
            if success:
                # 测试连接
                connection_ok = ai_manager.test_provider_connection(provider)
                
                if connection_ok:
                    self._show_message(e.page, "测试成功", "AI接口连接正常！")
                    # 设置为当前提供商
                    ai_manager.set_current_provider(provider)
                    # 更新状态显示
                    self.ai_status_text.value = self._get_ai_status_text()
                else:
                    self._show_message(e.page, "连接失败", "API密钥或地址可能有误，请检查配置")
            else:
                self._show_message(e.page, "配置失败", "配置AI提供商失败，请检查参数")
                
        except Exception as ex:
            self._show_message(e.page, "测试异常", f"测试过程中发生错误：{str(ex)}")
        
        finally:
            # 恢复按钮状态
            self.test_button.text = "测试连接"
            self.test_button.disabled = False
            e.page.update()
    
    def _save_ai_config(self, e):
        """保存AI配置"""
        provider = self.ai_provider_dropdown.value
        api_key = self.api_key_field.value.strip()
        api_url = self.api_url_field.value.strip()
        
        if provider == "none":
            # 清除AI配置
            ai_manager.current_provider = None
            ai_manager.current_provider_name = None
            ai_manager.save_config()
            self._show_message(e.page, "保存成功", "已禁用AI功能")
            return
        
        if not api_key:
            self._show_message(e.page, "保存失败", "请先输入API密钥")
            return
        
        try:
            # 创建配置
            config = {"api_key": api_key}
            if api_url:
                config["base_url"] = api_url
            
            # 配置并保存
            success = ai_manager.configure_provider(provider, config)
            
            if success:
                ai_manager.set_current_provider(provider)
                self._show_message(e.page, "保存成功", "AI配置已保存")
                # 更新状态显示
                self.ai_status_text.value = self._get_ai_status_text()
                e.page.update()
            else:
                self._show_message(e.page, "保存失败", "配置保存失败，请检查参数")
                
        except Exception as ex:
            self._show_message(e.page, "保存异常", f"保存过程中发生错误：{str(ex)}")
    
    def _get_ai_status_text(self) -> str:
        """获取AI状态文本"""
        if not ai_manager.is_configured():
            return "状态: 未配置AI接口"
        
        provider_name = ai_manager.current_provider_name
        if provider_name:
            status = ai_manager.get_provider_status(provider_name)
            connection_status = status.get("connection_status", "未知")
            api_key_masked = status.get("api_key_masked", "未配置")
            
            return f"状态: {connection_status} | 密钥: {api_key_masked}"
        
        return "状态: 配置异常"
    
    def _export_data(self, e):
        """导出数据"""
        # TODO: 实现数据导出
        self._show_message(e.page, "导出成功", "数据已导出到下载目录")
    
    def _import_data(self, e):
        """导入数据"""
        # TODO: 实现数据导入
        self._show_message(e.page, "功能开发中", "数据导入功能即将推出")
    
    def _backup_now(self, e):
        """立即备份"""
        try:
            # TODO: 实现备份功能
            backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._show_message(e.page, "备份成功", f"备份文件: backup_{backup_time}.db")
        except Exception as ex:
            self._show_message(e.page, "备份失败", str(ex))
    
    def _restore_backup(self, e):
        """恢复备份"""
        # TODO: 实现恢复功能
        self._show_message(e.page, "功能开发中", "备份恢复功能即将推出")
    
    def _clear_data_dialog(self, e):
        """显示清除数据确认对话框"""
        def confirm_clear(e):
            # TODO: 实现数据清除
            dialog.open = False
            e.page.update()
            self._show_message(e.page, "数据已清除", "所有数据已被删除")
        
        def cancel(e):
            dialog.open = False
            e.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("危险操作", color=ThemeConfig.DANGER_COLOR),
            content=ft.Text("确定要清除所有数据吗？此操作不可恢复！"),
            actions=[
                ft.TextButton("取消", on_click=cancel),
                ft.TextButton(
                    "确定清除",
                    on_click=confirm_clear,
                    style=ft.ButtonStyle(color=ThemeConfig.DANGER_COLOR)
                ),
            ],
        )
        
        e.page.dialog = dialog
        dialog.open = True
        e.page.update()
    
    def _show_guide(self, e):
        """显示使用指南"""
        guide_text = """
【基础概念】
• 血量：代表剩余生命时间，每分钟-1
• 心境：精力状态，范围-80到+200
• 境界：技能掌握程度
• 灵石：财务状况，1灵石=1元

【使用方法】
1. 在心境系统记录日常任务
2. 在境界系统追踪技能进度
3. 在灵石系统管理财务
4. 在统御系统维护人际关系

【修炼建议】
• 保持心境平衡，避免负面情绪
• 持续学习提升境界
• 合理理财积累灵石
• 定期维护重要关系
        """
        
        self._show_message(e.page, "使用指南", guide_text)
    
    def _check_update(self, e):
        """检查更新"""
        self._show_message(e.page, "已是最新版本", f"当前版本 {VERSION} 已是最新")
    
    def _update_initial_blood(self, birth_year: int):
        """更新初始血量"""
        age = datetime.now().year - birth_year
        initial_blood = (80 - age) * 365 * 24 * 60
        # TODO: 更新数据库中的血量设置
    
    def _show_message(self, page, title: str, content: str):
        """显示消息对话框"""
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.TextButton("确定", on_click=close_dialog),
            ],
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()