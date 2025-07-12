
# PIGAS: How It's Made.

## Table of Content
1. [Part I: Project Bricks](#part-one)
2. [Part II: Essential API methods](#part-two)

## Part I: Project Bricks <a name="part-one"></a>

In this series of articles, I want to take you inside the PIGAS project.
In the first part, I want to give you a bird's eye view of the project.
How does it work? How is it made? Is it an AI project?
Let's move together step by step.

What Is PIGAS Exactly?
The abbreviation PIGAS is the name of the entire project (Personal In-Game Adventure Sidekick), as well as the name of its main part (let's call it AI controller). The second part of the project is Gingham Shirt, an addon used to obtain information about the state of the game.

PIGAS Project Dependency Chain
PIGAS relies on several layers of interaction:
1. WoW Client (C++ Game Client). It communicates with WoW server and contains all game state data (position, health, combat status, etc).
2. WoW API (Limited Lua interface) provides controlled access to game data (e.g., player HP, position, but not raw memory). It does not allow direct player control (no "move-to" commands).
3. Gingham Shirt (Custom WoW Addon). The project addon that extracts game data (player/companion state) and encodes it visually as colored squares (a "plaid" pattern).
4. PIGAS (External AI Controller). As was mentioned before it's the main part of the project. 
It reads the Gingham Shirt, decodes colors into game data (positions, HP, commands, etc), makes decisions about companion behaviour (e.g., follow, attack, heal) and sends inputs via keyboard emulation.

This scheme is completely closed: all changes of companion states in the game world made by PIGAS will be written to the server data, the server data will be read by Gingham Shirt (using the WoW API) and written in plaid format, and the new data will be used by PIGAS to make new decisions. 
One PIGAS cycle takes about 200 ms.

Gingham Shirt Part Logic
The Gingham Shirt encodes a large amount of data into colored patterns. Here are some of them:
- player and companion coordinates in the game world (X and Y coordinates);
- direction of the companion facing;
- current and max health/mana values of companion and player;
- combat states of both;
- mount state of companion;
- last party chat message;
- game object information under cursor (detects if the companion is hovering over an enemy, NPC, or item).

PIGAS Part Logic
PIGAS acts as a rule-based AI assistant. In this case it:
- reads the Gingham Shirt;
- interprets the data (e.g., "Player HP is low" or "Player send the command #loot");
- decides an action (e.g., "Use healing spell on player" or "Go to the player position");
- executes via keyboard/mouse emulation.

Well, what is the PIGAS?
By today's standards, PIGAS could be called as rule-based AI agent (not machine learning, but logic-driven) and half-automated in-game assistant (like a smart companion NPC) that is completely dependent on the player's actions and states.


## Part II: Essential API methods <a name="part-two"></a>

In the first part of this article series, we introduced the PIGAS project and its architecture. Here’s a visual representation of the system:

```
WoW Client    ➡️    WoW API

     ⬆️                ⬇️  
   
    PIGAS    ⬅️   Gingham Shirt  
```
In this article, we’ll explore the WoW API with some essential methods for retrieving information about the current game state.

Understanding WoW API Methods
The WoW API consists of over 800 Lua functions that allow interaction with the C++ based game client. These methods act as a bridge, enabling developers to fetch data from the game but imposing strict limitations to prevent cheating.
A lot of API methods were deprecated over the years (since vanilla) due to botting, cheating, and other exploitative behavior.
Key Restrictions:
No direct control over gameplay: You cannot manipulate character movement (e.g., changing coordinates) or force attacks on creatures.
Limited interaction capabilities: You can still use methods like AcceptResurrect(), AcceptQuest(), AcceptGroup(), SendChatMessage(), and AddFriend().
In essence, the WoW API primarily functions as a "getter" rather than a "setter"—you can retrieve game state information but rarely modify it.

Core API Methods Used by Gingham Shirt
Gingham Shirt relies on several critical API methods to relay data to PIGAS. Below are the most important ones, categorized by functionality:

1. Player Interaction
AcceptQuest() – Automatically accepts shared quests.
AcceptGroup() – Auto-accepts party invites.
GetLootRollItemInfo() & RollOnLoot() – Checks active loot rolls and automatically selects "Greed."
SendChatMessage() – Sends messages in party chat.
2. Player & Companion Status
GetPlayerMapPosition() – Retrieves coordinates of the player and companion.
GetPlayerFacing() – Determines the companion’s facing direction.
UnitHealth(), UnitMana() – Fetches health and mana levels.
GetMirrorTimerInfo() & GetMirrorTimerProgress() – Tracks breath levels (e.g., underwater).
3. Cursor/Object Inspection
UnitExists() – Checks if a unit exists under the cursor.
UnitName(), UnitRace(), UnitFactionGroup(), etc – Retrieves unit details.
GetTooltipInfo() – Extracts tooltip text (useful for looting checks).
4. Map & Location Data
GetCurrentMapAreaID(), GetMapInfo() – Fetches map ID and name.

Why Are These Methods Crucial for PIGAS?
Player Interaction – Automating quest acceptance, group joining, and loot rolling improves convenience, reducing manual input.
Game State Monitoring – Tracking health, mana, and positioning ensures the companion behaves correctly.
Cursor-Based Checks – Essential for looting logic (e.g., verifying if loot has been detected).
Map Awareness – Since WoW maps use non-uniform distance scaling, knowing the current map helps adjust movement calculations between the player and companion.

Beyond the Basics
The WoW API offers many more useful methods, including:
Retrieving achievement and quest log data.
Managing party/guild interactions.
Accessing vendor/trading information.
Modifying client settings.
P.S. Every known WoW addon is built using these API methods!
