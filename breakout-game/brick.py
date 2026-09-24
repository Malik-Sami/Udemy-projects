import turtle

BRICK_WIDTH = 70
BRICK_HEIGHT = 20

ROW_CONFIGS = [
    {"color": "#FF3B30", "points": 7},  # Red
    {"color": "#FF9500", "points": 5},  # Orange
    {"color": "#FFCC00", "points": 4},  # Yellow
    {"color": "#34C759", "points": 3},  # Green
    {"color": "#007AFF", "points": 1},  # Blue
]


class Brick(turtle.Turtle):
    def __init__(self, x, y, color, points):
        super().__init__()
        self.shape("square")
        self.color(color)
        # Default square is 20x20. Scale to BRICK_HEIGHT x BRICK_WIDTH
        self.shapesize(stretch_wid=BRICK_HEIGHT / 20, stretch_len=BRICK_WIDTH / 20)
        self.penup()
        self.goto(x, y)
        self.points = points
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT

    def destroy(self):
        """Hides and moves the brick out of bounds."""
        self.hideturtle()
        self.goto(2000, 2000)


class BrickManager:
    def __init__(self):
        self.bricks = []
        self.create_wall()

    def create_wall(self):
        """Builds a wall of colored bricks."""
        self.clear_all()

        columns = 10
        gap_x = 8
        gap_y = 10
        # Calculate horizontal centering:
        total_width = (columns * BRICK_WIDTH) + ((columns - 1) * gap_x)
        start_x = -(total_width / 2) + (BRICK_WIDTH / 2)
        start_y = 230

        for row_idx, config in enumerate(ROW_CONFIGS):
            row_y = start_y - (row_idx * (BRICK_HEIGHT + gap_y))
            for col_idx in range(columns):
                brick_x = start_x + (col_idx * (BRICK_WIDTH + gap_x))
                brick = Brick(brick_x, row_y, config["color"], config["points"])
                self.bricks.append(brick)

    def check_collision(self, ball):
        """
        Checks collision between ball and active bricks using AABB intersection.
        Returns the score earned from the hit brick, or 0 if no collision.
        """
        for brick in self.bricks:
            dist_x = abs(ball.xcor() - brick.xcor())
            dist_y = abs(ball.ycor() - brick.ycor())

            half_w = (brick.width / 2) + ball.radius
            half_h = (brick.height / 2) + ball.radius

            if dist_x < half_w and dist_y < half_h:
                # Collision confirmed! Determine bounce axis via penetration depth
                overlap_x = half_w - dist_x
                overlap_y = half_h - dist_y

                if overlap_y < overlap_x:
                    ball.bounce_y()
                else:
                    ball.bounce_x()

                ball.increase_speed()
                points = brick.points
                brick.destroy()
                self.bricks.remove(brick)
                return points

        return 0

    def remaining_count(self):
        return len(self.bricks)

    def clear_all(self):
        for brick in self.bricks:
            brick.destroy()
        self.bricks.clear()
