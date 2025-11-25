import flet as ft

def main(page: ft.Page):
    """Main application entry point"""
    try:
        # Import configuration
        from config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, ThemeConfig

        # Set page properties
        page.title = "FanRen XiuXian 3W Day"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = ThemeConfig.BG_COLOR
        page.window_width = WINDOW_WIDTH
        page.window_height = WINDOW_HEIGHT
        page.window_resizable = True
        page.scroll = ft.ScrollMode.AUTO
        page.padding = 0
        page.spacing = 0
        page.theme = ft.Theme(
            color_scheme_seed=ThemeConfig.PRIMARY_COLOR,
            use_material3=True,
        )

        # Import and setup main window
        from ui.main_window import MainWindow
        window = MainWindow(page)
        window.setup()

    except Exception as e:
        import traceback
        # Show error if something fails
        error_text = ft.Column([
            ft.Text("Application Error", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.RED),
            ft.Text(f"Error: {str(e)}", size=14, selectable=True),
            ft.Text("Traceback:", size=12, weight=ft.FontWeight.BOLD),
            ft.Text(traceback.format_exc(), size=10, selectable=True),
        ], scroll=ft.ScrollMode.AUTO)
        page.add(error_text)
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
