import flet as ft
from ui.main_window import MainWindow

def main(page: ft.Page):
    """主函数 - 修复版本"""
    # 设置页面基本属性
    page.title = "凡人修仙3w天"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f5f5f5"
    
    # 设置窗口大小
    page.window_width = 412
    page.window_height = 915
    page.window_resizable = False
    
    # 创建主窗口实例并传入页面
    window = MainWindow(page)
    
    # 初始化界面
    window.setup()

if __name__ == "__main__":
    # 使用新的启动方式
    ft.app(target=main)