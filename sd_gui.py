from math import floor
from dearpygui.core import *
from dearpygui.simple import *
from serial_test import *
# from serial_interface import *
from threading import Condition
import time


class serial_debug_gui():
    def __init__(self):
        self.port = None
        self.port_list = None
        self.create_main_window()
        self.last_plot_render = time.time()

    def set_style(self):
        set_style_window_padding(4.00, 4.00)
        set_style_frame_padding(2.00, 2.00)
        set_style_item_spacing(8.00, 4.00)
        set_style_item_inner_spacing(4.00, 4.00)
        set_style_touch_extra_padding(0.00, 0.00)
        set_style_indent_spacing(21.00)
        set_style_scrollbar_size(14.00)
        set_style_grab_min_size(6.00)
        set_style_window_border_size(1.00)
        set_style_child_border_size(1.00)
        set_style_popup_border_size(1.00)
        set_style_frame_border_size(0.00)
        set_style_tab_border_size(0.00)
        set_style_window_rounding(5.00)
        set_style_child_rounding(0.00)
        set_style_frame_rounding(0.00)
        set_style_popup_rounding(0.00)
        set_style_scrollbar_rounding(9.00)
        set_style_grab_rounding(0.00)
        set_style_tab_rounding(3.00)
        set_style_window_title_align(0.00, 0.50)
        set_style_window_menu_button_position(mvDir_Left)
        set_style_color_button_position(mvDir_Right)
        set_style_button_text_align(0.50, 0.50)
        set_style_selectable_text_align(0.00, 0.00)
        set_style_display_safe_area_padding(7.00, 3.00)
        set_style_global_alpha(1.00)
        set_style_antialiased_lines(True)
        set_style_antialiased_fill(True)
        set_style_curve_tessellation_tolerance(1.25)
        set_style_circle_segment_max_error(1.60)

    def toggle_port_sel_win(self, *args):
        if is_item_visible("Select Port"):
            hide_item("Select Port")
        else:
            show_item("Select Port")

    def select_port(self, *args):
        port = self.port_list[get_value("portslist")]
        baudrate = get_value("baudrate")
        print(port, baudrate)
        if (self.port != None):
            if (self.port.port == port) or (self.port.baudrate == baudrate):
                return
            else:
                self.port.close()
        self.port = serial_interface(
            port, baudrate, log_window="Logger", raw_log_window="Raw Logger")
        self.set_window_layout()

    def refresh_portslist(self, *args):
        self.port_list = list_ports()
        configure_item("portslist", items=self.port_list)

    def create_port_sel_window(self):
        self.port_list = list_ports()
        with window("Select Port", x_pos=0, y_pos=20):
            add_text("Select port")
            add_same_line()
            add_button("refresh ports", callback=self.refresh_portslist)
            add_listbox("portslist", items=self.port_list)
            add_input_int("baudrate", default_value=115200)
            add_button("setlect port button",
                       callback=self.select_port, label="select port")

    def set_window_layout(self, *args):
        size = get_item_rect_size("Main Window")
        menu_height = get_item_height("MenuBar")
        width_4 = floor(size[0]/4)
        height_4 = floor((size[1]-menu_height)/4)

        # setting the size of the select port window
        configure_item("Select Port", x_pos=0, y_pos=menu_height,
                       width=floor(width_4/2), height=height_4)
        # setting the log window
        configure_item("Logger Window", x_pos=0, y_pos=menu_height+height_4,
                       width=width_4, height=height_4*2)
        # setting the Raw log window
        configure_item("Raw Logger Window", x_pos=0, y_pos=menu_height+height_4*3,
                       width=width_4, height=height_4)
        
        # set the graph grid
        # first determine how many plots are visible.
        if(self.port!=None):
            all_plots = self.port.get_data()["plots"].keys()
            visible_plots = []
            for name in all_plots:
                plot_name = f"{name}##window"
                if is_item_shown(plot_name):
                    visible_plots.append(plot_name)

            # now layout the plots favouring devision in height
            n = len(visible_plots)
            if n ==1:
                n_width =1
                n_height = n
            elif n ==2 or n==3:
                n_width =1
                n_height = n
            elif n == 4:
                n_width = 2
                n_height = 2
                
            elif n<=6:
                n_width = 2
                n_height = 3
            elif n<=8:
                n_width = 2
                n_height = 4
            elif n == 9:
                n_width = 3
                n_height = 3
            elif n<=12:
                n_width = 3
                n_height = 4
            elif n<=16:
                n_width = 4
                n_height = 4
            elif n <=20:
                n_width = 5
                n_height = 4
            elif n <=25:
                n_width = 5
                n_height = 5
            elif n<= 30:
                n_width = 6
                n_height = 5
            
            for i in range(n):
                configure_item(visible_plots[i],x_pos=width_4+(i%n_width)*floor((width_4*3)/n_width), y_pos=menu_height+floor(i/n_width)*floor(height_4*4/n_height),
                       width=floor((width_4*3)/n_width), height=floor(height_4*4/n_height))


    def update_plot(self, name, data):
        clear_plot(f"{name}##plot")
        tdata = []
        now = time.time()
        for t in data["t"]:
            tdata.append(t-now)
        add_line_series(f"{name}##plot", f"{name}##line",
                        tdata, data["x"], weight=2)
        set_plot_ylimits_auto(f"{name}##plot")
        set_plot_xlimits(f"{name}##plot", tdata[0], 0.0)

    def create_plot(self, name: str, data):
        print(f"created new plot window {name}")
        with window(f"{name}##window"):
            plotname = f"{name}##plot"
            add_plot(plotname)
            add_line_series(plotname, f"{name}##line",
                            data["t"], data["x"], weight=2)

            set_plot_xlimits_auto(plotname)
            set_plot_ylimits_auto(plotname)
            # add_data(f"{name}_datat", list(data["t"]))
            # add_data(f"{name}_datax", list(data["x"]))

    def render_plots(self):
        if self.port != None:
            data = self.port.get_data()
            all_items = get_windows()
            for key in data["plots"]:
                if f"{key}##window" in all_items:
                    # print(f"updating plot {key}")
                    self.update_plot(key, data["plots"][key])
                else:
                    self.create_plot(key, data["plots"][key])

    def on_render(self, *args):
        now = time.time()
        if(now-self.last_plot_render > 0.01):
            try:
                self.render_plots()
            except:
                pass
            self.last_plot_render = now

    def close_app(self, *args):
        print("closing the window")
        self.port.close()

    def create_main_window(self):
        with window("Main Window"):
            with menu_bar("MenuBar"):
                with menu("Tools"):
                    add_menu_item(
                        "Select Port menu", label="Select Port", callback=self.toggle_port_sel_win)
                    with tooltip("Select Port menu", "tooltip1"):
                        # this is because the popup doesnt have a width to set
                        add_dummy(width=150)
                        add_text(
                            'show the window for changing the port')
                    add_menu_item("Set Layout", callback=self.set_window_layout)
                    add_menu_item("Show Logger##demo", callback=show_logger)
                    add_menu_item("Show About##demo", callback=show_about)
                    add_menu_item("Show Metrics##demo", callback=show_metrics)
                    add_menu_item("Show Documentation##demo",
                                  callback=show_documentation)
                    add_menu_item("Show Debug##demo", callback=show_debug)
                with menu("Themes##demo"):
                    add_menu_item("Dark", callback=lambda sender,
                                  data: set_theme(sender), check=True)
                    add_menu_item("Light", callback=lambda sender,
                                  data: set_theme(sender), check=True)
                    add_menu_item("Classic", callback=lambda sender, data: set_theme(
                        sender), check=True, shortcut="Ctrl+Shift+T")
                    add_menu_item("Dark 2", callback=lambda sender,
                                  data: set_theme(sender), check=True)
                    add_menu_item("Grey", callback=lambda sender,
                                  data: set_theme(sender), check=True)
                    add_menu_item("Dark Grey", callback=lambda sender,
                                  data: set_theme(sender), check=True)
                    add_menu_item("Cherry", callback=lambda sender,
                                  data: set_theme(sender), check=True)
                    add_menu_item("Purple", callback=lambda sender,
                                  data: set_theme(sender), check=True)
                    add_menu_item("Gold", callback=lambda sender, data: set_theme(
                        sender), check=True, shortcut="Ctrl+Shift+P")
                    add_menu_item("Red", callback=lambda sender, data: set_theme(
                        sender), check=True, shortcut="Ctrl+Shift+Y")

        with window("Raw Logger Window"):
            add_logger("Raw Logger", autosize_x=True,
                       autosize_y=True, log_level=0, auto_scroll=True)
        with window("Logger Window"):
            add_logger("Logger", autosize_x=True, autosize_y=True, auto_scroll=True)

        self.create_port_sel_window()
        set_render_callback(self.on_render)
        self.set_style()
        set_exit_callback(self.close_app)
        # self.set_window_layout()

    def run(self):
        start_dearpygui(primary_window="Main Window")


if __name__ == "__main__":
    sd_gui = serial_debug_gui()
    sd_gui.run()
