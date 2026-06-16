#!/usr/bin/env python3
from curses import wrapper, window
from classes import Tty, Splash, User, Mail, App


def main(stdscr: window) -> None:
    tty: Tty = Tty(stdscr)
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
    mail: Mail = Mail(tty)
    user: User = User(tty, mail)
    user.init()
    app: App = App(tty, mail)
    app.run()
    try:
        mail.server.logout()
    except Exception:
        pass


# Wrapper is from curses module; initializes window, colors, etc automatically
wrapper(main)
