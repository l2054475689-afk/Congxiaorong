import flet as ft
import traceback
import sys
import os

def main(page: ft.Page):
    """Main function - minimal update version"""

    # Create a simple text control for logging
    output = ft.Text("Starting...", selectable=True, size=11)
    page.add(output)
    page.update()

    logs = []

    def update_log():
        output.value = "\n".join(logs[-30:])  # Show last 30 lines
        try:
            page.update()
        except:
            pass

    try:
        logs.append("=== DIAGNOSTIC MODE ===")
        logs.append(f"Step 1: Started")
        logs.append(f"Python: {sys.version[:35]}")
        logs.append(f"Platform: {sys.platform}")
        update_log()

        # Critical test: Can we import anything?
        logs.append("Step 2: Test import sys")
        import sys as sys2
        logs.append("Step 2.1: sys import OK")
        update_log()

        # Test pathlib
        logs.append("Step 3: Test import pathlib")
        from pathlib import Path
        logs.append("Step 3.1: pathlib OK")
        update_log()

        # Now test config
        logs.append("Step 4: Import config...")
        update_log()

        import config
        logs.append("Step 4.1: config imported!")
        update_log()

        from config import ThemeConfig
        logs.append("Step 4.2: ThemeConfig imported!")
        update_log()

        logs.append("=== SUCCESS ===")
        update_log()

    except Exception as e:
        logs.append(f"ERROR: {str(e)[:100]}")
        logs.append(f"Type: {type(e).__name__}")
        logs.extend(traceback.format_exc().split('\n')[:15])
        update_log()

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
