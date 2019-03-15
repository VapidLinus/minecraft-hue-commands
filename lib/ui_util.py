from curses import *
from curses.ascii import *
import curses

def ui_multichoice(stdscr, title, choices):
    """Displays the titles and lists all the choices to the user.
    Returns the index of the choice that was selected."""
    # Add choice index to start of every choice string
    choices = ["{}) {}".format(i + 1, choice) for i, choice in enumerate(choices)]

    # Display the title and choices
    ui_message(stdscr, title, choices)
    
    # Make user select a choice
    while True:
        char = stdscr.getch()
        if not isdigit(char):
            continue
        choice_index = int(chr(char)) - 1
        if not choice_index in range(0, len(choices)):
            continue
        return choice_index

def ui_popup(stdscr, title, subtitles):
    """Shows a popup with a title and one or moresubtitles and waits for the user to press a key before continuing."""
    subtitles.extend(["Press any key to continue."])
    ui_message(stdscr, title, subtitles)
    stdscr.getch()

def ui_message(stdscr, title, subtitles):
    """Shows a message with a title and one or more subtitles."""
    # Hide output and cursor
    stdscr.clear()
    noecho()
    curs_set(0)

    # Find the length of the longest sentence
    longest_sentence = len(title)
    for subtitle in subtitles:
        length = len(subtitle)
        if length > longest_sentence:
            longest_sentence = length

    # Calculate starting positions to be in the center of the screen
    start_x = curses.COLS // 2 - longest_sentence // 2
    start_y = curses.LINES // 2 - len(subtitles) // 2

    # Print title and subtitles
    stdscr.addstr(start_y, start_x, title, color_pair(4))
    for i, subtitle in enumerate(subtitles):
        stdscr.addstr(start_y + i + 1, start_x, subtitle)