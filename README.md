# Fractal Gods: Sovereign Paradox

A stylized 2D combat prototype built with Pygame that now hits Phase 2 of the "Fractal Gods" experience. This slice elevates the combat loop with myth-tier abilities, adaptive echoes, and expanded feedback while preserving the tight movement, stamina-driven attacks, and parry-first mindset from the opener.

## Phase 2 Feature Set
- **Mythic Abilities Unlocked** – Spend Myth Energy on burst powers: freeze the battlefield with **Time Slow (X)**, call down an **Ascendent Lightning strike (C)**, or double-tap **A/D** for a **Void Shift** teleport with invulnerability frames.
- **Combo Engine** – Every successful hit adds to a living combo counter that boosts damage, feeds Myth Energy, and unlocks flashier finishers.
- **Adaptive Echo AI** – The sentinel studies your habits and adjusts chase speed or attack tempo depending on whether you lean on lights, heavies, or parries.
- **Myth Energy Economy** – A dedicated meter tracks the godlike resource, rewarding aggression, parries, and smart ability timing.
- **Expanded Visual & Audio FX** – New cast animations, aura blooms, lightning bolts, and time dilation overlays push the arena toward high-drama spectacle.
- **Persistent Combat Feedback** – Ability status readouts, combo banners, and cooldown trackers keep every system readable at a glance.

## Controls
| Action | Key |
| --- | --- |
| Move | `A` / `D` |
| Jump | `W` |
| Crouch | `S` |
| Light Attack | `1` |
| Heavy Attack | `2` |
| Parry | `F` |
| Time Slow | `X` |
| Lightning Strike | `C` |
| Void Shift | Double-tap `A` or `D` |
| Reset Duel | `R` |
| Quit | `Esc` or close window |

Each ability consumes Myth Energy. Manage the meter to decide when to slow reality, reposition, or obliterate echoes from afar.

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

The arena window will open at 960×540. Duel the echo sentinel, chain combos to juice Myth Energy, and unleash abilities to break the loop. Press `R` after a win or loss to restart.

## Project Roadmap
- **Phase 3 – Arena Multipliers:** rotating battleground modifiers (vortex winds, vault hazards) that react to combo state and Myth Energy levels.
- **Phase 4 – Echo Intelligence:** expand enemy behaviors so echoes learn from recent player habits across multiple encounters.
- **Phase 4 – Progression Tree:** craft the symbolic path selection UI and persistent upgrades.
- **Phase 5 – Narrative Integration:** weave in story arcs, arenas, and lore codices that reinforce the sovereign paradox mythology.

Contributions, ideas, and playtest notes are welcome as we continue shaping the pantheon.
