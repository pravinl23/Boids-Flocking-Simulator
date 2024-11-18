# Boids-Flocking-Simulator

A Python-based simulation of Boids, inspired by Craig Reynolds' 1986 paper on distributed behavioral models. This project demonstrates flocking behavior through a combination of separation, alignment, and cohesion rules, allowing users to observe emergent patterns in a dynamic and interactive environment.

---

## Features

- **Realistic Flocking Behavior**:
  - Separation: Avoid collisions with nearby boids.
  - Alignment: Match velocity with nearby boids.
  - Cohesion: Move toward the center of nearby boids.
- **Interactive Controls**:
  - Enable/disable flocking behaviors dynamically.
  - Adjust parameters for cohesion, alignment, and separation.
  - Toggle cursor-following mode for interactive movement.
  - Add Obstacles to screen manually that boids will avoid

---

## Requirements

To run this simulator, you need:

- **Python 3.8+**
- Required Libraries:
  - `pygame`
  - `math`
  - `random`

You can install the dependencies using:
```bash
pip install pygame


| Key/Action        | Function                             |
|-------------------|--------------------------------------|
| `ESC`             | Exit the simulation                  |
| `Y`               | Toggle Cursor-Following mode         |
| `X`               | Toggle Obstacles on Screen           |
