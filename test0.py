import os    ##provide functions to intereact with the OS
import random
import math
import pygame
from os import listdir
from os.path import isfile, join    

pygame.init()   ##initialize the pygame

BG_color = (0, 0, 0)    ##background color
WIDTH, HEIGHT = 1000, 600    ##window size
FPS = 60    ##frames per second
PLAYER_VEL = 5    ##player velocity

window = pygame.display.set_mode((WIDTH, HEIGHT))    ##window size

pygame.display.set_caption("PlatFormer")    ##window title


def get_background(name):
    image =  pygame.image.load(join("Assets","Python-Platformer-main","assets","Background",name))
    _, _, width, height = image.get_rect()

    tiles = []

    ##origin is located at top left corner. there for following calculation is for find positions of the each bg image

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            tiles.append((i * width, j * height))


    return image, tiles


def draw_background(window, image, tiles):

    for title in tiles:
        window.blit(image, title)

    pygame.display.update()    ##update the display



def main(window):
    
    tiles,image = get_background("Blue.png")
    # print ("Tiles   ",tiles)
    # print ("Image   ",image)

    ##draw_background(window, tiles, image)
  

    run = True
    while run:
        pygame.time.Clock().tick(FPS)    ##control the frame rate
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
    pygame.quit()
    quit();        



if __name__ == "__main__":
    main(window)