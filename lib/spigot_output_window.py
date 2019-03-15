import queue
import re
from threading import Thread
from curses import *

class SpigotOutputWindow:
    """Output window for Spigot.
    Prints out the server's outpit from stdout and stderr.
    A callback can be registered which executes when a setblock command is detected from Minecraft."""
    set_block_callbacks = []

    def __init__(self, window, process):
        self.window = window
        self.output_queue = queue.Queue()

        self.window.scrollok(True)
        self.window.bkgd(' ', color_pair(1))

        # Look from output from the server in new threads.
        # This lets us read output without blocking the main thread.
        # Seperate threads are needed for stdout and stderr.

        # Listen to standard output
        t = Thread(target=self.enqueue_pipe_output, args=["", process.stdout, self.output_queue])
        t.daemon = True
        t.start()

        # Listen to error output
        t = Thread(target=self.enqueue_pipe_output, args=["Error: ", process.stderr, self.output_queue])
        t.daemon = True
        t.start()
    
    def register_set_block_callback(self, callback):
        """Registers a callback that will be executed when the setblock command is detected in Minecraft."""
        self.set_block_callbacks.extend([callback])

    def update(self):
        """Updates the window."""
        refresh = False
        try:
            # Look through each new line
            for name, line in iter(self.output_queue.get_nowait, None):
                # Write the outputted line to the window 
                self.window.addstr("{}{}".format(name, line))

                # Decode the outputted line and match it with the regex below.
                # The regex searches for the output string that is printed when the setblock command is used in a command block.
                # It also extracts the 3 coordinates that are also outputted in the outputted line.
                line = line.decode('ascii')
                match = re.search(".*\[@: Changed the block at (\-*\d{1,10}), (\-*\d{1,10}), (\-*\d{1,10})]", line)
                if match:
                    # Get the three extracted coordinates
                    x = int(match.group(1))
                    y = int(match.group(2))
                    z = int(match.group(3))
                    # Log that we detected the setblock command
                    self.window.addstr("Found set block at {}, {}, {}\n".format(x, y, z), color_pair(3))
                    # Execute all callbacks
                    for callback in self.set_block_callbacks:
                        callback(x, y, z)
                
                refresh = True
        except queue.Empty:
            pass

        # If any new lines were outputted, refresh the window
        if refresh:
            self.window.refresh() 
        
    def enqueue_pipe_output(self, name, pipe, queue):
        """Puts the name and output from a pipe into the queue."""
        try:
            with pipe:
                for line in iter(pipe.readline, b''):
                    queue.put((name, line))
        finally:
            queue.put(None)
                