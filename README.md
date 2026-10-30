# Description
This project contains a few games written in python, few other ones may be added if time allows.

# Getting Started
1. Clone the repository (https://www.github.com/pjedra96/python-games) to a directory of your choice.
2. Ensure you have a Python platform installed on your system, along with PIP - the Python package manager
3. Install all dependencies on your machine at the root of the repository clone, using `pip install -U -r requirements.txt`.
4. Execute `python py_snake.py` from the Command Prompt at the root of the clone, or `python py_2048.py` for the new game

# Game added (py-2048)
Slide the tiles with the arrow keys (or WASD). Two tiles with the same number merge into one when they touch. Reach the 2048 tile to win, then keep going if you like.

| Key | Action |
|---|---|
| Arrow keys / WASD | Slide the tiles |
| U | Undo the last move (one step) |
| R | New game |
| C | Keep going after reaching 2048 |
| Q | Quit |

The best score is saved in `bestscore.txt` next to the game.