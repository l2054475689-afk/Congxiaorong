import flet as ft
import traceback
import sys
import os
import time

def main(page: ft.Page):
    """Main function - diagnostic version"""
    log_text = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True)
    page.add(log_text)

    def log(msg, color=None):
        """Add log message without immediate update"""
        log_text.controls.append(
            ft.Text(msg, size=12, color=color)
        )

    try:
        log("Step 1: main started")
        log(f"Python: {sys.version[:30]}")
        log(f"Platform: {sys.platform}")
        log(f"CWD: {os.getcwd()[:40]}")
        page.update()  # Single update for step 1

        time.sleep(0.5)  # Small delay

        # Step 2: Import config
        log("Step 2: Importing config...")
        page.update()

        try:
            import config
            log("Step 2.1: config module imported", ft.colors.GREEN)
            page.update()

            time.sleep(0.3)

            from config import ThemeConfig
            log("Step 2.2: ThemeConfig imported", ft.colors.GREEN)
            page.update()

        except Exception as e:
            log(f"Step 2 FAILED!", ft.colors.RED)
            log(f"Error: {str(e)[:100]}", ft.colors.RED)
            log(f"Type: {type(e).__name__}")
            page.update()

            # Show traceback
            error_lines = traceback.format_exc().split('\n')
            for line in error_lines[:20]:
                if line.strip():
                    log(line[:80])
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
