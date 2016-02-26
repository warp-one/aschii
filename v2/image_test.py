import libtcodpy as libtcod

libtcod.console_set_custom_font('terminal8x8_gs_ro.png', 
            libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW,)
libtcod.console_init_root(30, 30, 'image test', False)
libtcod.sys_set_fps(60)

def handle_keys():
    key = libtcod.console_check_for_keypress()
    if key.vk == libtcod.KEY_ENTER:
        return True

cycl_image = libtcod.image_load('comics/cycl.png')

con = libtcod.console_new(30, 30)

while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(0, libtcod.white)
    libtcod.image_blit_2x(cycl_image, con, 0, 0, 0, 0, -1, -1)
    libtcod.console_put_char(con, 1, 1, '@', libtcod.BKGND_NONE)
    libtcod.console_blit(con, 0, 0, 30, 30, 0, 0, 0)
    libtcod.console_flush()
    
    if handle_keys():
        break