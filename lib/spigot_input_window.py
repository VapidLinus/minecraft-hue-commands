from queue import Queue
from threading import Thread
from curses import *
from curses.ascii import *

class SpigotInputWindow:
    """Input window for Spigot.
    Lets the user type a command and then sends it to the server's stdin pipe."""
    input_text = ""

    def __init__(self, window, process):
        self.window = window
        self.process = process

        self.window.bkgd(' ', color_pair(2))
        self.window.scrollok(True)
        self.window.keypad(True)

        # Render window           
        self.header()

    def header(self):
        """Writes the info text and prints the user's current input text."""
        self.window.clear()
        self.window.addstr(0, 1, "Type to enter a command: ('stop' to exit)", A_REVERSE)
        self.window.addstr(1, 1, self.input_text)
        self.window.refresh()

    def update(self):
        """Updates the window."""
        # Don't freeze the terminal when looking for input
        self.window.nodelay(1)

        # Check for user input
        char = self.window.getch()
        if char is not ERR:
            # If the user hit enter
            if char in [KEY_ENTER, ord('\n')]:
                # Send the user's current input to the server's stdin pipe. Flush it to force it to be sent right away
                # Clear the user's input text
                self.process.stdin.write("{}\n".format(self.input_text).encode('ascii', 'ignore'))
                self.process.stdin.flush()
                self.input_text = ""
            # If the user hit backspace
            elif char in [KEY_BACKSPACE, ord('\b')]:
                # Remove the last character from the user's input
                self.input_text = self.input_text[:-1]
            # If the user entered a valid character
            elif isprint(char):
                # Add it to the input text
                self.input_text += chr(char)
            self.header()