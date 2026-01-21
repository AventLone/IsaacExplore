from abc import ABC, abstractmethod
from screeninfo import get_monitors
import dearpygui.dearpygui as dpg

class MainWindow(ABC):
    MAIN_WINDOW_NAME = "MainWindow"
    MONITOR_SIZE = (1980, 1080)

    for monitor in get_monitors():
        if monitor.is_primary:
            MONITOR_SIZE = (monitor.width, monitor.height)

    def __init__(self, window_title: str, window_szie: tuple[int, int], resizable=True) -> None:
        dpg.create_context()
        dpg.set_global_font_scale(3)
        self._setup_windows()
        dpg.create_viewport(title=window_title, width=window_szie[0], height=window_szie[1],
                            x_pos=round((MainWindow.MONITOR_SIZE[0] - window_szie[0]) / 2),
                            y_pos=round((MainWindow.MONITOR_SIZE[1] - window_szie[1]) / 2),
                            resizable=resizable)
        dpg.setup_dearpygui()        

    def show(self):
        dpg.show_viewport()
        dpg.set_primary_window(MainWindow.MAIN_WINDOW_NAME, True)
        self._render_loop()
        dpg.destroy_context()

    def _render_loop(self):
        while dpg.is_dearpygui_running():
            self._render_once()
            dpg.render_dearpygui_frame()

    @abstractmethod
    def _setup_windows(self):
        pass

    @abstractmethod
    def _render_once(self):
        pass

class TestWindow(MainWindow):
    def __init__(self, window_title: str) -> None:
        window_size = (round(MainWindow.MONITOR_SIZE[0] / 4), round(MainWindow.MONITOR_SIZE[1] / 4))
        self.checkbox_states = {"Semantic Segmentation": False, "Instance Segmentation": True, "BBox 2D": False}
        super().__init__(window_title, window_size, resizable=False)

        self.environments_path = ""
        self.objs_path = ""

    def _setup_windows(self):
        self._setup_mainwindow()

    def _render_once(self):
        return super()._render_once()
    
    def _setup_mainwindow(self):
        def checkbox_changed(sender, app_data):
            option_name: str = dpg.get_item_label(sender) # type: ignore
            self.checkbox_states[option_name] = app_data
            print(f"{option_name}: {app_data}")

        # 1. The callback that handles the folder selection
        def environments_folder_callback(sender, app_data):
            # app_data contains a dictionary; 'file_path_name' is the full path
            folder_path = app_data.get("file_path_name", "")
            dpg.set_value("folder_input", self.environments_path)

        # 2. Define the file dialog (hidden by default)
        with dpg.file_dialog(
            label="Select Folder", 
            tag="folder_dialog_tag", 
            show=False, 
            callback=environments_folder_callback, 
            directory_selector=True, # Critical for folder selection
            width=600, 
            height=400
        ):
            dpg.add_file_extension(".*") # Necessary to show items in dialog

        with dpg.window(tag=MainWindow.MAIN_WINDOW_NAME):
            dpg.add_text("Hello, world")
            save_button = dpg.add_button(label="Save")
            # dpg.set_mouse_(button, dpg.mvCursor_Hand)
            self.data_required = dpg.add_input_text(label="Data frames", default_value="100")
            dpg.add_slider_float(label="float", default_value=0.273, max_value=1)

            # 1. Select generated data types
            with dpg.collapsing_header(label="Data Type Options", default_open=False, closable=False):
                for option_name, default_state in self.checkbox_states.items():
                    dpg.add_checkbox(
                        label=option_name,
                        default_value=default_state,
                        callback=checkbox_changed
                    )
            
            dpg.add_separator()
            dpg.add_text("Selected options will be shown here")

            # 2. Choose the environments and objs folders
            with dpg.group(horizontal=True):
                dpg.add_input_text(label="Selected Path", tag="folder_input", width=300)
                dpg.add_button(label="Browse...", callback=lambda: dpg.show_item("folder_dialog_tag"))

            # Create a table with 3 columns
            with dpg.table(header_row=False):
                # Column 1 & 3: Flexible spacers
                # Column 2: Fixed or sized to fit the button
                dpg.add_table_column() # Left spacer
                dpg.add_table_column(width_fixed=True) # Middle (content)
                dpg.add_table_column() # Right spacer

                with dpg.table_row():
                    dpg.add_text("") # Empty cell for left spacer
                    dpg.add_button(label="Centered Button") # The button
                    dpg.add_text("") # Empty cell for right spacer

if __name__ == "__main__":
    main_window = TestWindow("Test")
    main_window.show()
