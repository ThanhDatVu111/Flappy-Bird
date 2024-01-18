import pygame
from pygame.locals import* #all the constants and definitions from the pygame.locals module
                            #are being imported into the current namespace
                            #check for specific keys being pressed or released
import random
pygame.init() #sets up the Pygame modules and prepares them for use in my program.
pygame.mixer.init()

screen_width = 460
screen_height = 750
window_dimension = (screen_width, screen_height)

game_screen = pygame.display.set_mode(window_dimension) #create a window for game
pygame.display.set_caption("꒰ঌ( •ө• )໒꒱ FLAPPY BIRD ꒰ঌ( •ө• )໒꒱") #set the window title

#back_ground and frame_rate set up
game_background = pygame.image.load("graphics/flappy_bg.png")
ground_image = pygame.image.load("graphics/ground1.png")
restart_image = pygame.image.load("graphics/restart.png")
start_image = pygame.image.load("graphics/start.png")

ground_scroll = 0
scroll_speed = 4
game_clock = pygame.time.Clock()
fps = 60

#additional variable
start_flying = False
game_over = False

#pipe variable
pipe_gap = 150
pipe_frequency = 1500 #1.5s
last_pipe_time = pygame.time.get_ticks()

#score variable
score = 0
pass_pipe = False

#define fond and render text function
font = pygame.font.SysFont("bauhaus 93", 60)
white = (255, 255, 255)
def animated_text(text, font, color, x, y):
    text_image = font.render(text, True, color)
    game_screen.blit(text_image, (x,y))

#reset the game when it's end
def reset_game():
	pipe_group.empty()
	flappy_bird.rect.x = 70
	flappy_bird.rect.y = int(screen_height/2)
	reset_score = 0
	return reset_score

# Load the sound
jump_sound = pygame.mixer.Sound("audio/flap.mp3") 
point_sound = pygame.mixer.Sound("audio/point.mp3") 
die_sound = pygame.mixer.Sound("audio/die.mp3") 
hit_sound = pygame.mixer.Sound("audio/hit.mp3") 

#Bird setup
class Bird(pygame.sprite.Sprite): #pygame.sprite.Sprite is a base class for creating sprite objects
    def __init__(bird,x,y):
        pygame.sprite.Sprite.__init__(bird) #Calling the constructor of the Sprite class to initialize the bird instance.
                                            #bird can use the functions and attributes provided by the Sprite class
        bird.images_list = []
        bird.index = 0
        bird.counter = 0
        for i in range(1,4):
            image = pygame.image.load(f"graphics/bird{i}.png")
            bird.images_list.append(image)
        bird.image = bird.images_list[bird.index] #first picture in the list
        bird.rect = bird.image.get_rect()
        bird.rect.center = [x,y]
        bird.velocity = 0
        bird.clicked = False

    def update(bird): 
        #handle gravity
        if start_flying == True:
            bird.velocity += 0.5
            if bird.velocity >= 100: #max velo to hit the ground is 100.0, never go above 100 velo
                bird.velocity = 100
            if bird.rect.bottom < 616: #above ground. Ground start at 616
                bird.rect.y += int(bird.velocity)

        #handle jump effect
        if game_over == False:
            if bird.rect.bottom < 616:  #if the bird is above the ground
                if pygame.mouse.get_pressed()[0] == 1 and bird.clicked == False: #bird.clicked avoid pressing mouse
                    bird.clicked = True
                    bird.velocity -= 11.75 
                    jump_sound.play()            
                if pygame.mouse.get_pressed()[0] == 0: #if mouse release
                    bird.clicked = False
            
            #handle bird animation
            bird.counter += 1
            cooldown = 5 #meaning that the animation will update every 5 frames
            if bird.counter > cooldown:
                bird.counter = 0
                bird.index += 1
                if bird.index == len(bird.images_list):
                    bird.index = 0
            bird.image = bird.images_list[bird.index]

            #handle rotation effect
            if bird.clicked == True:
                bird.image = pygame.transform.rotate(bird.images_list[bird.index], bird.velocity * (-3.0))
        else:
            bird.image = pygame.transform.rotate(bird.images_list[bird.index], -90.0)


