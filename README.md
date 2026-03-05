# Aim Trainer Pro - SEM252 Project

A reflex training mini-game built with Python and Pygame. Test your reaction time and accuracy by clicking targets before they disappear!

## 🎮 Gameplay

Aim Trainer Pro tests your speed and precision through a dynamic 60-second challenge. 

- **Objective**: Click on targets that appear on the screen as quickly and accurately as possible within the time limit.
- **Controls**: Use your mouse to aim and the **Left Mouse Button** to shoot targets. Press **ESC** to pause or resume the game at any time.
- **Dynamic Difficulty**: As the game progresses, the targets will continually become smaller and disappear faster, making it increasingly more difficult to hit them.
- **Visual Feedback**: Real-time stats are displayed on the HUD. Hitting a target produces satisfying screen-pop effects and floating score text.
- **Customization**: You can customize your crosshair type, color, size, and other game difficulty settings entirely from the built-in Settings menu to suit your playstyle.

## 🏆 Score System

The scoring system rewards both **accuracy** and **speed**. Hitting the center of a target or destroying a target very quickly yields bonus points.

- **Overall Score Formula**: `Final Score = Hit Zone Base Points + Time Bonus`

### 1. Hit Zones (Base Points)
Targets consist of 3 concentric circles. Closer to the bullseye means more points:
- **Inner Circle**: 150 Base Points *(PERFECT!)*
- **Middle Circle**: 125 Base Points *(GREAT!)*
- **Outer Circle**: 100 Base Points *(GOOD!)*

### 2. Time Bonus
Up to 100 additional points are awarded based on how fast your reaction time is. 
- **Formula**: `Bonus = max(0, (TTL - ReactionTime) / TTL * 100)`
- *Explanation*: The faster you click the target before its Time-To-Live (TTL) runs out, the closer you get to the full 100 bonus points.

### 3. Misses & Timeouts
- **User Miss**: Clicking the background instead of a target.
- **Target Miss**: Letting a target disappear before clicking it (Timeout).
- **Penalty**: Both result in 0 points. User Misses also lower your overall accuracy percentage at the end of the game.

### 4. Game History & Scoreboard
Whenever you finish a game naturally, your Final Score, Overall Accuracy, Average Reaction Time, and Date are automatically saved. You can proudly show off your top 10 best runs on the **Scoreboard** screen accessible from the main menu!

## 🚀 How to Run

### Prerequisites
- Python 3.7 or higher installed on your system.
Before running the game, make sure to install the required dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Running the game:
Make sure you are in the project's root folder and run the `main.py` file:
```bash
python main.py
```

---

**Enjoy training your aim! 🎯**
