# PIGAS
## Personal In-Game Adventure Sidekick
### v0.5.0

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
   - If you are using `Ubuntu` install `xdotool` via `sudo apt install xdotool`.
   - If you are using `Windows` on `MacOS` via `Parallels` please, be sure to set `Scaled` resolution mode in `Configure-Hardware-Graphics` menu and set correct resolution in `Windows` (e.g., `1920x1200`). 
2. Rename `template.config.yaml` to `config.yaml`; `template.context.txt` to `context.txt`.
3. Fill all fields in `config.yaml`.
4. Run `pigas.exe` to begin program initialization. It will copy `Config.wtf` and Addon to game directory.
5. Set initial skills and rotation in `data\class\GAME_EXPANSION\COMPANION_CLASS` (see below for the part __How to set skills/rotations__).
6. Enter the game as your companion.
7. Run `pigas.exe`

#### Player
1. Copy file `data\macros\macros-cache.txt` to `GAME_DIRECTORY\WTF\Account\YOUR_ACCOUNT\macros-cache.txt`. It contains all commands to control your companion.
2. Send a party invite to your companion.

### How to set skills/rotations
In `data\class\GAME_EXPANSION\COMPANION_CLASS` you will find some examples of spellbook and rotations. 
To use your companion spells, you should:
1. Add the necessary and known by you companion spells in `spellbook.yaml`. Spell should be placed on the action bar in the game.  In `spellbook.yaml` you should fill the button on spell in keyboard, spell name, cast time, cooldown (for time spells it should be their action time) and action bar number.
2. Fill the rotations in `rotations.yaml`. For combat rotation, you could add support spells (like Power Word: Shield) and target for them ('Player' or 'Player Pet'). 'Attack Target Is Target Of' field means the target to attack (e.g., player's target).
3. For this version of PIGAS, buffing spells will be used at the start.
### How to play

Companion get commands from your player (player and companion should be in one party).
Companion recognize these commands:
- `#stay` to stay in one place;
- `#follow` to follow by player;
- `#assist` - to help player in combat;
- `#defend` - to defend yourself and player;
- `#only-heal` - to use only heal spells;
- `#passive` - to do nothing in combat;
- `#mount` - to mount (spell `Mount` should be in `spellbook`);
- `#dismount` - to dismount;
- `#loot` - to move on player position and try to loot something;
- `#movement-speed` - to change movement speed (run/walk);
- `#pause` - paused PIGAS;
- `#disable` - to disable PIGAS.

You could send some emotions to a companion (`Let's /dance!`) or commands (e.g., `&/cast 0 1` or `&.server info`).
To add some text to your context use `%Now we are in the Orgrimmar.`

### Some extra config parameters
Some extra parameters are supported in `config.yaml`:
1. Debug
    ```
    other:
      debug: true
    ```
2. Open-AI
    ```
    open-ai:
      base_url:  # api url
      api_key:  # api key
    ```
3. Distances fix
    ```
    navigation:
        distance_to_player_delta: 0.15
        mounted_distance_coefficient: 1.25
        looting_distance_coefficient: 0.5
        start_to_avoid_obstacles_distance_coefficient: 3.0
        start_to_wait_player_distance_coefficient: 50.0
    ```