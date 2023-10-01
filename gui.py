import pygame
import main
import tkinter as tk
from tkinter import filedialog
import json
import os
import sys

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BACKGROUND_COLOR = (245, 245, 245)
BUTTON_NORMAL_COLOR = (34, 139, 34)
BUTTON_HOVER_COLOR = (0, 100, 0)
BUTTON_PRESSED_COLOR = (46, 87, 46)
AVATARS_DIR = './resources/avatars/'
BUTTON_HEIGHT = 40
BUTTON_PADDING = 20
PROFILE_ICON_SIZE = 50

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WildLogics Launcher")
clock = pygame.time.Clock()
button_sound = pygame.mixer.Sound('./resources/button_press.wav')
background_image = pygame.image.load('./resources/bg.jpg').convert_alpha()

font_path = "./resources/Monocraft.ttf"
title_font = pygame.font.Font(font_path, 34)
button_font = pygame.font.Font(font_path, 20)
input_font = pygame.font.Font(None, 32)

PROFILE_FILE = 'profile.txt'
PROFILE_PICTURE_FILE = 'profile_picture.jpg'
DEFAULT_PICTURE = pygame.image.load('./resources/avatar.jpeg').convert_alpha()

PROFILE_DIR = 'user_profile'  # New Directory for profile data
if not os.path.exists(PROFILE_DIR):
    os.makedirs(PROFILE_DIR)
PROFILE_FILE = os.path.join(PROFILE_DIR, 'profile.json')
PROFILE_PICTURE_FILE = os.path.join(PROFILE_DIR, 'profile_picture.jpg')


def load_profile():
    try:
        with open(PROFILE_FILE, 'r') as file:
            data = json.load(file)
            return data.get('name', "Guest")
    except (FileNotFoundError, json.JSONDecodeError):
        return "Guest"


def save_profile(name):
    try:
        data = {
            'name': name
        }
        with open(PROFILE_FILE, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error while saving profile: {e}")
        raise


def load_profile_picture():
    try:
        return pygame.image.load(PROFILE_PICTURE_FILE).convert_alpha()
    except FileNotFoundError:
        return DEFAULT_PICTURE
def get_avatar_thumbnail(avatar_path, size=(50, 50)):
    img = pygame.image.load(avatar_path)
    img = pygame.transform.scale(img, size)
    return img

def change_picture():
    avatar_files = [f for f in os.listdir(AVATARS_DIR) if os.path.isfile(os.path.join(AVATARS_DIR, f)) and (f.endswith('.jpg') or f.endswith('.png'))]
    avatar_thumbnails = [get_avatar_thumbnail(os.path.join(AVATARS_DIR, f)) for f in avatar_files]
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    menu_width = 300
    menu_height = len(avatar_files) * 50 + 20
    menu_x = (SCREEN_WIDTH - menu_width) // 2
    menu_y = (SCREEN_HEIGHT - menu_height) // 2
    pygame.draw.rect(overlay, (255, 255, 255), (menu_x, menu_y, menu_width, menu_height))
    running = True
    selected_picture = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for index, avatar in enumerate(avatar_files):
                    avatar_rect = pygame.Rect(menu_x, menu_y + index * 50, menu_width, 50)
                    if avatar_rect.collidepoint(event.pos):
                        selected_picture = os.path.join(AVATARS_DIR, avatar)
                        running = False
            if event.type == pygame.QUIT:
                running = False
        screen.blit(background_image, (0, 0))
        screen.blit(overlay, (0, 0))
        for index, avatar_thumbnail in enumerate(avatar_thumbnails):
            avatar_rect = pygame.Rect(menu_x, menu_y + index * 50, menu_width, 50)
            if avatar_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (220, 220, 220), avatar_rect)
            screen.blit(avatar_thumbnail, (avatar_rect.x + 10, avatar_rect.y + 10))
        pygame.display.flip()
        clock.tick(60)
    if selected_picture:
        img = pygame.image.load(selected_picture).convert_alpha()
        pygame.image.save(img, PROFILE_PICTURE_FILE)
        return img
    return None

def draw_button(text, x, y, action=None, width=150):
    text_surface = button_font.render(text, True, (255, 255, 255))
    button_rect = pygame.Rect(x - width/2, y - BUTTON_HEIGHT/2, width, BUTTON_HEIGHT)
    button_hovered = button_rect.collidepoint(pygame.mouse.get_pos())
    
    if button_hovered:
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect)
        if pygame.mouse.get_pressed()[0]:
            pygame.draw.rect(screen, BUTTON_PRESSED_COLOR, button_rect)
            if action:
                action()
    else:
        pygame.draw.rect(screen, BUTTON_NORMAL_COLOR, button_rect)
    
    text_rect = text_surface.get_rect(center=button_rect.center)
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
        profile_hovered = draw_button("Profile", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60)
        
        if profile_hovered and pygame.mouse.get_pressed()[0]:
            while True:  # Continue showing the profile screen until we're done with it.
                done_with_profile = profile_screen()
                if done_with_profile:
                    break
        
        exit_hovered = draw_button("Exit", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 120, action=exit)
        profile_icon = pygame.transform.scale(load_profile_picture(), (PROFILE_ICON_SIZE, PROFILE_ICON_SIZE))
        screen.blit(profile_icon, (SCREEN_WIDTH - PROFILE_ICON_SIZE - 10, 10))
        
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
    pygame.time.wait(200)
    running = True
    name_input = load_profile()
    profile_picture = load_profile_picture()
    picture_rect = profile_picture.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100))
    input_box = pygame.Rect(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 10, 200, 30)
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
            pygame.time.wait(200)  # To prevent unintended clicks.
            profile_picture = change_picture() or profile_picture  # Use the new picture or keep the old one if no picture is selected.
            picture_rect = profile_picture.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100))
            pygame.event.clear()
            continue  # Skip rest of the loop iteration.
        
        save_hovered = draw_button("Save", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 120)
        if save_hovered and pygame.mouse.get_pressed()[0]:
            save_profile(name_input)
            pygame.event.clear()
            return True  # Indicate we are done with the profile screen.
        
        back_hovered = draw_button("Back", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 180)
        if back_hovered and pygame.mouse.get_pressed()[0]:
            pygame.event.clear()
            return False  # Indicate we are not done with the profile screen.

        txt_surface = input_font.render(name_input, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)

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
                        pass
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    else:
                        name_input += event.unicode
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
main_menu()
