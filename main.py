
import random
import pygame
from collections import defaultdict, Counter

# -------------------- CONFIGURATION --------------------

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Rock Paper Scissors")

CLOCK = pygame.time.Clock()

BG = (19, 24, 42)
PANEL = (31, 39, 62)
WHITE = (245, 247, 255)
MUTED = (170, 181, 204)
BLUE = (75, 145, 255)
GREEN = (66, 200, 145)
RED = (240, 90, 105)
YELLOW = (255, 202, 90)

FONT = pygame.font.SysFont("arial", 22)
SMALL = pygame.font.SysFont("arial", 17)
TITLE = pygame.font.SysFont("arial", 36, bold=True)
BIG = pygame.font.SysFont("arial", 27, bold=True)

MOVES = ["Rock", "Paper", "Scissors"]

# What defeats each move?
COUNTER = {
    "Rock": "Paper",
    "Paper": "Scissors",
    "Scissors": "Rock",
}


# -------------------- AI ENGINE --------------------

class PatternAI:
    def __init__(self):
        self.history = []
        self.transitions = defaultdict(Counter)

    def predict(self):
        """Predict the next move from the last observed move."""
        if not self.history:
            return None

        previous = self.history[-1]
        choices = self.transitions[previous]

        if not choices:
            return None

        # Select the most frequently observed next move.
        highest = max(choices.values())
        best_moves = [
            move for move, count in choices.items()
            if count == highest
        ]

        return random.choice(best_moves)

    def choose_move(self):
        """Counter the prediction, or play randomly."""
        prediction = self.predict()

        if prediction is None:
            return random.choice(MOVES), None

        return COUNTER[prediction], prediction

    def learn(self, player_move):
        """Record the move and update transition counts."""
        if self.history:
            previous = self.history[-1]
            self.transitions[previous][player_move] += 1

        self.history.append(player_move)


# -------------------- GAME LOGIC --------------------

def get_result(player, ai):
    if player == ai:
        return "Draw"

    winning_pairs = {
        ("Rock", "Scissors"),
        ("Paper", "Rock"),
        ("Scissors", "Paper"),
    }

    if (player, ai) in winning_pairs:
        return "You win!"

    return "AI wins!"


ai_brain = PatternAI()

player_score = 0
ai_score = 0
draws = 0

player_move = None
ai_move = None
prediction = None
message = "Choose your move to start!"
result_color = WHITE
rounds = 0
recent_results = []

buttons = {
    move: pygame.Rect(65 + i * 245, 430, 210, 58)
    for i, move in enumerate(MOVES)
}

reset_button = pygame.Rect(310, 520, 180, 45)


def play_round(move):
    global player_move, ai_move, prediction
    global player_score, ai_score, draws
    global message, result_color, rounds, recent_results

    # AI makes its decision before seeing the current move.
    ai_move, prediction = ai_brain.choose_move()
    player_move = move

    outcome = get_result(player_move, ai_move)
    rounds += 1

    if outcome == "You win!":
        player_score += 1
        result_color = GREEN
    elif outcome == "AI wins!":
        ai_score += 1
        result_color = RED
    else:
        draws += 1
        result_color = YELLOW

    message = outcome

    recent_results.insert(
        0, f"{player_move} vs {ai_move} - {outcome}"
    )
    recent_results = recent_results[:3]

    # Only now does the AI learn the current move.
    ai_brain.learn(player_move)


# -------------------- DRAWING HELPERS --------------------

def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(surface, rect)


def draw_panel(rect, color=PANEL, radius=16):
    pygame.draw.rect(screen, color, rect, border_radius=radius)


# -------------------- MAIN LOOP --------------------

running = True

while running:
    CLOCK.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for move, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        play_round(move)

                if reset_button.collidepoint(event.pos):
                    ai_brain = PatternAI()
                    player_score = ai_score = draws = 0
                    player_move = ai_move = prediction = None
                    rounds = 0
                    recent_results = []
                    message = "Game reset! Choose your move."
                    result_color = WHITE

    # Background
    screen.fill(BG)

    # Header
    draw_text("AI ROCK PAPER SCISSORS", TITLE, WHITE, 400, 35, True)
    draw_text(
        "Play against an AI that learns your patterns",
        SMALL, MUTED, 400, 72, True
    )

    # Scoreboard
    draw_panel(pygame.Rect(45, 105, 710, 85))

    draw_text("YOU", SMALL, BLUE, 165, 120, True)
    draw_text(str(player_score), BIG, WHITE, 165, 155, True)

    draw_text("DRAWS", SMALL, YELLOW, 400, 120, True)
    draw_text(str(draws), BIG, WHITE, 400, 155, True)

    draw_text("AI", SMALL, RED, 635, 120, True)
    draw_text(str(ai_score), BIG, WHITE, 635, 155, True)

    # Current round
    draw_panel(pygame.Rect(45, 205, 710, 115))

    draw_text(
        f"Your move: {player_move or '-'}",
        FONT, BLUE, 75, 225
    )
    draw_text(
        f"AI move: {ai_move or '-'}",
        FONT, RED, 420, 225
    )
    draw_text(message, BIG, result_color, 400, 285, True)

    # AI status and prediction
    draw_panel(pygame.Rect(45, 335, 710, 75))

    if prediction:
        status = f"AI predicted: {prediction}"
        detail = "AI selected its counter before your move."
    else:
        status = "AI is exploring"
        detail = "Not enough patterns yet - playing randomly."

    draw_text(status, FONT, GREEN, 400, 353, True)
    draw_text(detail, SMALL, MUTED, 400, 383, True)

    # Move buttons
    mouse_pos = pygame.mouse.get_pos()

    for move, rect in buttons.items():
        color = BLUE if rect.collidepoint(mouse_pos) else PANEL
        pygame.draw.rect(screen, color, rect, border_radius=12)
        draw_text(move, FONT, WHITE, rect.centerx, rect.centery, True)

    # Recent history
    if recent_results:
        draw_text("Recent rounds", SMALL, MUTED, 45, 495)
        draw_text(recent_results[0], SMALL, WHITE, 185, 495)

    # Reset button
    pygame.draw.rect(
        screen,
        (65, 76, 101),
        reset_button,
        border_radius=10
    )
    draw_text("Reset Game", SMALL, WHITE,
              reset_button.centerx, reset_button.centery, True)

    pygame.display.flip()

pygame.quit()
