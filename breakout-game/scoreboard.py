import os
import turtle

FONT_NAME = "Courier"
SCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.txt")


class Scoreboard(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.lives = 3
        self.high_score = self.load_high_score()
        self.hideturtle()
        self.penup()
        self.color("white")
        self.update_display()

        # Overlay turtle for messages
        self.message_turtle = turtle.Turtle()
        self.message_turtle.hideturtle()
        self.message_turtle.penup()
        self.message_turtle.color("#FFD700")  # Gold arcade text

    def load_high_score(self):
        if os.path.exists(SCORE_FILE):
            try:
                with open(SCORE_FILE, "r") as file:
                    return int(file.read().strip())
            except (ValueError, OSError):
                return 0
        return 0

    def save_high_score(self):
        try:
            with open(SCORE_FILE, "w") as file:
                file.write(str(self.high_score))
        except OSError:
            pass

    def update_display(self):
        self.clear()
        self.goto(0, 260)
        hearts = "♥ " * self.lives
        display_text = (
            f"SCORE: {self.score:03d}     "
            f"LIVES: {hearts.strip() if hearts else 'NONE'}     "
            f"BEST: {self.high_score:03d}"
        )
        self.write(display_text, align="center", font=(FONT_NAME, 14, "bold"))

    def add_score(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        self.update_display()

    def lose_life(self):
        self.lives -= 1
        self.update_display()
        return self.lives <= 0

    def show_launch_prompt(self):
        self.message_turtle.clear()
        self.message_turtle.goto(0, -60)
        self.message_turtle.write(
            "PRESS [SPACE] TO LAUNCH BALL",
            align="center",
            font=(FONT_NAME, 13, "bold"),
        )

    def clear_message(self):
        self.message_turtle.clear()

    def game_over(self):
        self.message_turtle.clear()
        self.message_turtle.color("#FF3B30")
        self.message_turtle.goto(0, 20)
        self.message_turtle.write(
            "GAME OVER",
            align="center",
            font=(FONT_NAME, 30, "bold"),
        )
        self.message_turtle.goto(0, -30)
        self.message_turtle.color("white")
        self.message_turtle.write(
            "Press 'R' to Restart",
            align="center",
            font=(FONT_NAME, 14, "normal"),
        )

    def you_win(self):
        self.message_turtle.clear()
        self.message_turtle.color("#34C759")
        self.message_turtle.goto(0, 20)
        self.message_turtle.write(
            "VICTORY! WALL CLEARED!",
            align="center",
            font=(FONT_NAME, 26, "bold"),
        )
        self.message_turtle.goto(0, -30)
        self.message_turtle.color("white")
        self.message_turtle.write(
            f"Final Score: {self.score}   -   Press 'R' to Play Again",
            align="center",
            font=(FONT_NAME, 14, "normal"),
        )

    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.clear_message()
        self.update_display()
