#!/usr/bin/env python3
from __future__ import annotations
from typing import Any,Literal
from os import path, getenv, mkdir, remove
from curses import use_default_colors, init_pair, window, echo, noecho, curs_set, color_pair as color
#from curses import COLOR_BLACK as black
from curses import COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_YELLOW, COLOR_MAGENTA
from imaplib import IMAP4_SSL as imap
import socket
from time import sleep

class Tty:
    def __init__(self, stdscr:window):
        self.stdscr:window = stdscr
        self.size:tuple[int, int] = self.stdscr.getmaxyx()
        self.center:list[int] = [self.size[0] // 2, self.size[1] // 2]
        self.current_pos:list[int] = []
        self.prev_pos:list[int]
        self.start_pos:list[int]
        use_default_colors()
        #             fg, bg
        init_pair(1, COLOR_RED, -1)
        self.redfg:int = 1
        init_pair(2, COLOR_GREEN, -1)
        self.greenfg:int = 2
        init_pair(3, COLOR_YELLOW, -1)
        self.yellowfg:int = 3
        init_pair(4, COLOR_BLUE, -1)
        self.bluefg:int = 4
        init_pair(5, COLOR_MAGENTA, -1)
        self.magentafg:int = 5
        init_pair(6, -1, COLOR_BLUE)
        self.bluebg:int = 6

    def intro_print(self, text:str|bytes, colorval:int) -> None:
        self.stdscr.addstr(self.current_pos[0], self.start_pos[1], f'{text}', color(colorval))
        self.current_pos[0]+=1
        self.stdscr.refresh()

class Splash:
    def __init__(self, tty:Tty):
        self.tty:Tty = tty
        self.message:list[list[str]] = [
            [
                '███████╗ ',
                '██║  ██║ ',
                '███████╝ ',
                '██║      ',
                '██╝      '],
            [
                '██╗   ██╗ ',
                ' ██╗ ██╔╝ ',
                '  ████╔╝  ',
                '   ██╔╝   ',
                '   ██╝    '],
            [
                '██   ██╗ ',
                '███ ███║ ',
                '██║█ ██║ ',
                '██║  ██║ ',
                '██╝  ██╝ '],
            [
                ' █████╗ ',
                '██║  ██ ',
                '███████ ',
                '██║  ██ ',
                '██╝  ██ '],
            [
                '███████╗ ',
                '██║  ██║ ',
                '███████╝ ',
                '██║      ',
                '██╝      ',]
        ]
        self.rows:int
        self.columns:int
        self.msg_center:list[int]

    def load_pos(self) -> None:
        self.rows = len(self.message[0])
        self.columns =  len(max((c for _, row in enumerate(self.message) for c in row))) \
            * len(self.message)
        self.msg_center = [(self.rows // 2), (self.columns // 2)]
        self.tty.start_pos = [self.msg_center[0], (self.tty.center[1] - self.msg_center[1])]
        self.tty.current_pos = [self.tty.start_pos[0], self.tty.start_pos[1]]

    def print_splash(self) -> None:
        # Print splash message loop
        for i in range(self.rows):
            # At beginning of every outer loop, reset horizontal cursor position
            self.tty.current_pos[1] = self.tty.start_pos[1]
            # Match column with desired color for the letter
            # Every line is printed left-to-right, so increment self.current_pos[1]
            # by len of index that was just printed each time, to reposition cursor
            # for the next column
            for j in range(len(self.message)):
                match j:
                    case 0:
                        self.tty.stdscr.addstr(self.tty.current_pos[0], self.tty.current_pos[1],\
                            self.message[j][i], color(self.tty.redfg))
                        self.tty.current_pos[1]+=len(self.message[j][i])
                    case 1:
                        self.tty.stdscr.addstr(self.tty.current_pos[0], self.tty.current_pos[1],\
                            self.message[j][i], color(self.tty.greenfg))
                        self.tty.current_pos[1]+=len(self.message[j][i])
                    case 2:
                        self.tty.stdscr.addstr(self.tty.current_pos[0], self.tty.current_pos[1],\
                            self.message[j][i], color(self.tty.yellowfg))
                        self.tty.current_pos[1]+=len(self.message[j][i])
                    case 3:
                        self.tty.stdscr.addstr(self.tty.current_pos[0], self.tty.current_pos[1],\
                            self.message[j][i], color(self.tty.bluefg))
                        self.tty.current_pos[1]+=len(self.message[j][i])
                    case 4:
                        self.tty.stdscr.addstr(self.tty.current_pos[0], self.tty.current_pos[1],\
                            self.message[j][i], color(self.tty.magentafg))
                        self.tty.current_pos[1]+=len(self.message[j][i])
                    case _:
                        pass
            # After inner loop completes, move forward one row then continue
            self.tty.current_pos[0]+=1

class Mail:
    def __init__(self, tty:Tty):
        self.tty:Tty = tty
        self.hostname:str
        self.port:int = 993
        self.server:imap
        self.command:str
        self.response:tuple[str, Any]

class Unread:
    def __init__(self, tty:Tty, mail:Mail):
        self.tty:Tty = tty
        self.mail:Mail = mail
        self.ids:list[int]
        self.headers:dict[str,str]
        self.win:window
        self.winsize:list[int]
        self.current_pos:list[int]

    def get_ids(self):
        # Call IMAP imap to get list of unread message ids
        self.mail.command = 'unseen'
        try:
            self.mail.response = self.mail.server.search(None, self.mail.command)
        except self.mail.server.error:
            raise
        else:
            if self.mail.response[0] == 'OK':
                # Response is in tuple index 1 as a single indexed byte list
                # and space-separated
                self.ids = self.mail.response[1][0].decode().split(' ')

    def get_headers(self):
        try:
            # IMAP fetch command requires ids to be comma-separated
            ids_str:str = str.join(',', (f'{i}' for i in self.ids))
            # Argument to give IMAP fetch for section (use body.peek to avoid marking as read)
            section:str = 'body.peek[header.fields (from subject)]'
            self.mail.response = self.mail.server.fetch(ids_str, section)
        except imap.error:
            raise
        else:
            # Populate headers dict with decoded, key = id, value = line-separated
            for i in self.ids:
                # response[1][n][0] begins with ID number
                for id in (header for header in self.mail.response[1]):
                    # Avoid errors by type checking
                    if type(id[0]) is bytes and id[0].decode().startswith(str(i)):
                        # bytes to str, rm trailing whitespace, split on \n
                        # provides two indexes containing: From and Subject
                        self.headers[str(i)] =  id[1].decode().rstrip().splitlines()

    def print(self):
        # Clears the screen and prints all dict values from self.headers
        _ = curs_set(0)
        # Initialize new window
        self.tty.stdscr.clear()
        self.current_pos = [1, 1]
        self.winsize = list(self.tty.size)
        self.winsize[0] -= 2
        self.winsize[1] -= 1
        self.win = self.tty.stdscr.derwin(*self.winsize, *self.current_pos)
        self.win.overwrite(self.tty.stdscr)
        self.win.erase()
        # WIP
        for message in self.headers.values():
            self.win.addstr(*self.current_pos, message[0], color(self.tty.redfg))  # pyright: ignore[reportCallIssue]
            self.current_pos[0]+=1
            self.win.addstr(*self.current_pos, message[1], color(self.tty.yellowfg))  # pyright: ignore[reportCallIssue]
            self.current_pos[0]+=1
        self.win.refresh()

class Inbox:
    def __init__(self, tty:Tty, mail:Mail):
        self.tty:Tty = tty
        self.mail:Mail = mail
        self.ids:list[int]

#class marked:
#    ...

class User:
    def __init__(self, tty:Tty, mail:Mail, unread:Unread, inbox:Inbox):
        self.tty:Tty = tty
        self.mail:Mail = mail
        self.unread:Unread = unread
        self.inbox:Inbox = inbox
        self.home:str|None = getenv('HOME')
        self.cfg_dir:str = '.config/pymail'
        self.cfg_path:str = path.join(self.home, self.cfg_dir) 
        self.cfg_email:str = path.join(self.cfg_path, '.email')
        self.cfg_pass:str = path.join(self.cfg_path, '.pass')
        self.cfg_token:str = path.join(self.cfg_path, '.token')
        self.email:str
        self.emailenc:bytes
        self.password:str
        self.passenc:bytes
        self.token:bytes

    def init(self) -> None:
        self.check_path()

    def check_path(self) -> None:
        # Check if user has saved credentials
        if path.exists(self.cfg_path):
            self.tty.intro_print('Pymail directory found. Checking for stored credentials', 0)
            # If files found, attempt to decrypt
            if path.exists(self.cfg_email) and path.exists(self.cfg_pass) and path.exists(self.cfg_token):
                if self.handle_decryption():
                    self.define_host()
                    self.imap_connect()
                    self.login()
                # On fail, delete files, request new login
                else:
                    remove(self.cfg_email)
                    remove(self.cfg_pass)
                    remove(self.cfg_token)
                    self.get_login_creds()
        else:
            mkdir(self.cfg_path)
            self.tty.intro_print(f'Created {self.cfg_path}', 0)
            self.get_login_creds()

    def get_login_creds(self) -> None:
        # Get email and password from user
        self.tty.intro_print('Email: ', 0)
        echo()
        self.email = self.tty.stdscr.getstr().decode()
        _ = curs_set(0)
        self.tty.intro_print('Password: ', 0)
        noecho()
        _ = curs_set(1)
        self.password = self.tty.stdscr.getstr().decode()
        _ = curs_set(0)
        self.define_host()
        self.imap_connect()
        # If successful connection, ask user if they want to save login information
        if self.ask_to_store():
            if self.handle_encryption():
                self.login()
            else:
                self.tty.intro_print('Credentials will not be saved. Continuing to login', 3)
                self.login()

    def define_host(self) -> None:
        # Callable to set imap hostname and port number
        # From fresh login or restored creds
        self.mail.hostname = f'imap.{self.email[self.email.find('@')+1:]}'

    # Setup connection to IMAP imap
    def imap_connect(self) -> None:
        try:
            self.tty.intro_print(f'Attempting to connect to {self.mail.hostname} on port {self.mail.port}', 0)
            self.mail.server = imap(self.mail.hostname, self.mail.port)
        except socket.error as e:
            self.tty.intro_print(f'{e.strerror}', 1)
            self.tty.intro_print('Exiting', 0)
            sleep(3)
            exit()

        self.tty.intro_print('Connected', 0)

    def ask_to_store(self) -> bool|None:
        # Ask user if they want to store locally - requires cryptography module
        self.tty.intro_print('Store credentials? Requires cryptography module. (y/n): ', 0)
        _ = curs_set(1)
        echo()
        user_response:str = self.tty.stdscr.getstr().decode()
        _ = curs_set(0)
        noecho()
        if user_response == 'n':
            self.tty.intro_print('Continuing without storing credentials', 0)
            return False
        elif user_response == 'y':
            return True
        else:
            self.tty.intro_print('Invalid entry', 3)
            # Recursive call to request again
            _ = self.ask_to_store()

    def handle_decryption(self) -> bool:
        if self.get_encrypted() and self.decrypt():
            return True
        else:
            return False

    def get_encrypted(self) -> bool:
        # Open token, password, and email encrypted files
        try:
            with open(f'{self.cfg_token}', 'r') as t:
                self.token = t.read().encode()
        except OSError as e:
            self.tty.intro_print(f'{e.strerror}', 1)
            self.tty.intro_print('Failed to retrieve token for decryption', 1)
            self.tty.intro_print('Please login again', 0)
            return False
        else:
            try:
                with open(f'{self.cfg_pass}','r') as p:
                    self.passenc = p.read().encode()
            except OSError as e:
                self.tty.intro_print(f'{e.strerror}', 1)
                self.tty.intro_print('Failed to retrieve password for decryption', 1)
                self.tty.intro_print('Please login again', 0)
                return False
            else:
                try:
                    with open(f'{self.cfg_email}', 'r') as m:
                        self.emailenc = m.read().encode()
                except OSError as e:
                    self.tty.intro_print(f'{e.strerror}', 1)
                    self.tty.intro_print('Failed to retrieve email for decryption', 1)
                    self.tty.intro_print('Please login again', 0)
                    return False
            return True

    def decrypt(self) -> bool:
        # After self.emailenc and self.passenc have been loaded
        # Use Fernet to decrypt and store in self.password and self.email
        from cryptography.fernet import Fernet
        fernet:object = Fernet(self.token)
        self.password = fernet.decrypt(self.passenc).decode()
        self.email = fernet.decrypt(self.emailenc).decode()
        return True

    def handle_encryption(self) -> bool:
        if self.encrypt() and self.store_encrypted_creds():
            return True
        else:
            return False

    def encrypt(self) -> bytes|bool:
        from cryptography.fernet import Fernet
        self.token = Fernet.generate_key()
        fernet = Fernet(self.token) # IMPORTANT: this key needs to be saved in order to decrypt
        self.emailenc = fernet.encrypt(self.email.encode())
        self.passenc = fernet.encrypt(self.password.encode())
        if self.store_encrypted_creds():
            return True
        else:
            return False

    def store_encrypted_creds(self) -> bool:
        # Write the encrypted credentials to system
        # Try/except for each to ensure token, email, and password
        # are all properly saved
        try:
            with open(f'{self.cfg_token}', 'w') as t:
                _ = t.write(self.token.decode())
        except OSError as e:
            self.tty.intro_print(f'{e.strerror}', 1)
            return False
        else:
            try:
                with open(f'{self.cfg_email}', 'w') as mail:
                    _ = mail.write(self.emailenc.decode())
            except OSError as e:
                self.tty.intro_print(f'{e.strerror}', 1)
                return False
            else:
                try:
                    with open(f'{self.cfg_pass}', 'w') as pw:
                        _ = pw.write(self.passenc.decode())
                except OSError as e:
                    self.tty.intro_print(f'{e.strerror}', 1)
                    return False
                else:
                    self.tty.intro_print(f'Credentials stored in {self.home}/{self.cfg_dir}', 0)
                    return True

    def login(self) -> None:
        response:tuple[Any, list[bytes | None]] = self.mail.server.login(self.email, self.password)
        if response[0] == 'OK':
            self.tty.intro_print('Successfully logged in', 0)
        else:
            self.tty.intro_print('Failed to login', 0)

        self.tty.intro_print('Selecting inbox...', 0)
        response = self.mail.server.select()
        if response[0] == 'OK':
            self.tty.intro_print('Opened inbox', 0)
        else:
            self.tty.intro_print('Failed to open inbox', 0)

    def get_unread_ids(self):
        return
