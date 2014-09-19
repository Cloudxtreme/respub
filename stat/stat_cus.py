import curses, traceback, string, os
import configobj
import curscol
#import dmTxt2Html

#-- Define the appearance of some interface elements
hotkey_attr = curses.A_BOLD | curses.A_UNDERLINE
menu_attr = curses.A_NORMAL

#-- Define additional constants
EXIT = 0
CONTINUE = 1

#-- Define default conversion dictionary
cfg_dict = {'target': '/var/log/stat',
            'source': '/proc/net/stat',
            'type':   'INFER',
            'proxy':  'NONE' }
counter = 0
#dmTxt2Html.promo = string.replace(dmTxt2Html.promo, dmTxt2Html.cgi_home, '')


#-- Give screen module scope
screen = None

class menu_item():
  def __init__(self, s, args = None):
    self.name = args[0]
    self.func = args[1]
    self.args = args[2:]
    self.y = 0
    self.x = 0
    self.h = 0
    self.w = 0
    self.sub_top = 0
    self.sub_bottom = 0
    self.sub_left = 0
    self.sub_right = 0

  def getyx(self):
    return (self.y, self.x)
  
  def setyx(self, y, x):
    (self.y, self.x) = (y, x)

  def resize(self, h, w):
    (self.h, self.w) = (h, w)

  def getmaxyx(self):
    return (self.y + h, self.x + w)

  def setlimit(self, t, b, l, r):
    (self.sub_left, self.sub_right, self.sub_top, self.sub_bottom) = (l, r, t, b)
  
  def getsublimit(self):
    return (self.sub_left, self.sub_right, self.sub_top, self.sub_bottom )

  def run(self):
    self.func(self.args)


class menu_grp():
  def __init__(self, parent_item, direction, items):
    self.direction = direction
    self.items = items

    if direction == None:
      self.direction = 'vr'
    #items organize in horizontal
    if  direction[0] == 'h':
      self.h = 1
      mw = 1
      for item in tiems:
        mw += len (item[0]) + 1
        self.w = mw
    else:
      maxname = 0
      for item in tiems:
        if len (item[0]) > maxname: 
          maxname = len(item[0])
          self.w = maxname
    # calc yx
    self.py = self.px = 0
    self.my = self.mx = 0
    self.top = self.bottom = 0
    self.left = self.right = 0

    if parent_item != None:
      self.py, self.px = parent.getyx()
      self.my, self.mx = parent.getmaxyx()
      self.left, self.right, self.top, self.bottom = parent.getsublimit()
    else:
      self.py, self.px = screen.getyx()
      self.my, self.mx = (self.py, self.px + 1)
      self.top, self.left, self.bottom, self.right= screen.getyx(), screen.getmaxyx()

    if self.direction[1] == 'd':
      self.x = self.px
      self.y = self.my
    elif self.direction[1] == 'u':
      self.x = self.px
      self.y = self.py - self.h
    elif self.direction[1] == 'l':
      self.x = self.px - self.w
      if self.my - self.h > self.top:
        self.y = self.my - self.h
      else:
        self.y = self.top
    else: 
      self.x = self.mx 
      if self.my - self.h > self.top:
        self.y = self.my - self.h
      else:
        self.y = self.top

  def key_handler(self, kef_assign=None, key_dict={}):
    pass
    
  def run(self):
    self.s = screen.subwin(self.h, self.w, self.y, self.x)
    s.box()
    mmove = 0
    for item in self.items:
      tmp = menu_item(s, item)
      menu_name = tmp.name
      menu_hotkey = menu_name[0]
      menu_no_hot = menu_name[1:]
      if self.direction[0] == 'h':
        s.addstr(self.y, self.x + mmove, menu_hotkey, hotkey_attr)
        s.addstr(self.y, self.x + mmove + 1, menu_no_hot, menu_attr)
        tmp.x = self.x + mmove;
        mmove += len(menu_name) + 1
      else:
        s.addstr(self.y + mmove, self.x, menu_hotkey, hotkey_attr)
        s.addstr(self.y + mmove, self.x + 1, menu_no_hot, menu_attr)
        mmove += 1
    #wait for keyinput


           
#-- Create the topbar menu
def topbar_menu(menus):
    max_yx = screen.getmaxyx()

    left_sp = 2
    right_sp = 2
    app_title=">>>>>>>Pktstat Interface  "


    mlen = len(menus)
    min_len = len(app_title) + left_sp + right_sp 
    for menu in menus:
        menu_name = menu[0]
        min_len += len(menu_name) + 1

    if max_yx[1] < min_len:
        print "Error: screen's width is too short!"
        return 1

    left = left_sp
    msplice = (max_yx[1] - min_len) / mlen

    for menu in menus:
        menu_name = menu[0]
        menu_hotkey = menu_name[0]
        menu_no_hot = menu_name[1:]
        screen.addstr(1, left, menu_hotkey, hotkey_attr)
        screen.addstr(1, left+1, menu_no_hot, menu_attr)
        left = left + len(menu_name) + msplice 
        # Add key handlers for this hotkey
        topbar_key_handler((string.upper(menu_hotkey), menu[1], menu[2]))
        topbar_key_handler((string.lower(menu_hotkey), menu[1], menu[2]))

    # Little aesthetic thing to display application title
    screen.addstr(1, max_yx[1] - len(app_title) - 1,
                  app_title)
                  #">"*(52-left)+ "Pktstat Interface",
                   #curses.A_STANDOUT)
                  #curses.color_pair(2))
    screen.refresh()

