import sys

LOGO = r"""
 ______        ______           ______           
|_   __|      |_   __|          |_   _|          
  | |  _  ___    | | __ _  ___    | | ___   ___  
  | | | |/ __|   | |/ _` |/ __|   | |/ _ \ / _ \ 
  | | | | (__    | | (_| | (__    | | (_) |  __/ 
  \_/ |_|\___|   \_/\__,_|\___|   \_/\___/ \___| 
"""

REFERENCE_BOARD = """
Positions Reference:
 1 | 2 | 3 
-----------
 4 | 5 | 6 
-----------
 7 | 8 | 9 
"""

WINNING_COMBINATIONS = [
    # Rows
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    # Columns
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    # Diagonals
    (0, 4, 8),
    (2, 4, 6),
]


def display_board(board: list[str]) -> None:
    """Print the current 3x3 game board."""
    print(f"\n {board[0]} | {board[1]} | {board[2]} ")
    print("-----------")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("-----------")
    print(f" {board[6]} | {board[7]} | {board[8]} \n")


def check_winner(board: list[str], player: str) -> bool:
    """Check if the specified player has won the game."""
    for combo in WINNING_COMBINATIONS:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] == player:
            return True
    return False


def is_board_full(board: list[str]) -> bool:
    """Check if all positions on the board are occupied."""
    return all(cell != " " for cell in board)


def get_player_move(board: list[str], player: str) -> int:
    """Prompt the current player for a move and validate it.
    
    Returns a valid 0-based board index (0 to 8).
    """
    while True:
        choice = input(f"Player '{player}', choose your position (1-9): ").strip()
        if not choice.isdigit():
            print("Invalid input! Please enter a number between 1 and 9.")
            continue

        position = int(choice)
        if position < 1 or position > 9:
            print("Out of range! Please choose a number from 1 to 9.")
            continue

        index = position - 1
        if board[index] != " ":
            print(f"Position {position} is already taken! Choose an empty spot.")
            continue

        return index


def play_round() -> str:
    """Play a single round of Tic Tac Toe.
    
    Returns 'X', 'O', or 'Tie'.
    """
    board = [" "] * 9
    current_player = "X"

    print(REFERENCE_BOARD)
    display_board(board)

    while True:
        move_index = get_player_move(board, current_player)
        board[move_index] = current_player
        display_board(board)

        if check_winner(board, current_player):
            print(f" Congratulations! Player '{current_player}' wins this round! ")
            return current_player

        if is_board_full(board):
            print("It's a tie! Well played both.")
            return "Tie"

        # Switch turns
        current_player = "O" if current_player == "X" else "X"


def display_scoreboard(scores: dict[str, int]) -> None:
    """Display the cumulative score tracker."""
    print("\n" + "=" * 32)
    print("           SCOREBOARD           ")
    print("=" * 32)
    print(f" Player X Wins : {scores['X']}")
    print(f" Player O Wins : {scores['O']}")
    print(f" Ties          : {scores['Tie']}")
    print("=" * 32 + "\n")


def main() -> None:
    """Main game loop managing replayability and scores."""
    print(LOGO)
    print("Welcome to Command Line Tic Tac Toe!")
    print("Two players take turns. Player 1 is 'X', and Player 2 is 'O'.")

    scores = {"X": 0, "O": 0, "Tie": 0}

    while True:
        result = play_round()
        scores[result] += 1
        display_scoreboard(scores)

        while True:
            play_again = input("Do you want to play another round? (y/n): ").strip().lower()
            if play_again in ["y", "yes"]:
                print("\nStarting a new round...")
                break
            elif play_again in ["n", "no"]:
                print("\nThanks for playing Tic Tac Toe! Goodbye!")
                sys.exit(0)
            else:
                print("Invalid response. Please type 'y' for yes or 'n' for no.")


if __name__ == "__main__":
    main()
