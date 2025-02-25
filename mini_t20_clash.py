import pygame
import random
import time
import os

# Initialize Pygame
pygame.init()
print("Pygame initialized")
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Over: India vs Australia")
clock = pygame.time.Clock()

# Colors
WHITE, BLACK, BLUE, YELLOW = (255, 255, 255), (0, 0, 0), (0, 0, 255), (255, 255, 0)
FIELD_GREEN, PITCH_YELLOW, RED = (34, 139, 34), (180, 140, 80), (255, 0, 0)
ORANGE, CYAN = (255, 165, 0), (0, 255, 255)

# Fonts
font = pygame.font.SysFont("Arial", 24)
score_font = pygame.font.SysFont("Arial", 20)
ball_font = pygame.font.SysFont("Arial", 18)

# Base directory for relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load images
print("Loading images...")
try:
    background = pygame.image.load(os.path.join(BASE_DIR, "dharamshala.png"))
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    background = None
    print("No background, using green.")

try:
    bowler_frames = [pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, f"bowler{i}.png")), (40, 80)) for i in range(1, 11)]
    batsman_frames = [pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, f"batsman{i}.png")), (40, 80)) for i in range(1, 9)]
    umpire_img = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "umpire.png")), (40, 80))
except Exception as e:
    print(f"Error loading sprites: {e}")
    pygame.quit()
    exit()

# Initial screen
print("Showing initial window...")
screen.fill(FIELD_GREEN if not background else (0, 0, 0))
if background:
    screen.blit(background, (0, 0))
pygame.display.flip()
time.sleep(0.5)

# Teams
india_batsmen = ["Rohit Sharma", "Shubman Gill", "Virat Kohli", "Shreyas Iyer", "Rishabh Pant"]
india_bowlers = ["Mohammed Shami", "Arshdeep Singh", "Kuldeep Yadav"]
aus_batsmen = ["Travis Head", "Steve Smith", "Marnus Labuschagne", "Glenn Maxwell", "Josh Inglis"]
aus_bowlers = ["Sean Abbott", "Nathan Ellis", "Adam Zampa"]

# Game state
runs, wickets, overs = 0, 0, 0
max_wickets = 2
current_batsman_idx = 0
current_bowler_idx = 0
target = 0
first_innings_balls = []
second_innings_balls = []

# Radio button helper
def draw_radio_buttons(options, selected, x, y, prompt):
    pygame.draw.rect(screen, WHITE, (x - 20, y - 20, 400, 50 + len(options) * 40))
    prompt_text = font.render(prompt, True, BLACK)
    screen.blit(prompt_text, (x, y))
    buttons = []
    for i, option in enumerate(options):
        pygame.draw.circle(screen, CYAN if i == selected else BLACK, (x + 20, y + 50 + i * 40), 10)
        option_text = score_font.render(option, True, BLACK)
        screen.blit(option_text, (x + 40, y + 45 + i * 40))
        buttons.append((x + 20 - 10, y + 50 + i * 40 - 10, 20, 20))
    pygame.display.flip()
    return buttons

def get_radio_selection(options, prompt):
    print(f"Showing selection for: {prompt}")
    selected = 0
    x, y = WIDTH//2 - 200, HEIGHT//2 - len(options) * 20 - 50
    buttons = draw_radio_buttons(options, selected, x, y, prompt)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i, (bx, by, bw, bh) in enumerate(buttons):
                    if bx <= mx <= bx + bw and by <= my <= by + bh:
                        selected = i
                        draw_radio_buttons(options, selected, x, y, prompt)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                print(f"Selected: {options[selected]}")
                return selected
        clock.tick(60)

# Random outcome generator
def get_outcome(bowler):
    is_pace = bowler in ["Mohammed Shami", "Arshdeep Singh", "Sean Abbott", "Nathan Ellis"]
    wicket_chance = 17 if is_pace else 15
    six_chance = 15
    roll = random.randint(1, 100)
    if roll <= 20: return "0"
    elif roll <= 45: return "1"
    elif roll <= 60: return "2"
    elif roll <= 75: return "4"
    elif roll <= (75 + six_chance): return "6"
    else: return "W"

