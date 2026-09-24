import os
import sys
import time
import turtle

# Ensure local modules can be resolved regardless of current working directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# pyrefly: ignore [missing-import]
from ball import Ball
# pyrefly: ignore [missing-import]
from brick import BrickManager
# pyrefly: ignore [missing-import]
from paddle import Paddle
# pyrefly: ignore [missing-import]
from scoreboard import Scoreboard

# Screen configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FRAME_DELAY = 1 / 60  # ~60 FPS


def main():
    screen = turtle.Screen()
    screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.bgcolor("#121212")  # Deep arcade charcoal
    screen.title("Breakout - Steve Wozniak Classic (100 Days of Code)")
    screen.tracer(0)

    # Initialize components
    paddle = Paddle()
    ball = Ball()
    bricks = BrickManager()
    scoreboard = Scoreboard()
    scoreboard.show_launch_prompt()

    # Track input states for smooth fluid motion
    keys_pressed = {"left": False, "right": False}
    game_state = {"status": "WAITING_LAUNCH"}  # WAITING_LAUNCH, PLAYING, GAME_OVER, VICTORY

    def press_left():
        keys_pressed["left"] = True

    def release_left():
        keys_pressed["left"] = False

    def press_right():
        keys_pressed["right"] = True

    def release_right():
        keys_pressed["right"] = False

    def launch_ball():
        if game_state["status"] == "WAITING_LAUNCH":
            scoreboard.clear_message()
            ball.launch()
            game_state["status"] = "PLAYING"

    def restart_game():
        if game_state["status"] in ("GAME_OVER", "VICTORY"):
            scoreboard.reset_game()
            bricks.create_wall()
            paddle.reset_position()
            ball.reset_to_paddle(paddle.xcor(), paddle.ycor())
            scoreboard.show_launch_prompt()
            game_state["status"] = "WAITING_LAUNCH"

    # Event listeners
    screen.listen()
    screen.onkeypress(press_left, "Left")
    screen.onkeyrelease(release_left, "Left")
    screen.onkeypress(press_left, "a")
    screen.onkeyrelease(release_left, "a")
    screen.onkeypress(press_left, "A")
    screen.onkeyrelease(release_left, "A")

    screen.onkeypress(press_right, "Right")
    screen.onkeyrelease(release_right, "Right")
    screen.onkeypress(press_right, "d")
    screen.onkeyrelease(release_right, "d")
    screen.onkeypress(press_right, "D")
    screen.onkeyrelease(release_right, "D")

    screen.onkey(launch_ball, "space")
    screen.onkey(restart_game, "r")
    screen.onkey(restart_game, "R")

    # Main game loop
    is_running = True
    try:
        while is_running:
            # Handle paddle movement
            if keys_pressed["left"]:
                paddle.move_left()
            if keys_pressed["right"]:
                paddle.move_right()

            if game_state["status"] == "WAITING_LAUNCH":
                # Ball follows paddle smoothly
                ball.goto(paddle.xcor(), paddle.ycor() + 18)

            elif game_state["status"] == "PLAYING":
                ball.move()

                # 1. Wall collisions (Left / Right)
                if ball.xcor() <= -385 and ball.dx < 0:
                    ball.bounce_x()
                elif ball.xcor() >= 385 and ball.dx > 0:
                    ball.bounce_x()

                # 2. Top wall collision
                if ball.ycor() >= 285 and ball.dy > 0:
                    ball.bounce_y()

                # 3. Paddle collision (only when falling)
                paddle_top = paddle.ycor() + (paddle.height / 2)
                paddle_bottom = paddle.ycor() - (paddle.height / 2)
                paddle_left = paddle.xcor() - (paddle.width / 2) - ball.radius
                paddle_right = paddle.xcor() + (paddle.width / 2) + ball.radius

                if (
                    ball.dy < 0
                    and (paddle_bottom <= ball.ycor() - ball.radius <= paddle_top + 4)
                    and (paddle_left <= ball.xcor() <= paddle_right)
                ):
                    ball.bounce_off_paddle(paddle)

                # 4. Brick wall collision
                points = bricks.check_collision(ball)
                if points > 0:
                    scoreboard.add_score(points)
                    if bricks.remaining_count() == 0:
                        game_state["status"] = "VICTORY"
                        scoreboard.you_win()

                # 5. Bottom boundary / Missed ball
                if ball.ycor() <= -290:
                    game_over = scoreboard.lose_life()
                    if game_over:
                        game_state["status"] = "GAME_OVER"
                        scoreboard.game_over()
                    else:
                        paddle.reset_position()
                        ball.reset_to_paddle(paddle.xcor(), paddle.ycor())
                        scoreboard.show_launch_prompt()
                        game_state["status"] = "WAITING_LAUNCH"

            screen.update()
            time.sleep(FRAME_DELAY)

    except (turtle.Terminator, Exception):
        # Exit cleanly if window is closed
        pass


if __name__ == "__main__":
    main()
