# Tiny STG

a very ~~shit~~ good game
## Controls

- W / ↑ : Move up  
- S / ↓ : Move down  
- A / ← : Move left  
- D / → : Move right  
- Shift : Slow movement  
- Z : Shoot  

## Requirements

```bash
pip install pygame
```

## Project Layout

```text
main.py              # Entry point
stg_df/
  constants.py       # Game constants and colors
  player.py          # Player movement, shooting, respawn
  projectiles.py     # Bullets and homing bullets
  enemies.py         # Enemy types, styles, movement, attack patterns
  waves.py           # Pseudo-random wave director and 36 spawn formations
  boss.py            # Boss phases and bullet patterns
  effects.py         # Explosion particles
  game.py            # Main game loop, state, collision, rendering
```

Normal play has 2 stages with 5 waves per stage. The next wave starts only after
the current enemies and enemy bullets are gone.
