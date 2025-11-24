import flet as ft

def main(page: ft.Page):
    """主函数 - 测试版"""
    try:
        # 显示测试信息
        page.add(ft.Text("Step 1: main函数已启动", size=20))
        page.update()

        # 测试导入config
        try:
            from config import ThemeConfig
            page.add(ft.Text("Step 2: config导入成功", size=20, color=ft.colors.GREEN))
            page.update()
        except Exception as e:
            page.add(ft.Text(f"Step 2 失败: {str(e)}", size=20, color=ft.colors.RED))
            page.update()
            return

        # 设置页面基本属性
        page.title = "凡人修仙3万天"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = ThemeConfig.BG_COLOR
        page.window_width = None
        page.window_height = None
        page.window_resizable = True
        page.scroll = ft.ScrollMode.AUTO
        page.padding = 0
        page.spacing = 0
        page.theme = ft.Theme(
            color_scheme_seed=ThemeConfig.PRIMARY_COLOR,
            use_material3=True,
        )

        page.add(ft.Text("Step 3: 页面配置完成", size=20, color=ft.colors.GREEN))
        page.update()

        # 测试导入MainWindow
        try:
            from ui.main_window import MainWindow
            page.add(ft.Text("Step 4: MainWindow导入成功", size=20, color=ft.colors.GREEN))
            page.update()
        except Exception as e:
            page.add(ft.Text(f"Step 4 失败: {str(e)}", size=20, color=ft.colors.RED))
            page.update()
            import traceback
            page.add(ft.Text(traceback.format_exc(), size=10, selectable=True))
            page.update()
            return

        # 测试创建MainWindow
        try:
            window = MainWindow(page)
            page.add(ft.Text("Step 5: MainWindow创建成功", size=20, color=ft.colors.GREEN))
            page.update()
        except Exception as e:
            page.add(ft.Text(f"Step 5 失败: {str(e)}", size=20, color=ft.colors.RED))
            page.update()
            import traceback
            page.add(ft.Text(traceback.format_exc(), size=10, selectable=True))
            page.update()
            return

        # 测试setup
        try:
            page.clean()  # 清除测试信息
            window.setup()
        except Exception as e:
            page.add(ft.Text(f"Step 6 失败: {str(e)}", size=20, color=ft.colors.RED))
            page.update()
            import traceback
            page.add(ft.Text(traceback.format_exc(), size=10, selectable=True))
            page.update()
            return

    except Exception as e:
        import traceback
        error_msg = f"未捕获错误:\n{str(e)}\n\n{traceback.format_exc()}"
        page.add(ft.Text("应用启动失败", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.RED))
        page.add(ft.Text(error_msg, size=12, selectable=True))
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
