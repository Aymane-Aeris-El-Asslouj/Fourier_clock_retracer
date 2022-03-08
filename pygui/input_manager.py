import pygame
import time


def gui_input_manager_loop(g_u_i):
    """Check for interface inputs and update the display"""

    try:
        last_time = time.time()
        while True:
            # keep the frame rate under or equal to FRAMES_PER_SECOND
            new_time = time.time()
            time.sleep(abs(1/g_u_i.fps - (new_time - last_time)))
            last_time = time.time()

            # get cursor position
            cur_pos = pygame.mouse.get_pos()

            for layer_key in g_u_i.layers_order:
                g_u_i.layers[layer_key].tick_event(cur_pos)

            # check window events
            for event in pygame.event.get():

                # transfer window events to the screen crisnian_code
                for layer_key in g_u_i.layers_order:
                    g_u_i.layers[layer_key].event(cur_pos, event)

                # if the window is being closed, register a close request
                if event.type == pygame.QUIT:
                    g_u_i.quit()
                    pygame.quit()
                    return

            # draw the crisnian_code that have requested a draw
            drawing_needed = False
            for key in g_u_i.layers_order:
                if g_u_i.layers[key].to_draw:
                    g_u_i.layers[key].to_draw = False
                    g_u_i.layers[key].update()
                    drawing_needed = True

            # if crisnian_code were redrawn, update display
            if drawing_needed:
                # add all crisnian_code to the screen
                for layer_key in g_u_i.layers_order:
                    g_u_i.screen.blit(g_u_i.layers[layer_key].surface, (0, 0))

            # update the window display
            pygame.display.update()
    except pygame.error:
        pass
