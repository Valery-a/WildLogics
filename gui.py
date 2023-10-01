import pygame
import main
import tkinter as tk
from tkinter import filedialog

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BUTTON_NORMAL_COLOR = (34, 139, 34)
BUTTON_HOVER_COLOR = (0, 100, 0)
BUTTON_PRESSED_COLOR = (46, 87, 46)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WildLogics Launcher")
clock = pygame.time.Clock()
button_sound = pygame.mixer.Sound('./resources/button_press.wav')
background_image = pygame.image.load('./resources/bg.jpg').convert_alpha()

font_path = "./resources/Monocraft.ttf"
title_font = pygame.font.Font(font_path, 34)
button_font = pygame.font.Font(font_path, 24)
input_font = pygame.font.Font(None, 32)

PROFILE_FILE = 'profile.txt'
PROFILE_PICTURE_FILE = 'profile_picture.jpg'
DEFAULT_PICTURE = pygame.image.load('./resources/avatar.jpeg').convert_alpha()

def load_profile():
    try:
        with open(PROFILE_FILE, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Guest"

def save_profile(name):
    with open(PROFILE_FILE, 'w') as file:
        file.write(name)

def load_profile_picture():
    try:
        return pygame.image.load(PROFILE_PICTURE_FILE).convert_alpha()
    except FileNotFoundError:
        return DEFAULT_PICTURE

def change_picture():
    pygame.quit()  # Quit pygame temporarily
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
    root.destroy()  # Ensure tkinter is fully closed
    if file_path:
        img = pygame.image.load(file_path).convert_alpha()
        pygame.image.save(img, PROFILE_PICTURE_FILE)
    pygame.init()  # Re-initialize pygame
def draw_button(text, x, y, action=None):
    text_surface = button_font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(x, y))
    button_rect = text_rect.inflate(20, 10)
    button_hovered = button_rect.collidepoint(pygame.mouse.get_pos())
    if button_hovered:
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect)
        if pygame.mouse.get_pressed()[0]:
            pygame.draw.rect(screen, BUTTON_PRESSED_COLOR, button_rect)
            if action:
                action()
    else:
        pygame.draw.rect(screen, BUTTON_NORMAL_COLOR, button_rect)
    screen.blit(text_surface, text_rect)
    return button_hovered

def main_menu():
    running = True
    while running:
        screen.blit(background_image, (0, 0))
        title_text = title_font.render('WildLogics Launcher', True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        screen.blit(title_text, title_rect)
        play_hovered = draw_button("Play", SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        profile_hovered = draw_button("Profile", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50, action=profile_screen)
        exit_hovered = draw_button("Exit", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100, action=exit)
        if play_hovered and pygame.mouse.get_pressed()[0]:
            button_sound.play()
            main.run_game()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

def profile_screen():
    running = True
    name_input = load_profile()
    profile_picture = load_profile_picture()
    picture_rect = profile_picture.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100))
    input_box = pygame.Rect(SCREEN_WIDTH/2 - 70, SCREEN_HEIGHT/2 + 10, 140, 30)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    while running:
        screen.blit(background_image, (0, 0))
        title_text = title_font.render('Profile', True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        screen.blit(title_text, title_rect)
        screen.blit(profile_picture, picture_rect)
        pygame.draw.rect(screen, (255, 255, 255), picture_rect, 3)
        change_picture_hovered = draw_button("Change Picture", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60)
        if change_picture_hovered and pygame.mouse.get_pressed()[0]:
            change_picture()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        save_profile(name_input)
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    else:
                        name_input += event.unicode
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
        txt_surface = input_font.render(name_input, True, color)
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)
        back_hovered = draw_button("Back", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 150, action=main_menu)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()