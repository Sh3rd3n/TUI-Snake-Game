"""
Snake Game TUI - Built with Textual
A classic snake game playable in your terminal!
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Header, Footer, Label
from textual.reactive import reactive
from textual.timer import Timer
from rich.text import Text
from rich.panel import Panel
import random
from enum import Enum, auto

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class SnakeGame(Static):
    """The snake game widget"""
    
    DEFAULT_CSS = """
    SnakeGame {
        width: 100%;
        height: 100%;
        content-align: center middle;
    }
    """
    
    # Game state
    snake = reactive([])
    food = reactive((0, 0))
    direction = reactive(Direction.RIGHT)
    score = reactive(0)
    game_over = reactive(False)
    paused = reactive(False)
    
    # Game settings
    WIDTH = 30
    HEIGHT = 20
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reset_game()
        self.timer: Timer | None = None
    
    def reset_game(self):
        """Reset the game to initial state"""
        # Start snake in the middle
        start_x = self.WIDTH // 2
        start_y = self.HEIGHT // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = Direction.RIGHT
        self.score = 0
        self.game_over = False
        self.paused = False
        self.place_food()
    
    def place_food(self):
        """Place food at a random location not on the snake"""
        while True:
            x = random.randint(0, self.WIDTH - 1)
            y = random.randint(0, self.HEIGHT - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
    
    def on_mount(self):
        """Start the game loop when mounted"""
        self.timer = self.set_interval(0.15, self.game_loop)
        self.update_display()
    
    def game_loop(self):
        """Main game loop - called every tick"""
        if self.game_over or self.paused:
            return
        
        # Calculate new head position
        head_x, head_y = self.snake[0]
        
        if self.direction == Direction.UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == Direction.DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == Direction.LEFT:
            new_head = (head_x - 1, head_y)
        else:  # RIGHT
            new_head = (head_x + 1, head_y)
        
        # Check for collisions with walls
        if (new_head[0] < 0 or new_head[0] >= self.WIDTH or 
            new_head[1] < 0 or new_head[1] >= self.HEIGHT):
            self.game_over = True
            self.update_display()
            return
        
        # Check for collisions with self
        if new_head in self.snake:
            self.game_over = True
            self.update_display()
            return
        
        # Move the snake
        self.snake.insert(0, new_head)
        
        # Check if food is eaten
        if new_head == self.food:
            self.score += 10
            self.place_food()
        else:
            self.snake.pop()  # Remove tail if no food eaten
        
        self.update_display()
    
    def update_display(self):
        """Render the game state"""
        if self.game_over:
            text = Text()
            text.append("GAME OVER!\n\n", style="bold red")
            text.append(f"Final Score: {self.score}\n\n", style="cyan")
            text.append("Press 'R' to restart\n", style="green")
            text.append("Press 'Q' to quit", style="yellow")
            self.update(Panel(text, title="Snake Game", border_style="red"))
            return
        
        # Build the game board
        lines = []
        for y in range(self.HEIGHT):
            row = []
            for x in range(self.WIDTH):
                if (x, y) == self.snake[0]:
                    row.append("▓▓")  # Snake head
                elif (x, y) in self.snake:
                    row.append("██")  # Snake body
                elif (x, y) == self.food:
                    row.append("● ")  # Food
                else:
                    row.append("  ")  # Empty space
            lines.append("".join(row))
        
        # Create display text
        text = Text("\n".join(lines))
        
        # Color the elements
        for y, line in enumerate(lines):
            for x in range(self.WIDTH):
                char_pos = x * 2
                if (x, y) == self.snake[0]:
                    text.stylize("bold bright_green", char_pos + y, char_pos + y + 2)
                elif (x, y) in self.snake:
                    text.stylize("bright_green", char_pos + y, char_pos + y + 2)
                elif (x, y) == self.food:
                    text.stylize("bold bright_red", char_pos + y, char_pos + y + 2)
        
        # Add score and instructions
        header = f"Score: {self.score}"
        if self.paused:
            header += " [PAUSED]"
        
        self.update(Panel(text, title=header, border_style="green"))
    
    def change_direction(self, new_direction: Direction):
        """Change snake direction (prevent 180-degree turns)"""
        if self.game_over:
            return
        
        # Prevent going directly backwards
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        if opposites.get(new_direction) != self.direction:
            self.direction = new_direction
    
    def toggle_pause(self):
        """Toggle pause state"""
        if not self.game_over:
            self.paused = not self.paused
            self.update_display()


class SnakeApp(App):
    """The main Snake game application"""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #game-container {
        width: 70;
        height: 30;
        border: solid green;
        padding: 1;
    }
    
    #sidebar {
        width: 25;
        height: 30;
        padding: 1;
    }
    
    #instructions {
        margin-top: 1;
    }
    
    #restart-btn {
        margin-top: 1;
    }
    
    #quit-btn {
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "restart", "Restart"),
        ("p", "pause", "Pause"),
        ("up", "up", "Up"),
        ("down", "down", "Down"),
        ("left", "left", "Left"),
        ("right", "right", "Right"),
        ("w", "up", "Up"),
        ("s", "down", "Down"),
        ("a", "left", "Left"),
        ("d", "right", "Right"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Horizontal():
            with Container(id="game-container"):
                yield SnakeGame(id="game")
            
            with Vertical(id="sidebar"):
                yield Label("[b]SNAKE GAME[/b]\n", classes="title")
                yield Label("Use arrow keys or WASD to move")
                yield Label("Eat the red dots (●) to grow")
                yield Label("Don't hit walls or yourself!\n")
                
                yield Static(id="instructions")
                
                yield Button("Restart (R)", id="restart-btn", variant="success")
                yield Button("Quit (Q)", id="quit-btn", variant="error")
        
        yield Footer()
    
    def on_mount(self):
        self.update_instructions()
    
    def update_instructions(self):
        instructions = self.query_one("#instructions", Static)
        instructions.update(
            "[b]Controls:[/b]\n"
            "↑/W - Up\n"
            "↓/S - Down\n"
            "←/A - Left\n"
            "→/D - Right\n"
            "P - Pause\n"
            "R - Restart\n"
            "Q - Quit\n"
        )
    
    def action_up(self):
        game = self.query_one(SnakeGame)
        game.change_direction(Direction.UP)
    
    def action_down(self):
        game = self.query_one(SnakeGame)
        game.change_direction(Direction.DOWN)
    
    def action_left(self):
        game = self.query_one(SnakeGame)
        game.change_direction(Direction.LEFT)
    
    def action_right(self):
        game = self.query_one(SnakeGame)
        game.change_direction(Direction.RIGHT)
    
    def action_pause(self):
        game = self.query_one(SnakeGame)
        game.toggle_pause()
    
    def action_restart(self):
        game = self.query_one(SnakeGame)
        game.reset_game()
        game.update_display()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "restart-btn":
            self.action_restart()
        elif event.button.id == "quit-btn":
            self.exit()


if __name__ == "__main__":
    app = SnakeApp()
    app.run()
