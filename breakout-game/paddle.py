import turtle

PADDLE_WIDTH = 120
PADDLE_HEIGHT = 20
PADDLE_SPEED = 9
X_LIMIT = 340  # 400 - (PADDLE_WIDTH / 2)


class Paddle(turtle.Turtle):
    def __init__(self, position=(0, -250)):
        super().__init__()
        self.shape("square")
        self.color("#00E5FF")  # Bright cyan arcade paddle
        # Default turtle square is 20x20 px
        self.shapesize(stretch_wid=PADDLE_HEIGHT / 20, stretch_len=PADDLE_WIDTH / 20)
        self.penup()
        self.goto(position)
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed_val = PADDLE_SPEED

    def move_left(self):
        new_x = self.xcor() - self.speed_val
        if new_x >= -X_LIMIT:
            self.setx(new_x)
        else:
            self.setx(-X_LIMIT)

    def move_right(self):
        new_x = self.xcor() + self.speed_val
        if new_x <= X_LIMIT:
            self.setx(new_x)
        else:
            self.setx(X_LIMIT)

    def reset_position(self):
        self.goto(0, -250)
