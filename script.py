# My imports
from lib.spigot_output_window import SpigotOutputWindow
from lib.spigot_input_window import SpigotInputWindow
from lib.hue_command_controller import HueCommandController
from lib.hue_commands import register_hue_commands
from lib.ui_util import ui_multichoice
from lib.ui_util import ui_popup
from lib.ui_util import ui_message

# Third party imports
from subprocess import Popen
from subprocess import PIPE
from phue import Bridge
from phue import PhueException
from curses import *
import curses

# Settings
hue_ip = "192.168.1.78"
hue_config = "/home/pi/Modul4/.python_hue"
spigot_path = r"/home/pi/Modul4/spigot/"
spigot_jar_path = "/home/pi/Modul4/spigot/spigot-1.13.2.jar"
start_spigot_command = ["sudo", "java", "-Xms512M", "-Xmx1008M", "-jar", spigot_jar_path, "nogui"]

# Variables
hue_command_contoller = None

def main(stdscr): 
    # Prepare colours for curses
    init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
    init_pair(5, curses.COLOR_RED, curses.COLOR_WHITE)

    # Overflow instead of crash when text is too large
    stdscr.scrollok(1)

    # Keep showing the Main Menu until it return False (exit)
    while display_main_menu(stdscr):
        pass

def display_main_menu(stdscr):
    """Displays a menu and lets the user choose which task to select.
    The main menu will keep displaying after a task is finished until
    the user selects the Exit option."""
    choice = ui_multichoice(
        stdscr,
        "Select an option:",
        ["Start Spigot",            # 0
        "Start Command Simulator",  # 1
        "Connect Hue Bridge",       # 2
        "Exit"])                    # 3

    # Start spigot
    if choice is 0:
        start_spigot(stdscr)
    # Start hue simulator
    elif choice is 1:
        start_command_simulator(stdscr)
    # Connect hue
    elif choice is 2:
        connect_bridge(stdscr)
    # Exit
    elif choice is 3:
        return False # Don't show the main menu again
    
    # Show the main menu again
    return True

def start_spigot(stdscr):
    """Starts the Spigot server.
    The server will keep running until the user writes 'stop' or the server crashes.
    Supplies a custom output and input window to view the server's log and to
    supply user-entered commands to the server.
    Registers a callback for when the 'setblock' command is used in a command block
    in Minecraft and tries to match its coordinates with one of the hue commands."""
    # This method is used below as a callback for the output window when
    # it detects the setblock command in Minecraft.
    def on_set_block(x, y, z):
        """Tries to execute the command associated with the specified coordinates."""
        command = get_hue_command_controller().try_match(x, y, z)

        # If a command was executed
        if command is not None:
            # Log which command we executed
            output_window.addstr("Hue Command:", color_pair(5))
            output_window.addstr(" {}\n".format(command.description))

    # It can take a few seconds for Spigot to start,
    # so we show a message to let the user know we're starting Spigot.
    ui_message(stdscr, "Starting Spigot", ["Please wait..."])
    stdscr.refresh()

    # Start spigot as subprocess.
    # Redirecting stdin, stdout, and stderr to the PIPE,
    # this stops the process from trying to recieve input or send output to the terminal.
    # Instead, we will below create our own output and input windows to control the server.

    spigot = Popen(start_spigot_command, cwd=spigot_path, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

    # Create output window
    # This window will show the server's output
    output_window = newwin(curses.LINES - 3, curses.COLS)
    spigot_output_window = SpigotOutputWindow(output_window, spigot)
    spigot_output_window.register_set_block_callback(on_set_block) # Listen to setblock commands
    
    # Create input window
    # This window is used to send input to the server
    input_window = newwin(3, curses.COLS, curses.LINES - 3, 0)
    spigot_input_window = SpigotInputWindow(input_window, spigot)

    # Keep updating the windows until Spigot is terminated
    while spigot.poll() is None:
        spigot_output_window.update()
        spigot_input_window.update()

def start_command_simulator(stdscr):
    """Starts the command simulator.
    Will fail and return if couldn't connect to the Hue Bridge.
    
    Shows a list of categories to the user (z coordinates of commands).
    When a category is selected, show a list of all commands in that category.
    When a command in a category is selected, execute the command."""
    hcc = None
    
    # Get or ceate the command controller which is conncted to the Hue Bridge
    # Return if we couldn't to the bridge
    try:
        hcc = get_hue_command_controller()
    except (OSError, PhueException) as e:
        ui_popup(stdscr,
            "Failed to start Command Simulator",
            [str(e)])
        return

    # Find all the different categories (z coordinate)
    categories = []
    for command in hcc.get_commands():
        if command.z not in categories:
            categories.extend([command.z])
    # Add an exit option
    categories.extend(["Exit"])
    
    # Select category
    while True:
        choice = ui_multichoice(stdscr, "Select category:", [str(c) for c in categories])

        # Select command
        if choice in range(0, len(categories) - 1):
            category = categories[choice]

            while True:
                # Find all commands in the selected category
                # Select the command's description
                commands = [command for command in hcc.get_commands() if command.z is category]
                command_descriptions = [command.description for command in commands]
                # Add a back option
                command_descriptions.extend(["Back"])
                
                choice = ui_multichoice(stdscr, "Select a command:", command_descriptions) 

                # Execute the selected command
                if choice in range(0, len(commands)):
                    flash()
                    hcc.execute_command(commands[choice])
                # Break to the category menu if the back option was seleced
                else:
                    break
        # Return if the exit option was selected 
        else:
            return

    

def connect_bridge(stdscr):
    """Prompts the user to press the link button on the Hue Bridge and then attempts to connect."""
    choice = ui_multichoice(stdscr, "Press the link button on your Hue Bridge and then continue", ["Continue", "Cancel"])

    # Return if user selected cancel
    if choice is 1:
        return

    # Try to connect to hue bridge
    try:
        hue = Bridge(ip=hue_ip, config_file_path=hue_config)
        hue.get_api() # will throw exception if there is a connection error
        ui_popup(stdscr, "Success!", ["Connected to Hue bridge."])
    except (OSError, PhueException) as e:
        ui_popup(stdscr,
            "Failed to connect to Hue bridge",
            [str(e)])

def get_hue_command_controller():
    """
    Gets or creates a hue command controller.
    If one was created previously, the cached one will be returned.
    """
    global hue_command_contoller

    # Return cached instance if it exists
    if hue_command_contoller is not None:
        return hue_command_contoller
    
    # Create the new instance and supply it with a connection to the bridge
    # Register the hue commands to the controller
    hue_command_contoller = HueCommandController(Bridge(ip=hue_ip, config_file_path=hue_config))
    register_hue_commands(hue_command_contoller)
    return hue_command_contoller

# Launch the curses main wrapper and quit when finished
wrapper(main)
quit()