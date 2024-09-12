import math
import pygame
import random
import time
import mysql.connector

# Initialize Pygame
pygame.init()

# Game window dimensions
WIDTH, HEIGHT = 1500, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

# Game constants
TARGET_INCREMENT = 400
TARGET_EVENT = pygame.USEREVENT
TARGET_PADDING = 30
BG_COLOR = (255, 187, 255)
LIVES = 3
TOP_BAR_HEIGHT = 50

# Fonts
LABEL_FONT = pygame.font.SysFont("comicsans", 24)
INSTRUCTIONS_FONT = pygame.font.SysFont("comicsans", 30)
BUTTON_FONT = pygame.font.SysFont("comicsans", 40)

# Colors
BUTTON_COLOR = (0, 200, 0)
TARGET_COLOR = (255, 0, 0)
SECONDARY_COLOR = (255, 255, 255)

# Database connection
conn = mysql.connector.connect(host='localhost', password='burrasiri@123', user='root', database='aim')
if conn.is_connected():
    print("Connection established")
cursor = conn.cursor()


# Target class
class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True

    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False
        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE

    def draw(self, win):
        pygame.draw.circle(win, TARGET_COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, SECONDARY_COLOR, (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, TARGET_COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, SECONDARY_COLOR, (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        dis = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return dis <= self.size


# Functions for drawing UI
def draw_instructions_screen():
    # Load the background image
    background_img = pygame.image.load("bg.jpg")

    # Scale the image to fit the window dimensions
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

    WIN.blit(background_img, (0, 0))  # Draw the background image

    instructions_text = [
        "Welcome to Aim Trainer!",
        "Instructions:",
        "1. Click on targets before they disappear.",
        "2. You have 3 lives. Missing a target reduces lives.",
        "3. Click 'Start Game' to begin.",
    ]
    y_offset = 50
    for text in instructions_text:
        text_surface = INSTRUCTIONS_FONT.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(left=50, top=y_offset)  # Align text to the left
        WIN.blit(text_surface, text_rect)
        y_offset += 40

    start_button = pygame.Rect(50, HEIGHT // 2 + 50, 250, 50)  # Align button to the left
    pygame.draw.rect(WIN, BUTTON_COLOR, start_button)
    start_button_text = BUTTON_FONT.render("Start Game", True, (0, 0, 0))
    text_rect = start_button_text.get_rect(center=start_button.center)
    WIN.blit(start_button_text, text_rect)


def draw(win, targets):
    win.fill(BG_COLOR)
    for target in targets:
        target.draw(win)


def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)
    return f"{minutes:02d}:{seconds:02d}.{milli}"


def draw_top_bar(win, elapsed_time, targets_pressed, misses):
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))
    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "black")
    speed = round(targets_pressed / elapsed_time, 1)
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")
    lives_label = LABEL_FONT.render(f"Lives: {LIVES - misses}", 1, "black")
    win.blit(time_label, (5, 5))
    win.blit(speed_label, (200, 5))
    win.blit(hits_label, (450, 5))
    win.blit(lives_label, (650, 5))


def user_scores(elapsed_time, speed, targets_pressed, accuracy):
    try:
        cursor.execute('''INSERT INTO userscores (time, speed, hits, accuracy) VALUES (%s, %s, %s, %s)''',
                       (elapsed_time, speed, targets_pressed, accuracy))
        conn.commit()
        print("Data Sent")
    except Exception as e:
        print("Data not sent:", e)


