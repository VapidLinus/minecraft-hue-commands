class HueCommand:
    """A command with a callback associated with a 3D coordinate."""
    def __init__(self, x, y, z, description, callback):
        self.x = x
        self.y = y
        self.z = z
        self.description = description
        self.callback = callback
    
    def try_match(self, bridge, x, y, z):
        """Checks if the supplied coordinate matches this command's coordinate.
        If it matches, the command's callback will be executed."""
        if self.x == x and self.y == y and self.z == z:
            self.callback(bridge)
            return True
        return False

class HueCommandController:
    """Controller for commands and callbacks.
    Commands and callbacks can be registered.
    An attempt can be made to execute all commands associated with a specific coordinate.
    When a command is executed, all callbacks will also be executed."""
    commands = []
    callbacks = []

    def __init__(self, bridge):
        self.bridge = bridge

    def register_callback(self, callback):
        """Registers a callback that will be executed when a command is executed."""
        self.callbacks.extend([callback])

    def register_command(self, command):
        """Registers a command."""
        self.commands.extend([command])

    def get_commands(self):
        """Returns a list of all registered commands."""
        return self.commands

    def execute_command(self, command):
        """Executes a command and executes all callbacks.
        The command must be registered in this controller's command list."""
        if command in self.commands:
            if command.try_match(self.bridge, command.x, command.y, command.z):
                for callback in self.callbacks: callback(command)
                return command
        return None

    def try_match(self, x, y, z):
        """Executes a command associated with the coordinate and executes all callbacks.
        Returns the command if one was executed, otherwise None.
        If more than one command is associated with the coordinate, only the first one that was registered will be executed."""
        for command in self.commands:
            if command.try_match(self.bridge, x, y, z):
                for callback in self.callbacks: callback(command)
                return command
        return None