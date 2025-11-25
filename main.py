# -*- coding: utf-8 -*-
import flet as ft

def main(page: ft.Page):
    """Main application entry point - lazy loading version"""

    # Create status display
    status = ft.Text("Loading...", size=12, selectable=True)
    page.add(status)
    page.update()

    logs = []

    def log(msg):
        logs.append(msg)
        status.value = "\n".join(logs[-25:])
        try:
            page.update()
        except:
            pass

    try:
        log("Step 1: Importing config...")
        from config import ThemeConfig, GameConfig
        log("Step 1: OK")

        log("Step 2: Setting page properties...")
        page.title = "FanRen XiuXian 3W Day"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = ThemeConfig.BG_COLOR
        page.scroll = ft.ScrollMode.AUTO
        page.padding = 0
        log("Step 2: OK")

        log("Step 3: Creating simple UI...")
        # Create a simple working UI first
        page.clean()

        # Simple working interface
        header = ft.Container(
            content=ft.Text("FanRen XiuXian 3W Day", size=20, weight=ft.FontWeight.BOLD),
            padding=20,
            bgcolor=ThemeConfig.PRIMARY_COLOR,
        )

        content = ft.Column([
            ft.Text("App loaded successfully!", size=16),
            ft.Text("Systems will load on demand.", size=12),
            ft.ElevatedButton("Load Full App", on_click=lambda _: load_full_app())
        ], padding=20)

        page.add(ft.Column([header, content], expand=True))
        page.update()
        log("Step 3: Simple UI loaded")

        def load_full_app():
            """Load full application when user clicks"""
            try:
                status2 = ft.Text("Loading full app...", size=12)
                page.clean()
                page.add(status2)
                page.update()

                from ui.main_window import MainWindow
                window = MainWindow(page)
                page.clean()
                window.setup()

            except Exception as e:
                import traceback
                page.clean()
                error_text = ft.Column([
                    ft.Text("Error loading app", size=18, color=ft.colors.RED),
                    ft.Text(str(e)[:200], size=12, selectable=True),
                    ft.Text(traceback.format_exc()[:1000], size=10, selectable=True),
                ], scroll=ft.ScrollMode.AUTO)
                page.add(error_text)
                page.update()

    except Exception as e:
        import traceback
        log(f"ERROR: {str(e)[:150]}")
        log(f"Type: {type(e).__name__}")
        for line in traceback.format_exc().split('\n')[:20]:
            if line.strip():
                log(line[:90])

if __name__ == "__main__":
    ft.app(target=main)
