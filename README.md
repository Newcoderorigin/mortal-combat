# Fractal Gods: Sovereign Paradox

A stylized 2D combat prototype built with Pygame that begins Phase 1 of the "Fractal Gods" experience. This vertical slice focuses on core moment-to-moment combat: responsive movement, a stamina-driven attack kit, timed parries, and a learning enemy patrolling a mythic arena.

## Phase 1 Feature Set
- **2D Combat Fundamentals** – Move, jump, crouch, and orient toward your foe with smooth gravity and ground detection.
- **Light & Heavy Strikes** – Spend stamina on quick jabs or slower, harder-hitting reality slices with knockback.
- **Reactive Parry Window** – Time your parry to deflect incoming blows, regain mythic focus, and stun the enemy for counterattacks.
- **Enemy Patrol & Assault** – Face an echo sentinel that roams the arena, chases when you draw near, and telegraphs heavy swings.
- **Health & Stamina Interface** – Monitor survivability and exertion through layered HUD bars and combat text cues.
- **Win / Lose Cycle** – Victory and defeat states pause the action and let you reset for another duel.

Future phases will layer in the god-tier abilities (lightning, time-slow, void shift), combo systems, and the symbolic progression tree once the combat core feels sharp.

## Controls
| Action | Key |
| --- | --- |
| Move | `A` / `D` |
| Jump | `W` |
| Crouch | `S` |
| Light Attack | `1` |
| Heavy Attack | `2` |
| Parry | `F` |
| Reset Duel | `R` |
| Quit | `Esc` or close window |

Ability slots `X` and `C` are reserved for future mythic powers.

## Getting Started
1. Ensure you have Python 3.10+ installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the prototype:
   ```bash
   python main.py
   ```

The arena window will open at 960×540. Duel the echo sentinel, experiment with spacing and parry timings, and press `R` after a win or loss to restart.

## Project Roadmap
- **Phase 2 – Power Systems:** introduce lightning strikes, time-slow bursts, void dash, and the myth energy meter.
- **Phase 3 – Echo Intelligence:** expand enemy behaviors so echoes learn from recent player habits.
- **Phase 4 – Progression Tree:** craft the symbolic path selection UI and persistent upgrades.
- **Phase 5 – Narrative Integration:** weave in story arcs, arenas, and lore codices that reinforce the sovereign paradox mythology.

Contributions, ideas, and playtest notes are welcome as we continue shaping the pantheon.
