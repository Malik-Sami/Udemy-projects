import turtle
import math
import random

BALL_RADIUS = 9
INITIAL_SPEED = 6.5
MAX_SPEED = 12.0
SPEED_INCREMENT = 0.15


class Ball(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.color("#FFFDE7")  # Warm white
        self.shapesize(stretch_wid=BALL_RADIUS / 10, stretch_len=BALL_RADIUS / 10)
        self.penup()
        self.radius = BALL_RADIUS
        self.speed_mag = INITIAL_SPEED
        self.dx = 0.0
        self.dy = 0.0
        self.is_stuck_to_paddle = True
        self.reset_to_paddle(0, -230)

    def reset_to_paddle(self, paddle_x, paddle_y):
        """Attaches the ball to the paddle prior to launch."""
        self.is_stuck_to_paddle = True
        self.speed_mag = INITIAL_SPEED
        self.goto(paddle_x, paddle_y + 18)
        self.dx = 0.0
        self.dy = 0.0

    def launch(self):
        """Launches the ball upward at a slight random angle."""
        if not self.is_stuck_to_paddle:
            return
        self.is_stuck_to_paddle = False
        angle_deg = random.choice([60, 70, 75, 105, 110, 120])
        angle_rad = math.radians(angle_deg)
        self.dx = self.speed_mag * math.cos(angle_rad)
        self.dy = self.speed_mag * math.sin(angle_rad)

    def move(self):
        if not self.is_stuck_to_paddle:
            self.setx(self.xcor() + self.dx)
            self.sety(self.ycor() + self.dy)

    def bounce_x(self):
        self.dx = -self.dx

    def bounce_y(self):
        self.dy = -self.dy

    def bounce_off_paddle(self, paddle):
        """
        Bounces off paddle with angle deflection based on where it hit:
        Hitting center sends it more vertical, edges send it out diagonally.
        """
        offset = (self.xcor() - paddle.xcor()) / (paddle.width / 2)
        # Clamp offset between -1.0 and 1.0
        offset = max(-0.95, min(0.95, offset))

        # Deflection angle between 25 deg and 155 deg
        # Center (0) -> 90 deg (straight up)
        # Left (-1)  -> 150 deg (sharp left)
        # Right (1)  -> 30 deg (sharp right)
        launch_angle = 90 - (offset * 60)
        angle_rad = math.radians(launch_angle)

        self.speed_mag = min(self.speed_mag + 0.1, MAX_SPEED)
        self.dx = self.speed_mag * math.cos(angle_rad)
        self.dy = abs(self.speed_mag * math.sin(angle_rad))  # Always bounce upwards

        # Place ball above paddle to prevent multi-collision glitch
        self.sety(paddle.ycor() + (paddle.height / 2) + self.radius + 1)

    def increase_speed(self):
        """Slightly speeds up ball after hitting a brick."""
        if self.speed_mag < MAX_SPEED:
            self.speed_mag += SPEED_INCREMENT
            # Re-normalize dx and dy
            current_angle = math.atan2(self.dy, self.dx)
            self.dx = self.speed_mag * math.cos(current_angle)
            self.dy = self.speed_mag * math.sin(current_angle)
