# PIGAS
## Personal In-Game Adventure Sidekick
### Version: 0.5.0

---

### Overview
**PIGAS** is your **Personal In-Game Adventure Sidekick**, designed to enhance your experience in *World of Warcraft*. It allows you to set up a second-hand companion that can assist you in quests, battles, and other adventures.

### Key Requirements
- **Two Accounts**: You must have a second account (_Companion_) running alongside your main account (_Player_).
- **Dual System Setup**: Your Companion account must run on a separate PC or virtual machine (VM).
- The companion acts as another player, fully synchronized and controlled!

---

### Compatibility
- Supported systems: **Windows** and **Ubuntu** (limited to Xorg window manager).  
- Tested with *Wrath of the Lich King (3.3.5a)* and *Cataclysm (4.3.4)* expansions. Other expansions remain untested but may be compatible.
- Recommended companion classes: Ranged attackers with healing and support capabilities (e.g., Priest, Druid, Shaman).

---

## How to Get Started

### 1. Prepare the Environment
1. **Install World of Warcraft**:
   - For **Windows** install the game on a second PC or virtual machine (VirtualBox, Hyper-V).
   - If using **Ubuntu**, install `xdotool`:
     ```bash
     sudo apt install xdotool
     ```
   - **MacOS users with Parallels**:
     - Set the resolution mode to **Scaled** in the `Configure > Hardware > Graphics` menu.
     - Ensure your Windows resolution is more than `1600x900` (`1920x1200` or `1920x1080` work quite well).

2. **Rename Configuration Files**:
   - Rename the following template files:
     - `tmp.config.yaml` → `config.yaml`
     - `tmp.context.txt` → `context.txt`
     - `tmp.open-ai.yaml` → `open-ai.yaml`

3. **Edit `config.yaml`**:
   - Fill in all required fields. You can reference the example file located at `data/example/config.yaml`.

4. **Run PIGAS**:
   - Launch `pigas.exe` to initialize the program. It will also copy configs and the necessary addon to the game directory.

---

### 2. Set Up Skills and Rotations
- Configure your companion's **spells and rotations** by following these steps:

1. **Add Spells**:
   - Navigate to `data/class/GAME_EXPANSION/COMPANION_CLASS/`.
   - Update `spellbook.yaml` with your companion's spells:
     - Include key bindings, spell names, cast times, cooldowns (or action time for time-range spells), 
     and the action bar numbers where they are placed in the game (please check `data/example/spells_and_rotations`).

2. **Define Rotations**:
   - Edit `rotations.yaml` to specify combat rotations, including:
     - Support spells: e.g., *Power Word: Shield*.
     - Targets: e.g., `Player` or `Player Pet`.
     - Specify the attack target using the field: `Attack Target Is Target Of` (e.g., `Player` means: should attack the player’s target).

3. **Buffing Spells**:
   - Buffing spells are used automatically at the start of a session.

---

### 3. Launch & Play
1. Log in to the game on your **Companion** account.
2. Send a party invite from your **Player** character to your **Companion**.
3. Start `pigas.exe` on the **Companion** system.
4. Control your Companion using in-game commands (see below).

---


## Controls and Commands

The **Player** account can issue the following commands, which direct the Companion's actions:

| Command           | Action                                                         |
|-------------------|----------------------------------------------------------------|
| `#stay`           | Companion stays in one place.                                  |
| `#follow`         | Companion follows the Player.                                  |
| `#assist`         | Helps the Player in combat.                                    |
| `#defend`         | Defends both the Player and itself.                            |
| `#only-heal`      | Uses healing spells exclusively.                               |
| `#passive`        | Enters passive mode (no combat actions).                       |
| `#mount`          | Mounts using the `Mount` spell (must be in spellbook).         |
| `#dismount`       | Dismounts.                                                     |
| `#loot`           | Moves to the Player's position and loots items.                |
| `#movement-speed` | Toggles movement speed (walk/run).                             |
| `#pause`          | Pauses PIGAS functionality temporarily.                        |
| `#disable`        | Completely disables PIGAS (**correct way to stop execution**). |

### Additional Commands
- Do emotions (`/emote`): `Let's /dance!`. Companion will repeat the emotion.
- Issue commands directly (`&command`): `&/cast Fireball`, `&.server info`, `&/use Hearthstone`.
- Add notes to the context file by prefixing text with `%`: `%Now we are in the Orgrimmar.`

---

## Configuring Companion Responses

Configure companion responses using the following files:

1. `open-ai.yaml` need to configure API access to OpenAI.
    ```yaml
    open-ai:
       base_url:  # API URL
       api_key:   # API key
    ```

2. `context.txt`: add relevant context for the *Companion* here.

---

### Extra Configurations
The following optional parameters are available in `config.yaml` to customize your setup further:

1. **Game Window Title**
   - If your game window title differs from the default, change it in the `game` section:
     ```yaml
     game:
       window-title: YOUR_GAME_WINDOW_TITLE
     ```

2. **Distances Fix**  
   Adjusting distance coefficients for navigation and interactions (default values are mentioned here):
   ```yaml
   navigation:
     distance_to_player_delta: 0.15
     mounted_distance_coefficient: 1.25
     looting_distance_coefficient: 0.5
     start_to_avoid_obstacles_distance_coefficient: 3.0
     start_to_wait_player_distance_coefficient: 50.0
   ```

3. **Debug Mode**
   - Enable debug mode for troubleshooting:
     ```yaml
     other:
       debug: true
     ```

4. **Companion Context File**
   - Set the custom context file for AI responses:
     ```yaml
     companion:
       context_file: YOUR_CONTEXT_FILE.txt
     ```

---

## Useful Tips
1. **Macro Setup**:
   - To simplify controlling your Companion, copy the file:  
     `.data/macro/macros-cache.txt` to your **Player** client directory:  
     `\WTF\Account\YOUR_PLAYER_ACCOUNT\macros-cache.txt`.

2. **Reinstall PIGAS**:
   - To reset your installation, remove the hidden `.local` file from the `pigas` directory.

3. **Adjust Distances**:
   - If you encounter distance-related issues between the Player and Companion (Companion is too close of far from the Player):
     - check the distance between characters with command `/distance` (as **Companion**);
     - set the distances manually in `config.yaml` in `navigation` (see below).

---

Enjoy your adventures with **PIGAS**, your ultimate sidekick in *World of Warcraft*!
