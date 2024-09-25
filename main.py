import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import numpy

# Function to check collision
def check_collision(x1, y1, width1, height1, x2, y2, width2, height2):
    return (x1 < x2 + width2 and x1 + width1 > x2 and y1 < y2 + height2 and y1 + height1 > y2)


# Game settings
width, height = 800, 600
num_meteors = 11
player_position = [width//2, 50]
player_size =[40,40]
meteor_size=[40,40]
meteors = [[random.randint(0, width), height, meteor_size[0], meteor_size[1]] for _ in range(num_meteors)]
bullets = []
score = 0
key_states = {"left": False, "right": False}
bullet_cooldown = 0
bullet_cooldown_max = 10  # Frames until next bullet can be fired
pygame.font.init()  # Initialize the font module
game_over_font = pygame.font.Font(None, 74)  # You can replace None with a path to a .ttf file


# Initialize Pygame and OpenGL
pygame.init()
display = pygame.display.set_mode((width, height), DOUBLEBUF|OPENGL)
glDisable(GL_DEPTH_TEST)
glDisable(GL_BLEND)
gluOrtho2D(0, width, 0, height)


# Load an image
spaceship_image = pygame.image.load('images/spaceship.png')
spaceship_texture = pygame.image.tostring(spaceship_image, "RGBA", 1)

bullet_image = pygame.image.load('images/effect_yellow_bullet.png')
bullet_texture = pygame.image.tostring(bullet_image, "RGBA", 1)

meteor_image = pygame.image.load('images/meteor_squareDetailedSmall.png')
meteor_texture = pygame.image.tostring(meteor_image, "RGBA", 1)

# Load a sound
#shoot_sound = pygame.mixer.Sound('GAME01/sounds/shoot.wav')

# Load Texture Function
def load_texture(image):
    glEnable(GL_TEXTURE_2D)
    texid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texid)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(image, "RGBA", 1))
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return texid

spaceship_texture_id = load_texture(spaceship_image)
bullet_texture_id = load_texture(bullet_image)
meteor_texture_id = load_texture(meteor_image)

def draw_spaceship(): #Draws the spaceship using quadrilaterals at the player's current position.
    glBindTexture(GL_TEXTURE_2D, spaceship_texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(player_position[0] - 20, player_position[1] - 20)
    glTexCoord2f(1, 0); glVertex2f(player_position[0] + 20, player_position[1] - 20)
    glTexCoord2f(1, 1); glVertex2f(player_position[0] + 20, player_position[1] + 20)
    glTexCoord2f(0, 1); glVertex2f(player_position[0] - 20, player_position[1] + 20)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)  # Unbind texture
    glColor3f(1, 1, 1)  # Reset color to white

def draw_meteor(x, y): #Draws a meteor as a triangle at the specified coordinates.
    glBindTexture(GL_TEXTURE_2D, meteor_texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x - 20, y - 20)  # Adjusted for 40x40 size
    glTexCoord2f(1, 0); glVertex2f(x + 20, y - 20)
    glTexCoord2f(1, 1); glVertex2f(x + 20, y + 20)
    glTexCoord2f(0, 1); glVertex2f(x - 20, y + 20)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)

def draw_bullet(x, y): #Draws a bullet as a small rectangle.
    glBindTexture(GL_TEXTURE_2D, bullet_texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x - 5, y - 15)  # Adjusted for 10x30 size
    glTexCoord2f(1, 0); glVertex2f(x + 5, y - 15)
    glTexCoord2f(1, 1); glVertex2f(x + 5, y + 15)
    glTexCoord2f(0, 1); glVertex2f(x - 5, y + 15)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)

def draw_bullet_bar(): #Draws a horizontal red bar that visualizes the bullet cooldown status.
    glPushMatrix()
    glTranslate(width - 110, height - 20, 0)
    glBegin(GL_QUADS)
    glColor3f(1, 0, 0)  # Red bar
    glVertex2f(0, 0)
    glVertex2f(100 * (1 - bullet_cooldown / bullet_cooldown_max), 0)
    glVertex2f(100 * (1 - bullet_cooldown / bullet_cooldown_max), 10)
    glVertex2f(0, 10)
    glEnd()
    glPopMatrix()


