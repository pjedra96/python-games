# snake game in python using pygame
import pygame
import time
import argparse
import random

# initialise pygame module
pygame.init()

# initialise all the colours in BGR (they're used by in the game)
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# set width and height variables
width = 500
height  = 400

# set the display mode dimensions using the width and height variables and caption
dis = pygame.display.set_mode((width, height))
pygame.display.set_caption('Python Snake Game')

clock = pygame.time.Clock()

# snake properties
snake_block = 10
snake_speed = 15
high_score = 0

# initialise the font to be used in the game
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 25)

# display the score
def display_score(score):
    global high_score
    # If the current score surpasses the high score, use it as the new high score
    if score >  high_score:
        high_score = score
    
    value = score_font.render("Score: " + str(score) + " High Score: " + str(high_score), True, yellow)
    dis.blit(value, [0, 0])

# draw and extend the snake
def extend_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, black, [x[0], x[1], snake_block, snake_block])
 
def message(msg,color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [width / 6, height/2])

def gameLoop():  # main function    
    # initialise the game over flag and set it to false
    game_over = False
    game_close = False
    
    # location of the snake on start (single square in the middle of the screen)
    x1 = width / 2
    y1 = height / 2
    
    x1_change = 0
    y1_change = 0

    # other snake properties (length, the position of the other squares)
    snake_list = []
    snake_length = 1
 
    # Set the dimensions for snake food squares
    foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, width - snake_block) / 10.0) * 10.0

    while not game_over:
        # If game is finished
        while game_close == True:
            dis.fill(blue)
            message("You Lost! Press C-Play Again or Q-Quit", red)
            display_score(snake_length - 1)
            pygame.display.update()
 
            for event in pygame.event.get():
                # Deal with 'c' and 'q' key press on game over
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        # Deal with key press during the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                game_close = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0


        # If the snake collides with any of the borders, the game is lost
        if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
            game_close = True
    
        x1 += x1_change
        y1 += y1_change

        print(foodx, foody)
        print(x1, y1)

        # set game background color
        dis.fill(blue)
        
        # Draw the food
        pygame.draw.rect(dis, green, [foodx, foody, snake_block, snake_block])
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_list.append(snake_Head)
 
        if len(snake_list) > snake_length:
            del snake_list[0]
 
        # If the snake hits its tail = game lost
        for x in snake_list[:-1]:
            if x == snake_Head:
                game_close = True
 
        extend_snake(snake_block, snake_list)
        display_score(snake_length - 1)
 
        pygame.display.update()
 
        # If snake catches the food draw another square/piece of food
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
            snake_length += 1
 
        clock.tick(snake_speed)
 
    pygame.quit()
    quit()

gameLoop()