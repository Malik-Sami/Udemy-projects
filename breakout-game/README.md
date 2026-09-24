# Breakout (1976 Classic)

A desktop recreation of the classic 1976 arcade game **Breakout**, originally conceptualized by Nolan Bushnell and Steve Bristow, and programmed by Steve Wozniak.

Built with Python and Object-Oriented Turtle Graphics as part of the **100 Days of Code: Python Pro Bootcamp**.

---

## 🎮 How to Play

### Controls
| Key | Action |
| --- | --- |
| `Left Arrow` / `A` | Move paddle left |
| `Right Arrow` / `D` | Move paddle right |
| `Space` | Launch ball from paddle |
| `R` | Restart game after Game Over / Victory |

### Gameplay & Rules
1. **Objective**: Break down the wall of colored bricks by bouncing the ball off your paddle without letting the ball fall past the bottom edge.
2. **Deflection Physics**: The ball's bounce angle depends on where it hits the paddle. Hitting near the paddle's edge creates sharper angles for aiming at hard-to-reach bricks.
3. **Speed Ramp**: Every brick broken slightly increases the ball speed for an authentic arcade challenge.
4. **Scoring**:
   - 🔴 **Red bricks (Row 1)**: 7 points
   - 🟠 **Orange bricks (Row 2)**: 5 points
   - 🟡 **Yellow bricks (Row 3)**: 4 points
   - 🟢 **Green bricks (Row 4)**: 3 points
   - 🔵 **Blue bricks (Row 5)**: 1 point
5. **Lives & High Scores**:
   - You start with **3 lives**.
   - Your highest score is automatically saved to `highscore.txt`.

---

## 🚀 Running the Game

From the workspace root or inside the `breakout-game` directory:

```bash
cd breakout-game
uv run python main.py
```