# Draw function
def draw_game(team_batting, batsman, bowler, score, over, ball, result, is_second_innings=False, frame=0):
    print(f"Drawing: {bowler} to {batsman} - Frame {frame}")
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(FIELD_GREEN)
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 100))

    pitch_x, pitch_y = WIDTH//2 - 81, HEIGHT - 30
    pitch_points = [(pitch_x, pitch_y), (pitch_x + 162, pitch_y), 
                    (pitch_x + 135, pitch_y - 302), (pitch_x + 27, pitch_y - 302)]
    pygame.draw.polygon(screen, PITCH_YELLOW, pitch_points)

    for x in [pitch_x + 74, pitch_x + 81, pitch_x + 88]:
        pygame.draw.rect(screen, WHITE, (x, pitch_y - 30, 4, 30))
    for x in [pitch_x + 64, pitch_x + 71, pitch_x + 78]:
        pygame.draw.rect(screen, WHITE, (x, pitch_y - 292, 4, 20))

    umpire_x, umpire_y = pitch_x + 71, pitch_y - 20
    screen.blit(umpire_img, (umpire_x, umpire_y))

    bowler_x = pitch_x + 91
    bowler_y = pitch_y + 20 - frame * 10
    screen.blit(bowler_frames[frame], (bowler_x, bowler_y))

    batsman_x, batsman_y = pitch_x + 61, pitch_y - 312
    if result in ["4", "6"]:
        if frame < 6:
            screen.blit(batsman_frames[0], (batsman_x, batsman_y))
        else:
            batsman_frame = frame - 6
            screen.blit(batsman_frames[batsman_frame], (batsman_x, batsman_y))
    else:
        screen.blit(batsman_frames[0], (batsman_x, batsman_y))

    ball_x, ball_y = pitch_x + 81, pitch_y - 151
    if result == "1" or result == "2":
        pygame.draw.circle(screen, WHITE, (ball_x + 30, ball_y + 30), 5)
    elif result == "4":
        pygame.draw.circle(screen, WHITE, (ball_x + 120, ball_y + 120), 5)
    elif result == "6":
        pygame.draw.circle(screen, WHITE, (ball_x + 180, ball_y - 180), 5)
    elif result == "W":
        pygame.draw.circle(screen, WHITE, (ball_x, ball_y + 60), 5)
    else:
        pygame.draw.circle(screen, WHITE, (ball_x, ball_y), 5)

    action_text = font.render(f"{bowler} to {batsman}: {result}", True, RED)
    screen.blit(action_text, (10, 40))

    overs_display = f"{over}.{ball}/1"
    if is_second_innings:
        balls_left = (6 - (over * 6 + ball))
        runs_needed = target - score if target > score else 0
        ticker_text = f"{team_batting}: {score}/{wickets} ({overs_display}) | Target: {target} | Needs {runs_needed} in {balls_left}"
    else:
        ticker_text = f"{team_batting}: {score}/{wickets} ({overs_display})"
    ticker = score_font.render(ticker_text, True, ORANGE)
    screen.blit(ticker, (WIDTH - ticker.get_width() - 10, 10))

    first_balls_str = " ".join(first_innings_balls) if first_innings_balls else ""
    second_balls_str = " ".join(second_innings_balls) if second_innings_balls else ""
    ball_text = f"{first_balls_str}{'      ' if first_balls_str else ''}{second_balls_str}"
    ball_display = ball_font.render(ball_text, True, WHITE)
    screen.blit(ball_display, (WIDTH - ball_display.get_width() - 10, 40))

    pygame.display.flip()

# Play innings
def play_innings(team_batting, batsmen, opponent_bowlers, ball_list):
    global runs, wickets, overs, current_batsman_idx, current_bowler_idx, target
    runs, wickets, overs = 0, 0, 0
    current_batsman_idx = 0
    current_bowler_idx = 0
    is_second_innings = (target > 0)
    
    print(f"Starting innings for {team_batting}...")
    for over in range(1):
        bowler = opponent_bowlers[current_bowler_idx % len(opponent_bowlers)]
        current_bowler_idx += 1
        for ball in range(6):
            if wickets >= max_wickets:
                break
            batsman = batsmen[current_batsman_idx % len(batsmen)]
            result = get_outcome(bowler)
            ball_list.append("W" if result == "W" else result if result != "0" else ".")
            frames = 10
            for frame in range(frames):
                draw_game(team_batting, batsman, bowler, runs, over, ball + 1, result, is_second_innings, frame)
                pygame.event.pump()
                time.sleep(0.05 if frame < 5 else 0.025)
            if result == "W":
                wickets += 1
                current_batsman_idx += 1
            elif result != "0":
                runs += int(result)
            draw_game(team_batting, batsman, bowler, runs, over, ball + 1, result, is_second_innings, frames - 1)
            print(f"{team_batting} - {bowler} to {batsman}: {result}")
            pygame.event.pump()
            time.sleep(0.5)
            # Check if second team has won
            if is_second_innings and runs >= target:
                print(f"{team_batting} wins after {over}.{ball + 1} balls!")
                return runs, wickets  # Exit early if target is overhauled
        overs += 1
    return runs, wickets

