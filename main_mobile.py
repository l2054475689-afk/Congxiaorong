"""
凡人修仙3w天 - 移动端优化版入口
适用于 Android/iOS 打包
"""
import flet as ft
from ui.main_window import MainWindow

def main(page: ft.Page):
    """主函数 - 移动端优化版"""
    try:
        # 设置页面基本属性
        page.title = "凡人修仙3w天"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = "#f5f5f5"

        # 移动端自适应窗口大小
        page.padding = 0
        page.spacing = 0

        # 创建主窗口实例并传入页面
        window = MainWindow(page)

        # 初始化界面
        window.setup()

    except Exception as e:
        # 显示错误信息
        error_msg = ft.Text(
            f"初始化错误:\n{str(e)}",
            size=16,
            color="red",
            text_align=ft.TextAlign.CENTER
        )
        page.add(
            ft.Container(
                content=error_msg,
                padding=20,
                alignment=ft.alignment.center,
                expand=True
            )
        )
        print(f"初始化错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 使用 Flet 应用启动
    ft.app(target=main)
