import pygame
import pygame_gui
import main  # Your game file

pygame.init()

SCREEN_WIDTH = 800  # You can adjust this as needed
SCREEN_HEIGHT = 600  # You can adjust this as needed

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WildLogics Launcher")
clock = pygame.time.Clock()

# Initialize GUI Manager
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((SCREEN_WIDTH/2 - 70, SCREEN_HEIGHT/2 - 15), (140, 30)),
                                            text='Play',
                                            manager=manager)

game_started = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    main.run_game()
                    game_started = True

        manager.process_events(event)

    manager.update(time_delta=1/60.0)

    screen.fill((0, 0, 0))
    manager.draw_ui(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