#-- Magic key handler both loads and processes keys strokes
def topbar_key_handler(key_assign=None, key_dict={}, arg_dict={}):
    if key_assign:
        key_dict[ord(key_assign[0])] = key_assign[1]
        arg_dict[ord(key_assign[0])] = key_assign[2]
    else:
        c = screen.getch()
        if c in (curses.KEY_END, ord('!')):
            return 0
        elif c not in key_dict.keys():
            curses.beep()
            return 1
        else:
          #rv = eval(key_dict[c])
          print key_dict[c] + '(' + arg_dict[c].__str__() + ')'
          eval(key_dict[c] + '(' + arg_dict[c].__str__() + ')')

          return 1

#-- Handlers for the topbar menus
def help_func(args=None):
    help_lines = []
    offset = 0
    fh_help = open('txt2html.txt')
    for line in fh_help.readlines():
        help_lines.append(string.rstrip(line))
    s = curses.newwin(19, 77, 3, 1)
    s.box()
    num_lines = len(help_lines)
    end = 0
    while not end:
        for i in range(1,18):
            if i+offset < num_lines:
                line = string.ljust(help_lines[i+offset],74)[:74]
            else:
                line = " "*74
                end = 1
            if i<3 and offset>0: s.addstr(i, 2, line, curses.A_BOLD)
            else: s.addstr(i, 2, line, curses.A_NORMAL)
        s.refresh()
        c = s.getch()
        offset = offset+15
    s.erase()
    return CONTINUE

def file_func(args):
    #s = curses.newwin(5,10,10,20)
    #s = screen.derwin(10, 10, 1, 2)
    s = curses.newwin(5,10,10,20)
    s.box()
    s.addstr(1,2, "I", hotkey_attr)
    s.addstr(1,3, "nput", menu_attr)
    s.addstr(2,2, "O", hotkey_attr)
    s.addstr(2,3, "utput", menu_attr)
    s.addstr(3,2, "T", hotkey_attr)
    s.addstr(3,3, "ype", menu_attr)
    s.addstr(1,2, "", hotkey_attr)
    s.refresh()
    c = s.getch()
    if c in (ord('I'), ord('i'), curses.KEY_ENTER, 10):
        curses.echo()
        s.erase()
        screen.addstr(5,33, " "*43, curses.A_UNDERLINE)
        cfg_dict['source'] = screen.getstr(5,33)
        curses.noecho()
    elif c in (ord('O'), ord('o')):
        curses.echo()
        s.erase()
        screen.addstr(8,33, " "*43, curses.A_UNDERLINE)
        cfg_dict['target'] = screen.getstr(8,33)
        curses.noecho()
    elif c in (ord('T'), ord('t')):
        s.addstr(3,7, "->", menu_attr)
        s.refresh()
        s2 = curses.newwin(8,15,4,10)
        s2.box()
        s2.addstr(1,2, "H", hotkey_attr)
        s2.addstr(1,3, "TML", menu_attr)
        s2.addstr(2,2, "P", hotkey_attr)
        s2.addstr(2,3, "ython", menu_attr)
        s2.addstr(3,2, "F", hotkey_attr)
        s2.addstr(3,3, "AQ", menu_attr)
        s2.addstr(4,2, "S", hotkey_attr)
        s2.addstr(4,3, "mart_ASCII", menu_attr)
        s2.addstr(5,2, "R", hotkey_attr)
        s2.addstr(5,3, "aw", menu_attr)
        s2.addstr(6,2, "I", hotkey_attr)
        s2.addstr(6,3, "nfer Type", menu_attr)
        s2.addstr(6,2, "", hotkey_attr)
        s2.refresh()
        c = s2.getch()
        if c in (ord('I'), ord('i'), curses.KEY_ENTER, 10):
            cfg_dict['type'] = 'INFER'
        elif c in (ord('H'), ord('h')): cfg_dict['type'] = 'HTML'
        elif c in (ord('P'), ord('p')): cfg_dict['type'] = 'PYTHON'
        elif c in (ord('F'), ord('f')): cfg_dict['type'] = 'FAQ'
        elif c in (ord('S'), ord('s')): cfg_dict['type'] = 'SMART_ASCII'
        elif c in (ord('R'), ord('r')): cfg_dict['type'] = 'RAW'
        else: curses.beep()
        s2.erase()
        s.erase()
    else:
        curses.beep()
        s.erase()
    return CONTINUE