#The following functions are used to update the game's state
def update_meteors():
    global score
    for meteor in meteors[:]:  # Use a slice copy for safe removal during iteration
        meteor[1] -= 2  # Meteor speed
        if meteor[1] < 0:  # If a meteor goes below the screen, replace it
            meteors.remove(meteor)
            meteors.append([random.randint(0, width), height, meteor_size[0], meteor_size[1]])
        for bullet in bullets[:]:  # Check collisions between meteors and bullets
            if bullet[1] >= meteor[1] and abs(bullet[0] - meteor[0]) < 20:
                bullets.remove(bullet)
                meteors.remove(meteor)
                score += 1  # Update score
                meteors.append([random.randint(0, width), height, meteor_size[0], meteor_size[1]])
                print("Score:", score)



#--------------------------------------------------------------------------
#Moves each bullet up the screen. Bullets that move off-screen are removed.
def update_bullets():
    for bullet in bullets:
        bullet[1] += 1  # Bullet speed
        if bullet[1] > height:
            bullets.remove(bullet)
#--------------------------------------------------------------------------
#This is the central loop where the game's logic executes repeatedly:
def game_loop():
    game_over=False
    bullet_cooldown=30  # Add bullet_cooldown here
    running = True
    while running:
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT) # Clears the screen for new drawing

        if not game_over:
            # Handle continuous key presses
            if key_states["left"]:
                player_position[0] = max(20, player_position[0] - 10)
            if key_states["right"]:
                player_position[0] = min(width - 20, player_position[0] + 10)

            # Draw spaceship, meteors, and bullets
            draw_spaceship()
            for meteor in meteors:
                draw_meteor(meteor[0], meteor[1])
                if check_collision(player_position[0], player_position[1], player_size[0], player_size[1],
                                   meteor[0], meteor[1], meteor[2], meteor[3]):
                    game_over = True
                    print("Game Over!")
                    break

            for bullet in bullets:
                draw_bullet(bullet[0], bullet[1])

            # Update meteors and bullets
            update_meteors()
            update_bullets()

            # Reduce the bullet cooldown if greater than zero
            if bullet_cooldown > 0:
                bullet_cooldown -= 1
        else:
            draw_game_over()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    key_states["left"] = True
                elif event.key == pygame.K_RIGHT:
                    key_states["right"] = True
                elif event.key == pygame.K_SPACE:
                    if bullet_cooldown == 0:
                        bullets.append([player_position[0], player_position[1] + 20])
                        bullet_cooldown = bullet_cooldown_max  # Reset cooldown
                        print("Bullet fired:", bullets)  # Debugging output

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    key_states["left"] = False
                elif event.key == pygame.K_RIGHT:
                    key_states["right"] = False

        pygame.display.flip()
        pygame.time.wait(10)


    pygame.quit()

def render_game_over_text():
    text_surface = game_over_font.render('Game Over', True, (255, 0, 0))  # Red color
    text_data = pygame.image.tostring(text_surface, "RGBA", 1)
    text_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, text_texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_surface.get_width(), text_surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return text_texture, text_surface.get_width(), text_surface.get_height()


def draw_game_over():
    text_texture, width, height = render_game_over_text()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, text_texture)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f((800 - width) / 2, (600 - height) / 2 + height)
    glTexCoord2f(1, 0); glVertex2f((800 - width) / 2 + width, (600 - height) / 2 + height)
    glTexCoord2f(1, 1); glVertex2f((800 - width) / 2 + width, (600 - height) / 2)
    glTexCoord2f(0, 1); glVertex2f((800 - width) / 2, (600 - height) / 2)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)


game_loop()


game_loop()
