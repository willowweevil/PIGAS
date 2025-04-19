# PIGAS
## Personal In-Game Adventure Sidekick
### v0.3.0

### Before you started
PIGAS allows you to get your second-hand companion in World of Warcraft video game.
It is **NECESSARY** to have a second account (_In-Game Companion_) that will run simultaneously with your main account (_Player_) on the second computer or virtual machine!
Your companion is just another player tied to you!

**Some useful notes:**
- This version of PIGAS could work only with Windows and Ubuntu (only with Xorg window manager).
- PIGAS 100% works with *Wrath of the Lich-King (3.3.5a)* and *Cataclysm (4.3.4)* expansions. Workability with other extensions didn't test yet.
- Recommended to use range-attack classes for a companion with healing and supporting spells (priest or druid are the best in this case).

### How to start
#### In-Game Companion
1. Install World of Warcraft to the second PC or virtual machine. In this case, you could use the VirtualBox to install Windows or Ubuntu (only with Xorg window manager) operating systems.
2. If you are using `Ubuntu` install `xdotool` via `sudo apt install xdotool`.
3. Rename `template.config.yaml` to `config.yaml`; `template.context.yaml` to `context.txt`.
4. Fill all fields in `config.yaml`.
5. Run `pigas.exe` to begin program initialization. It will copy `Config.wtf` and Addon to game directory.
6. Set initial skills and rotation in `data\class\YOUR_EXPANSION\COMPANION_CLASS` (see below for the part __How to set skills/rotations__).
7. Enter the game as your companion.
8. Run `pigas.exe`

#### Player
1. Copy file `data\macros\macros-cache.txt` to `GAME_DIRECTORY\WTF\Account\YOUR_ACCOUNT\macros-cache.txt`. It contains all commands to control your companion.
2. Send a party invite to your companion.

### How to set skills/rotations

### How to play

Companion get commands from your player (they should be in party).