def doit_func(args=None):
    global counter
    counter = counter+1
    if cfg_dict['type'] == 'INFER':
        print "hello"
        #cfg_dict['type'] = dmTxt2Html.infer_type(cfg_dict['source'])
    #dmTxt2Html.main(cfg_dict)
    return CONTINUE

def proxy_func(args=None):
    s = curses.newwin(6, 15, 2, 8)
    s.box()
    s.addstr(1, 2, "P", hotkey_attr)
    s.addstr(1, 3, "roxy Bar", menu_attr)
    s.addstr(2, 2, "T", hotkey_attr)
    s.addstr(2, 3, "rap Links", menu_attr)
    s.addstr(3, 2, "A", hotkey_attr)
    s.addstr(3, 3, "ll Proxyes", menu_attr)
    s.addstr(4, 2, "N", hotkey_attr)
    s.addstr(4, 3, "o Proxies", menu_attr)
    s.addstr(4, 2, "", hotkey_attr)
    s.refresh()
    c = s.getch()
    s.erase()
    if c in (ord('N'), ord('n'), curses.KEY_ENTER, 10):
        cfg_dict['proxy'] = 'NONE'
    elif c in (ord('P'), ord('p')): cfg_dict['proxy'] = 'NAVIGATOR'
    elif c in (ord('T'), ord('t')): cfg_dict['proxy'] = 'TRAP_LINKS'
    elif c in (ord('A'), ord('a')): cfg_dict['proxy'] = 'ALL'
    else: curses.beep()
    return CONTINUE

#-- Display the currently selected options
def draw_dict():
    screen.addstr(5,33, " "*43, curses.A_NORMAL)
    screen.addstr(8,33, " "*43, curses.A_NORMAL)
    screen.addstr(11,33, " "*43, curses.A_NORMAL)
    screen.addstr(14,33, " "*43, curses.A_NORMAL)
    screen.addstr(5, 33, cfg_dict['source'], curses.A_STANDOUT)
    screen.addstr(8, 33, cfg_dict['target'], curses.A_STANDOUT)
    screen.addstr(11,33, cfg_dict['type'], curses.A_STANDOUT)
    screen.addstr(14,33, cfg_dict['proxy'], curses.A_STANDOUT)
    screen.addstr(17,33, str(counter), curses.A_STANDOUT)
    screen.refresh()


#-- Top level function call (everything except [curses] setup/cleanup)
def main(stdscr):
    # Frame the interface area at fixed VT100 size
    global screen
    bottom = curses.LINES
    sleft = curses.COLS
    hight = bottom - 10
    width = sleft - 20
    hstart = (bottom - hight) / 2
    lstart = (sleft - width) / 2
    screen = stdscr.subwin(hight, width, hstart, lstart)
    screen.box()
    screen.hline(2, 1, curses.ACS_HLINE, width - 2)
    screen.refresh()

    # Define the topbar menus
    file_menu = ("File", "file_func", ('asss', 'asdf'))
    proxy_menu = ("Proxy Mode", "proxy_func", None)
    doit_menu = ("Do It!", "doit_func", None)
    help_menu = ("Help", "help_func", None)
    exit_menu = ("Exit", "EXIT", 0)

    # Add the topbar menus to screen object
    topbar_menu((file_menu, proxy_menu, doit_menu, help_menu, exit_menu))

    # Draw the onscreen field titles
    screen.addstr(5, 4, "           Source of Input:", curses.A_BOLD)
    screen.addstr(8, 4, "        Output Destination:", curses.A_BOLD)
    screen.addstr(11, 4,"           Conversion Type:", curses.A_BOLD)
    screen.addstr(14, 4,"                Proxy Mode:", curses.A_BOLD)
    screen.addstr(17, 4,"Conversions during Session:", curses.A_BOLD)
    screen.addstr(1, 77, "", curses.A_STANDOUT)
    draw_dict()

    # Enter the topbar menu loop
    while topbar_key_handler():
        draw_dict()


if __name__=='__main__':
    try:
        # Initialize curses
        stdscr=curses.initscr()
        curses.start_color()
        # Turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho() ; curses.cbreak()

        # In keypad mode, escape sequences for special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.KEY_LEFT will be returned
        stdscr.keypad(1)
        main(stdscr)                    # Enter the main loop
        # Set everything back to normal
        stdscr.keypad(0)
        curses.echo() ; curses.nocbreak()
        curses.endwin()                 # Terminate curses
    except:
        # In the event of an error, restore the terminal
        # to a sane state.
        stdscr.keypad(0)
        curses.echo() ; curses.nocbreak()
        curses.endwin()
        traceback.print_exc()           # Print the exception

