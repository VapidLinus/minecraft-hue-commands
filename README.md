# minecraft-hue-commands
This script starts a Minecraft server as a subprocess. It uses curses to create an output and input window for the server to let it operate normally. /setblock commands in command blocks are detected and can be used to trigger commands that sends commands to Hue lights.

This project is not intended to work as is, but can instead be used for reference. A Minecraft/Spigot server needs to be downloaded and compiled. Additional configuration in script.py is required. This is my first time ever using Python though, so there's likely tons of bad code and bad practices. Use with care :)

The code implies that the server must be a Spigot server. This is not true and it should work just the same for a regular Minecraft server. I just haven't had time to rename the classes and menu options to reflect this.

Depends on the standard Python 3.x libraries, as well as:
https://github.com/studioimaginaire/phue
