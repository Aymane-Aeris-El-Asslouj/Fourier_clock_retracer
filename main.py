from pygui import gui, input_manager as i_m
from crisnian_code import crisnian_layer as c_l
import os


FONT_TYPE = "Arial"
FONT_SIZE = 20
GUI_TITLE = "Crisnian"
GUI_WIDTH = 870
GUI_HEIGHT = 650
FRAME_RATE = 30


def main():

    # initialize GUI object
    g_u_i = gui.GUI(GUI_TITLE, (GUI_WIDTH, GUI_HEIGHT), FRAME_RATE)
    g_u_i.set_font(FONT_TYPE, FONT_SIZE)
    g_u_i.set_icon(os.path.join("icons", 'icon.png'))

    # add program layer
    c_layer = c_l.CrisnianLayer(g_u_i, (GUI_WIDTH, GUI_HEIGHT))
    g_u_i.add_layer("Crisnian layer", c_layer)

    # activate GUI (infinite interaction loop)
    i_m.gui_input_manager_loop(g_u_i)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
