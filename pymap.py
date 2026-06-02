#!/usr/bin/env python3
from curses import wrapper
from time import sleep
from pymap_classes import Tty, Splash, User, Mail, Unread, Inbox
#import re -- might want this at some point (regex module)

def main(stdscr):
    tty:Tty = Tty(stdscr)
    tty.size = stdscr.getmaxyx()
    splash:Splash = Splash(tty)
    splash.load_pos()
    # Curses - allows special escape keys
    stdscr.keypad(True)
    stdscr.clear()
    # Print the splash screen
    splash.print_splash()
    # Refresh the screen to show changes
    stdscr.refresh()
    mail:object = Mail(tty)
    unread:object = Unread(tty, mail)
    inbox:Inbox = Inbox(tty, mail)
    user:object = User(tty, mail, unread, inbox)
    user.init()
    try:
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
    stdscr.getch()
    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break

# Wrapper is from curses module; initializes window, colors, etc automatically
wrapper(main)
