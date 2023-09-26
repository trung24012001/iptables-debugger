import os
import platform

if platform.system() != "Linux":
    exit("Only supported on Linux.")

if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.")
