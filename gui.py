from dearpygui.core import *
from dearpygui.simple import *
from math import sin

def on_render(sender, data):
    frame_count = get_data("frame_count")
    frame_count += 1
    add_data("frame_count", frame_count)
    plot_data = get_value("plot_data")
    if len(plot_data) > 100:
        plot_data.pop(0)
    plot_data.append(sin(frame_count/30))
    set_value("plot_data", plot_data)

with window("Tutorial", width=500, height=500):
    add_simple_plot("Simple Plot", source="plot_data", minscale=-1.0, maxscale=1.0, height=300)
    add_data("frame_count", 0)
    set_render_callback(on_render)

with window("Test"):
    add_text("Here is some dummy text")

with window("Tutorial"):
    add_text("Hoping this is added to the Tutorial window")

start_dearpygui()