import flet as ft

def main(page: ft.Page):
    """Main application entry point - diagnostic version"""

    # Create diagnostic output
    status = ft.Text("Initializing...", size=12, selectable=True)
    page.add(status)
    page.update()

    logs = []

    def add_log(msg):
        logs.append(msg)
        status.value = "\n".join(logs[-20:])
        try:
            page.update()
        except:
            pass

    try:
        add_log("Step 1: Importing config...")
        from config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, ThemeConfig
        add_log("Step 1: Config imported OK")

        add_log("Step 2: Setting page properties...")
        page.title = "FanRen XiuXian 3W Day"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = ThemeConfig.BG_COLOR
        page.scroll = ft.ScrollMode.AUTO
        page.padding = 0
        page.spacing = 0
        add_log("Step 2: Page properties set OK")

        add_log("Step 3: Testing system imports...")

        # Test each import individually
        add_log("Step 3.1: Importing database...")
        from database.db_manager import DatabaseManager
        add_log("Step 3.1: OK")

        add_log("Step 3.2: Importing panel...")
        from systems.panel import PanelSystem
        add_log("Step 3.2: OK")

        add_log("Step 3.3: Importing xinjing...")
        from systems.xinjing import XinjingSystem
        add_log("Step 3.3: OK")

        add_log("Step 3.4: Importing jingjie...")
        from systems.jingjie import JingjieSystem
        add_log("Step 3.4: OK")

        add_log("Step 3.5: Importing lingshi...")
        from systems.lingshi import LingshiSystem
        add_log("Step 3.5: OK")

        add_log("Step 3.6: Importing tongyu...")
        from systems.tongyu import TongyuSystem
        add_log("Step 3.6: OK")

        add_log("Step 3.7: Importing lizhi...")
        from systems.lizhi import LizhiSystem
        add_log("Step 3.7: OK")

        add_log("Step 3.8: Importing settings...")
        from systems.settings import SettingsSystem
        add_log("Step 3.8: OK")

        add_log("Step 3.9: Importing MainWindow...")
        from ui.main_window import MainWindow
        add_log("Step 3.9: MainWindow imported OK")

        add_log("Step 4: Creating MainWindow instance...")
        window = MainWindow(page)
        add_log("Step 4: MainWindow instance created OK")

        add_log("Step 5: Calling window.setup()...")
        page.clean()  # Clear diagnostic messages
        window.setup()
        add_log("Step 5: Setup complete!")

    except Exception as e:
        import traceback
        add_log(f"ERROR at current step!")
        add_log(f"Error: {str(e)[:200]}")
        add_log(f"Type: {type(e).__name__}")
        add_log("--- Traceback ---")
        for line in traceback.format_exc().split('\n')[:25]:
            if line.strip():
                add_log(line[:100])

if __name__ == "__main__":
    ft.app(target=main)
