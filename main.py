import flet as ft
from config import ThemeConfig

def main(page: ft.Page):
    """主函数 - 自适应版"""
    try:
        # 设置页面基本属性
        page.title = "凡人修仙3万天"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = ThemeConfig.BG_COLOR

        # 设置窗口为自适应（移动端）
        page.window_width = None  # 自适应宽度
        page.window_height = None  # 自适应高度
        page.window_resizable = True  # 允许调整大小

        # 设置视口适配（针对移动端）
        page.scroll = ft.ScrollMode.AUTO
        page.padding = 0
        page.spacing = 0

        # 设置主题（移除外部字体依赖，避免国内网络问题）
        page.theme = ft.Theme(
            color_scheme_seed=ThemeConfig.PRIMARY_COLOR,
            use_material3=True,
        )

        # 延迟导入，捕获导入错误
        from ui.main_window import MainWindow

        # 创建主窗口实例并传入页面
        window = MainWindow(page)

        # 初始化界面
        window.setup()

    except Exception as e:
        # 显示错误信息
        import traceback
        error_msg = f"初始化错误:\n{str(e)}\n\n{traceback.format_exc()}"
        page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("应用启动失败", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.RED),
                        ft.Text(error_msg, size=12, selectable=True),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                expand=True,
            )
        )
        page.update()

if __name__ == "__main__":
    # 使用新的启动方式
    ft.app(target=main)