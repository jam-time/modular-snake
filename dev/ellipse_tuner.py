"""Interactive ellipse tuner for snake head shape."""

import pygame

pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption('Ellipse Tuner - Number keys to select ellipse')
clock = pygame.time.Clock()

radius = 150
center = (500, 350)

ellipses = [
    {'width': 300, 'height': 132, 'y_offset': -144},
    {'width': 273, 'height': 126, 'y_offset': -108},
    {'width': 246, 'height': 117, 'y_offset': -72},
    {'width': 219, 'height': 105, 'y_offset': -36},
    {'width': 192, 'height': 93, 'y_offset': 0},
    {'width': 165, 'height': 78, 'y_offset': 36},
    {'width': 138, 'height': 60, 'y_offset': 72},
    {'width': 111, 'height': 42, 'y_offset': 108},
    {'width': 84, 'height': 21, 'y_offset': 144},
]

selected_ellipse = 0
selected_param = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                selected_ellipse = 0
            elif event.key == pygame.K_2:
                selected_ellipse = 1
            elif event.key == pygame.K_3:
                selected_ellipse = 2
            elif event.key == pygame.K_4:
                selected_ellipse = 3
            elif event.key == pygame.K_5:
                selected_ellipse = 4
            elif event.key == pygame.K_6:
                selected_ellipse = 5
            elif event.key == pygame.K_7:
                selected_ellipse = 6
            elif event.key == pygame.K_8:
                selected_ellipse = 7
            elif event.key == pygame.K_9:
                selected_ellipse = 8
            elif event.key == pygame.K_q:
                selected_param = 0
            elif event.key == pygame.K_w:
                selected_param = 1
            elif event.key == pygame.K_e:
                selected_param = 2

    keys = pygame.key.get_pressed()
    adjust = 1
    
    if keys[pygame.K_UP]:
        if selected_param == 0:
            ellipses[selected_ellipse]['width'] += adjust
        elif selected_param == 1:
            ellipses[selected_ellipse]['height'] += adjust
        elif selected_param == 2:
            ellipses[selected_ellipse]['y_offset'] -= adjust
    
    if keys[pygame.K_DOWN]:
        if selected_param == 0:
            ellipses[selected_ellipse]['width'] -= adjust
        elif selected_param == 1:
            ellipses[selected_ellipse]['height'] -= adjust
        elif selected_param == 2:
            ellipses[selected_ellipse]['y_offset'] += adjust

    screen.fill((20, 20, 30))

    base_color = (70, 220, 70, 180)

    for i, ellipse in enumerate(ellipses):
        color = base_color
        
        temp_surface = pygame.Surface((ellipse['width'], ellipse['height']), pygame.SRCALPHA)
        temp_rect = pygame.Rect(0, 0, ellipse['width'], ellipse['height'])
        pygame.draw.ellipse(temp_surface, color, temp_rect)
        
        if i == selected_ellipse:
            pygame.draw.ellipse(temp_surface, (255, 255, 0, 255), temp_rect, 3)
        
        screen.blit(temp_surface, (
            int(center[0] - ellipse['width'] / 2),
            int(center[1] - ellipse['height'] / 2 + ellipse['y_offset'])
        ))

    font = pygame.font.Font(None, 24)
    params = ['width', 'height', 'y_offset']
    y = 10
    text = font.render(f'Ellipse {selected_ellipse + 1}/9 (keys 1-9)', True, (255, 255, 0))
    screen.blit(text, (10, y))
    y += 30
    
    for i, param in enumerate(params):
        value = ellipses[selected_ellipse][param]
        color = (255, 255, 0) if i == selected_param else (255, 255, 255)
        text = font.render(f'{param}: {value}', True, color)
        screen.blit(text, (10, y))
        y += 25

    info1 = font.render('1-9: Select ellipse | Q/W/E: width/height/y_offset', True, (150, 150, 150))
    info2 = font.render('UP/DOWN: Adjust | SHIFT: Fine tune', True, (150, 150, 150))
    screen.blit(info1, (10, 640))
    screen.blit(info2, (10, 665))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print('\nFinal ellipse values:')
for i, e in enumerate(ellipses):
    print(f"    {{'width': {e['width']}, 'height': {e['height']}, 'y_offset': {e['y_offset']}}},  # Layer {i}")