def end_screen(win, elapsed_time, targets_pressed, clicks):
    # Load the background image
    background_img = pygame.image.load("bg.jpg")

    # Scale the image to fit the window dimensions
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

    win.blit(background_img, (0, 0))  # Draw the background image

    time_label = LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", 1, "black")
    if clicks > 0:
        speed = round(targets_pressed / elapsed_time, 1)
        accuracy = round(targets_pressed / clicks * 100, 1)
    else:
        speed = 0
        accuracy = 0
    speed_label = LABEL_FONT.render(f"Speed: {speed} t/s", 1, "black")
    hits_label = LABEL_FONT.render(f"Hits: {targets_pressed}", 1, "black")
    accuracy_label = LABEL_FONT.render(f"Accuracy: {accuracy}%", 1, "black")

    # Adjust x-coordinates for left alignment
    label_x = 50

    win.blit(time_label, (label_x, 100))
    win.blit(speed_label, (label_x, 200))
    win.blit(hits_label, (label_x, 300))
    win.blit(accuracy_label, (label_x, 400))

    button_width = 200
    button_height = 50
    button_padding = 20
    button_radius = 10  # Radius for rounded corners

    # Adjust x-coordinates for left alignment
    play_again_button_x = 50
    quit_button_x = 50 + button_width + button_padding

    play_again_button = pygame.Rect(play_again_button_x, HEIGHT // 2 + 80, button_width, button_height)
    pygame.draw.rect(WIN, (85, 107, 47), play_again_button, border_radius=button_radius)
    play_again_text = BUTTON_FONT.render("Play Again", True, (0, 0, 0))
    play_again_text_rect = play_again_text.get_rect(center=play_again_button.center)
    WIN.blit(play_again_text, play_again_text_rect)

    quit_button = pygame.Rect(quit_button_x, HEIGHT // 2 + 80, button_width, button_height)
    pygame.draw.rect(WIN, (85, 107, 47), quit_button, border_radius=button_radius)
    quit_text = BUTTON_FONT.render("Quit", True, (0, 0, 0))
    quit_text_rect = quit_text.get_rect(center=quit_button.center)
    WIN.blit(quit_text, quit_text_rect)

    pygame.display.update()

    run = True
    user_scores(elapsed_time, speed, targets_pressed, accuracy)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_again_button.collidepoint(mouse_pos):
                    start_game()
                    return True  # Return True to indicate restarting the game
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    return False  # Return False to indicate quitting the game
    return False  # Default to False if no action is taken


def start_game():
    # Reset all game variables
    targets = []
    clock = pygame.time.Clock()
    targets_pressed = 0
    clicks = 0
    misses = 0
    start_time = time.time()
    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    # Set a variable to track the time since the last interaction
    last_interaction_time = time.time()

    while True:
        clock.tick(60)
        click = False
        mouse_pos = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time

        # Check if the user hasn't interacted for more than 10 seconds
        if time.time() - last_interaction_time > 10:
            return end_screen(WIN, elapsed_time, targets_pressed, clicks)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                target = Target(x, y)
                targets.append(target)

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1  # Increment clicks whenever mouse is clicked

                # Update the last interaction time when the user clicks
                last_interaction_time = time.time()

        for target in targets:
            target.update()

            if target.size <= 0:
                targets.remove(target)
                misses += 1

            if click and target.collide(*mouse_pos):
                targets.remove(target)
                targets_pressed += 1

        if misses >= LIVES:
            return end_screen(WIN, elapsed_time, targets_pressed, clicks)

        draw(WIN, targets)
        draw_top_bar(WIN, elapsed_time, targets_pressed, misses)
        pygame.display.update()


def main():
    instructions_screen = True
    game_running = False

    # Initialize Pygame display
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if instructions_screen:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    start_button = pygame.Rect(50, HEIGHT // 2 + 50, 250, 50)
                    if start_button.collidepoint(mouse_pos):
                        instructions_screen = False
                        game_running = True
                        start_game()

            if not game_running:  # Check if the game is not running
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    play_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 50)
                    if play_again_button.collidepoint(mouse_pos):
                        instructions_screen = False  # Set instructions_screen to False
                        game_running = True  # Set game_running to True to start the game
                        start_game()  # Start the game again when play again button is clicked
                    quit_button = pygame.Rect(WIDTH // 2 + 150, HEIGHT // 2 + 150, 200, 50)
                    if quit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        return

        if instructions_screen:
            draw_instructions_screen()

        pygame.display.update()


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()