# User input graphical functions
def get_user_team():
    options = ["India", "Australia"]
    selected = get_radio_selection(options, "Choose your team:")
    return options[selected], options[1 - selected]

def get_toss_call():
    options = ["Heads", "Tails"]
    selected = get_radio_selection(options, "Call the toss:")
    return "H" if selected == 0 else "T"

def get_toss_decision():
    options = ["Bat", "Bowl"]
    selected = get_radio_selection(options, "You won the toss! Choose:")
    return "B" if selected == 0 else "F"

def get_batsmen(user_team_batsmen):
    selected = get_radio_selection(user_team_batsmen, "Select your first batsman:")
    first = user_team_batsmen.pop(selected)
    selected = get_radio_selection(user_team_batsmen, "Select your second batsman:")
    second = user_team_batsmen.pop(selected)
    return [first, second] + user_team_batsmen

def get_bowler(user_team_bowlers):
    selected = get_radio_selection(user_team_bowlers, "Select your bowler:")
    return [user_team_bowlers[selected]]

# Main game loop
def play_game():
    global target, first_innings_balls, second_innings_balls
    running = True
    first_innings_balls = []
    second_innings_balls = []

    # User picks team
    user_team, cpu_team = get_user_team()
    user_batsmen = india_batsmen if user_team == "India" else aus_batsmen
    cpu_batsmen = aus_batsmen if user_team == "India" else india_batsmen
    user_bowlers = india_bowlers if user_team == "India" else aus_bowlers
    cpu_bowlers = aus_bowlers if user_team == "India" else india_bowlers

    # Toss
    user_call = get_toss_call()
    toss_result = random.choice(["H", "T"])
    user_won_toss = user_call == toss_result
    print(f"Toss: {'Heads' if toss_result == 'H' else 'Tails'} - {user_team if user_won_toss else cpu_team} wins!")

    # Decide batting order
    if user_won_toss:
        decision = get_toss_decision()
        user_bats_first = decision == "B"
    else:
        user_bats_first = random.choice([True, False])
    batting_team = user_team if user_bats_first else cpu_team
    bowling_team = cpu_team if user_bats_first else user_team
    print(f"{batting_team} bats first.")

    # User picks batsmen or bowler
    if user_bats_first:
        selected_batsmen = get_batsmen(user_batsmen.copy())
        first_team_batsmen = selected_batsmen
        first_team_bowlers = cpu_bowlers
        second_team_batsmen = cpu_batsmen
        second_team_bowlers = get_bowler(user_bowlers.copy())
    else:
        selected_bowler = get_bowler(user_bowlers.copy())
        first_team_batsmen = cpu_batsmen
        first_team_bowlers = selected_bowler
        second_team_batsmen = get_batsmen(user_batsmen.copy())
        second_team_bowlers = cpu_bowlers

    # Play innings
    first_score, first_wickets = play_innings(batting_team, first_team_batsmen, first_team_bowlers, first_innings_balls)
    target = first_score + 1
    second_score, second_wickets = play_innings(bowling_team, second_team_batsmen, second_team_bowlers, second_innings_balls)

    # Results with both innings (preserve top-right)
    first_team = batting_team
    second_team = bowling_team
    result_text = f"{first_team}: {first_score}/{first_wickets}\n{second_team}: {second_score}/{second_wickets}\nResult: {first_team if first_score > second_score else second_team} wins by {abs(first_score - second_score)} runs!"
    print(result_text)
    
    # Draw only the top-left results over the last frame
    pygame.draw.rect(screen, BLACK, (0, 0, 200, 100))  # Small black box for results
    lines = result_text.split('\n')
    for i, line in enumerate(lines):
        text = font.render(line, True, YELLOW if i < 2 else CYAN)
        screen.blit(text, (10, 10 + i * 40))
    pygame.display.flip()

    # Wait for input
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_p:
                    return True
        clock.tick(60)

# Run game
print("Starting game...")
while True:
    if not play_game():
        break
    target = 0

pygame.quit()
print("Game ended.")