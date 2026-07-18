#!/usr/bin/env python3
from curses import wrapper, window
<<<<<<< HEAD
<<<<<<< HEAD
from classes import Tty, Splash, User, Mail, App


def main(stdscr: window) -> None:
    tty: Tty = Tty(stdscr)
=======
=======
>>>>>>> c2892da (rebase local changes on main)
from time import sleep
from pymap_classes import Tty, Splash, User, Mail, Unread, Inbox
#import re -- might want this at some point (regex module)

def main(stdscr:window):
    tty:Tty = Tty(stdscr)
<<<<<<< HEAD
>>>>>>> 2db2a01 (WIP)
=======
=======
from classes import Tty, Splash, User, Mail, App


def main(stdscr: window) -> None:
    tty: Tty = Tty(stdscr)
>>>>>>> 3815c75 (WIP)
>>>>>>> c2892da (rebase local changes on main)
    tty.size = stdscr.getmaxyx()
    splash: Splash = Splash(tty)
    splash.load_pos()
    # Curses - allows special escape keys
    stdscr.keypad(True)
    stdscr.clear()
    # Print the splash screen
    splash.print_splash()
    # Refresh the screen to show changes
    stdscr.refresh()
<<<<<<< HEAD
<<<<<<< HEAD
    mail: Mail = Mail(tty)
    user: User = User(tty, mail)
=======
=======
>>>>>>> c2892da (rebase local changes on main)
    mail:object = Mail(tty)
    unread:object = Unread(tty, mail)
    inbox:Inbox = Inbox(tty, mail)
    user:User = User(tty, mail, unread, inbox)
<<<<<<< HEAD
>>>>>>> 2db2a01 (WIP)
=======
=======
    mail: Mail = Mail(tty)
    user: User = User(tty, mail)
>>>>>>> 3815c75 (WIP)
>>>>>>> c2892da (rebase local changes on main)
    user.init()
    app: App = App(tty, mail)
    app.run()
    try:
<<<<<<< HEAD
<<<<<<< HEAD
        mail.server.logout()
    except Exception:
        pass
=======
=======
>>>>>>> c2892da (rebase local changes on main)
        unread.get_ids()
    except mail.server.error:
        tty.intro_print('Error retrieving unread message ids', 1)
        tty.intro_print('Exiting', 1)
        sleep(2)
        exit()
    try:
        unread.get_headers()
    except mail.server.error:
        tty.intro_print('Error fetching unread messages', 1)
        tty.intro_print('Exiting', 1)
        sleep(2)
        exit()
    unread.print()
    # Placeholder for testing to keep program alive
    _ = stdscr.getch()
    while True:
        key:int = stdscr.getch()
        match key:
            case ord("q"):
                break
            case _:
                pass
=======
        mail.server.logout()
    except Exception:
        pass
<<<<<<< HEAD

>>>>>>> 3815c75 (WIP)

<<<<<<< HEAD
>>>>>>> 2db2a01 (WIP)
=======
=======
>>>>>>> 96ba07e (Add local fuzzy search with live-updating Search tab)
>>>>>>> 213f8dd (Add R keybind to refresh all tabs simultaneously)
# Wrapper is from curses module; initializes window, colors, etc automatically
wrapper(main)
