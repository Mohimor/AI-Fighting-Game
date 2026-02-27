# 🤖 Pixel Warrior - AI Fighting Game

**Artificial Intelligence Course Project**  
**Shahid Beheshti University – Fall 2025**  
**Instructor: Dr. Salimibadr**

---

## 📌 Overview

**Pixel Warrior** is a two-player fighting game where each fighter is controlled by an **intelligent agent**. The game simulates turn-based combat with real-time decision making, where agents must choose between moving, jumping, attacking (light/heavy), or dashing to defeat their opponent.

The project implements a **Minimax search tree** with **alpha-beta pruning** and a **heuristic evaluation function** to create an AI agent that can make optimal decisions in each frame.

---

## 🎮 Game Story

In a peaceful gymnasium ("Zourkhaneh"), where strength has always been controlled by unwritten rules, everything changes when strange creatures enter this world - **giant talking turtles**! The champions of the gym see them as an unknown threat and capture them. Soon after, three more turtles arrive with their elderly rat master. Now, the fate of these strangers is determined through one-on-one combat.

---

## ✨ Key Features

- ✅ **Two AI agents** competing against each other
- ✅ **Minimax algorithm** with depth-limited search (depth 2)
- ✅ **Alpha-beta pruning** for optimization
- ✅ **Heuristic evaluation function** with multiple weighted factors
- ✅ **Transposition table** to avoid re-computation
- ✅ **Time management** (0.4 second limit per decision)
- ✅ **Multiple agent language support** (Python, C++, Java)
- ✅ **Debug output** for frame-by-frame analysis
- ✅ **Random character selection** (5 different fighter types)
- ✅ **Random background selection** (3 different parallax backgrounds)
- ✅ **Health bars, victory screens, and round management**

---

## 🧠 AI Implementation

### 1. **Heuristic Evaluation Function**

The heuristic function evaluates each game state based on multiple weighted factors:

| Factor | Weight | Description |
| :--- | :--- | :--- |
| `health_diff` | 1.0 | Difference between player and opponent health |
| `distance_x` | -1.8 | Horizontal distance (negative weight encourages getting closer) |
| `distance_y` | -1.8 | Vertical distance (negative weight encourages same height) |
| `light_attack` | 1.4 | Bonus when light attack is ready |
| `heavy_attack` | 1.6 | Bonus when heavy attack is ready |
| `opponent_cooldown` | 1.8 | Bonus when opponent's attacks are on cooldown |
| `corner_penalty` | -1.8 | Penalty for being near screen corners |
| `good_range` | 1.8 | Bonus for being in optimal attack range (120-180 pixels) |
| `opponent_attacking` | -1.6 | Penalty when opponent is attacking (especially at close range) |
| `too_close_penalty` | -2.2 | Penalty for being too close (< 100 pixels) |
| `height_advantage` | 1.4 | Bonus for being above opponent |
| `same_height` | 1.2 | Bonus for being at similar height |

### 2. **Minimax with Alpha-Beta Pruning**

The agent uses a depth-limited minimax search (depth = 2) with alpha-beta pruning:

```python
def minimax(self, state, depth, alpha, beta, max_player):
    # Time check for 0.4 second limit
    if time_spent > 0.35:
        return self.heuristic(state, depth), None, current_depth
    
    # Terminal state check
    if depth == 0 or game_over:
        return self.heuristic(state, depth), None, current_depth
    
    # Transposition table lookup
    state_key = self._get_state_key(state, depth, max_player)
    
    if max_player:
        # Maximizing player (our agent)
        for action in possible_actions:
            new_state = self.action(state, action)
            # Consider opponent's possible responses
            for opp_action in opponent_actions:
                eval_score = self.minimax(opp_state, depth-1, alpha, beta, False)
            # Update best move
    else:
        # Minimizing player (opponent)
        for opp_action in opponent_actions:
            eval_score = self.minimax(new_state, depth-1, alpha, beta, True)
