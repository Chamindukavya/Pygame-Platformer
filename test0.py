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

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

#Load sprites from the sprite sheet
def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("Assets","Python-Platformer-main","assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("Assets","Python-Platformer-main","assets","Terrain","Terrain.png")
       ## image =  pygame.image.load(join("Assets","Python-Platformer-main","assets","Background",name))

    blocks = pygame.image.load(join(path)).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)  ##(96,0) is the cordinate of the block in the sprite sheet. from that coordinates we get a size * size block
    surface.blit(blocks, (0, 0), rect)##draw the spi=ecified rect part of the blocks to the surface. begin the drawing top left corner of the surface(0,0)

    return pygame.transform.scale2x(surface) ##scale the block to 2x


class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters","VirtualGuy",32,32,True)
    ANIMATION_DELAY = 2

    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.falling_count = 0
        self.jump_count = 0
        
    def jump(self):

        self.y_vel = self.GRAVITY  * (-8)

        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.falling_count = 0 

    def move(self,dx,dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self,vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    
    def move_right(self,vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self,fps):
        self.y_vel += min(1,(self.falling_count/fps)*self.GRAVITY) #increase the falling speed with the falling time
        self.move(self.x_vel,self.y_vel)

        self.update_sprite()

        self.falling_count+=1

    def landed(self):
        self.falling_count = 0
        self.y_vel = 0
        self.jump_count = 0   

    def head(self):
        self.count = 0
        self.y_vel *= -1     #start to move downwards

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.x_vel != 0:
            sprite_sheet = "run"

        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY*2:
            sprite_sheet = "fall"
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]   ##get the sprites from the SPRITES dictionary
        
        ##animation delay is used to slow down the animation. if the delay is 5, then the sprite will change at every 5 frames
        ##animation count will increment at every frame. when we take integer division of the animation count by the ANIMATION_DELAY, we get the sprite index
        ##imagin from int dev we got 5. then the sprite index is 5%len(sprites) = 5. if we got 0, then the sprite index is 0. if we got 6, then the sprite index is 0
        ##this will help to keep the sprite index in the range of the sprites list
        sprite_index = (self.animation_count//self.ANIMATION_DELAY) % len(sprites)  

        self.sprite = sprites[sprite_index]  ##get the sprite from the sprites list

        self.update()

        self.animation_count += 1

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x,self.rect.y)) #define the cordinate of the sprite
        self.mask = pygame.mask.from_surface(self.sprite) #help to make pixel perfect collision. this will bound the sprites to pixel

    def draw(self,win,offset): 
        win.blit(self.sprite,(self.rect.x - offset,self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        # in case of Blocks we can pass x,y like this without using rect
        # self.x = x
        # self.y = y
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win,offset):
        win.blit(self.image, (self.rect.x - offset, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

def get_background(name):
    image =  pygame.image.load(join("Assets","Python-Platformer-main","assets","Background",name))
    _, _, width, height = image.get_rect()

    tiles = []

    ##origin is located at top left corner. there for following calculation is for find positions of the each bg image

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            tiles.append((i * width, j * height))


    return image, tiles

def draw_game(window, image, tiles,player,objects,offset):

    for tile in tiles:
        window.blit(image, tile)

    for obj in objects:
        obj.draw(window,offset)

    player.draw(window,offset)
    pygame.display.update()    ##when there is a change in the display, it will update the displays

def handle_vertical_collision(player,objects,dy):

    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj): #look if player and obj are collide each other
            if dy > 0 : #look whether player is moving down
                player.rect.bottom = obj.rect.top #if player is moving down, then set the bottom of the player rect to the top of the obj rect
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.head()
            collided_objects.append(obj)

    return collided_objects 

def collide(player,objects,dx):
    collide_object = None
    player.move(dx,0)
    player.update()
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            collide_object = obj
            break
    player.move(-dx,0)
    player.update()
    return collide_object           
                
def handle_move(player,objects):

    player.x_vel = 0  #when we once press a key, it will don't stop even we release the key.
                      #Becouse once we updata the x_vel variable player class i will last forever.
    
    collide_left = collide(player,objects,-PLAYER_VEL)
    collide_right = collide(player,objects,PLAYER_VEL)


    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    handle_vertical_collision(player,objects,player.y_vel)    
    
def main(window):

    ##background
    tiles,image = get_background("Blue.png")

    block_size = 96
    offset = 0
    scroll_area_width = 200

    ##player
    player = Player(50,100, 50, 50)

    #floor is made from -width to 2*width. so that the player can move in the x direction
    #floor is array of objects of Block class
    floor = [Block(i*block_size,HEIGHT-block_size,block_size) for i in range(-WIDTH//block_size,(WIDTH*2)//block_size)]

    blocks = [*floor, Block(0, HEIGHT-(block_size*4),block_size),Block(0, HEIGHT-(block_size*2),block_size)]

    # main loop
    run = True
    while run:
        pygame.time.Clock().tick(FPS)    ##control the frame rate
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()    

        player.loop(FPS)   
        handle_move(player,blocks)
        draw_game(window, tiles, image,player,blocks,offset)

        ##scrolling the camera
        if (((player.rect.right-offset >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset <= scroll_area_width )and player.x_vel < 0)):
            offset += player.x_vel

    pygame.quit()
    quit();        

if __name__ == "__main__":
    main(window)