#Pipe setup
class Pipe(pygame.sprite.Sprite): #pygame.sprite.Sprite is a base class for creating sprite objects
    def __init__(pipe, x, y, position):
        pygame.sprite.Sprite.__init__(pipe)
        pipe.image = pygame.image.load("graphics/pipe.png") #load pipe picture
        pipe.rect = pipe.image.get_rect() #create dimension for pipe
        #position = 0 => top, position = 1 => bottom
        if position == 0: #top
            pipe.image = pygame.transform.flip(pipe.image, False, True) #image, x, y, flip the pipe
            pipe.rect.bottomleft = [x, y - int(pipe_gap/2)] #pipe location
        if position == 1: #bottom
            pipe.rect.topleft = [x, y + int(pipe_gap/2)] #pipe location
    
    def update(pipe):
        pipe.rect.x -= scroll_speed
        if pipe.rect.right < 0: # if the right of the pipe is already off the screen, delete it
            pipe.kill()

class Button():
	def __init__(button, x, y, image):
		button.image = image
		button.rect = button.image.get_rect()
		button.rect.topleft = (x, y)

	def draw_and_pressed(button):
		action = False
		pos = pygame.mouse.get_pos() #get mouse position
		if button.rect.collidepoint(pos): #if the mouse coordinates fall within button rectangle
			if pygame.mouse.get_pressed()[0] == 1: #if clicked
				action = True
		#draw button
		game_screen.blit(button.image, (button.rect.x, button.rect.y))
		return action


bird_group = pygame.sprite.Group() #this group will be used to manage and handle sprite-related operations for the bird
pipe_group = pygame.sprite.Group() #this group will be used to manage and handle sprite-related operations for the pipe
flappy_bird = Bird(70, int(screen_height/2))
bird_group.add(flappy_bird)
restart_button = Button((screen_width / 2) - 55, (screen_height / 2) - 100, restart_image) #create restart button 

# Load background music
pygame.mixer.music.load("audio/Underwater Theme.mp3")
pygame.mixer.music.play(-1)  # -1 means loop indefinitely

#game loop
die_sound_played = False
hit_sound_played = False
run_time = True

while run_time:
    game_clock.tick(fps) #control the frame rate of the game loop
    game_screen.blit(game_background,(0,0)) #rendering the game background
    bird_group.draw(game_screen) # Drawing all sprites in the bird_group onto game_screen
    bird_group.update() #update the each sprite in the group for the bird
    pipe_group.draw(game_screen) 
    game_screen.blit(ground_image,(ground_scroll,616)) #rendering ground
    if start_flying == False and game_over == False:
        scaled_start_image = pygame.transform.scale(start_image, (230, 100))
        game_screen.blit(scaled_start_image,((screen_width / 2) - 110, (screen_height / 2) - 200))
    
    #set up the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
        and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
        and pass_pipe == False: # check if the bird enter the pipe, between the pipe 
            pass_pipe = True
        if pass_pipe == True: #if already between the pipe
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right: #if the bird pass the right side of the pipe
                score += 1
                point_sound.play()
                pass_pipe = False

    animated_text(str(score), font, white, 215, 20) #draw text

    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy_bird.rect.top < 0: #check if bird collide with pipe, not delete anything
        if hit_sound_played == False:
            hit_sound.play()
            hit_sound_played = True
        game_over = True

    if flappy_bird.rect.bottom > 615: #if bird hit the ground => stop game
        game_over = True
        start_flying = False

    if game_over == False and start_flying == True:
        #genarate new pipe
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > pipe_frequency: #genarate new_pipe every 1.5s
            pipe_rand_height = random.randint(-100,100)
            bottom_pipe = Pipe(screen_width, int(screen_height/2) + pipe_rand_height, 1)
            top_pipe = Pipe(screen_width, int(screen_height/2) + pipe_rand_height, 0)
            pipe_group.add(bottom_pipe, top_pipe)
            last_pipe_time = current_time

        #ground scroll
        ground_scroll -= scroll_speed #the ground is moving to the left 0 -> -4 -> -8 ... 
                                    #creating the effect of moving to the right
        if(abs(ground_scroll) > 36): 
            ground_scroll = 0

        pipe_group.update() #update to actuallt scroll and draw the pipe
        
    #check for game over and reset
    if game_over == True:
        if die_sound_played == False and hit_sound_played == False:
            die_sound.play()
            die_sound_played = True

        if restart_button.draw_and_pressed() == True:
            game_over = False
            die_sound_played = False
            hit_sound_played = False
            score = reset_game() #run reset game and return reset_score to the score
               
    for i in pygame.event.get(): #retrieves all the messages and events that are currently in the event queue
        if i.type == pygame.QUIT:
            run_time = False
        if i.type == pygame.MOUSEBUTTONDOWN and start_flying == False and game_over == False:
            start_flying = True

    pygame.display.update()
pygame.quit() #Pygame modules are properly cleaned up and resources are released to prevent memory leak