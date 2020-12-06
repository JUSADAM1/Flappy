import pygame
import random
import os
import time
import neat
import pickle
pygame.font.init()  # init font

# Loading up the images and setting up size of the screen
# Constant values
WIN_WIDTH = 600
# Constant values
WIN_HEIGHT = 800
FLOOR = 730
# Font for score on  top of the screen
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

gen = 0

# Bird class for the bird movement
class Bird:

    # How much the bird is going to tilt
    MAX_ROTATION = 25
    # Class Variables/ CONSTANTS
    IMGS = bird_images
    # How much we are going to rotate on each frame
    # Technically every time the bird moves
    ROT_VEL = 20
    # How long each bird will show
    # This can also be used for how long and how fast each bird will flapping there wings
    ANIMATION_TIME = 5

    # will be used to initialize the objects state
    # x = the strting position of the birds x position
    # y = the starting position of the birds y position
    def __init__(self, x, y):

        self.x = x
        self.y = y
        # How much the bird image is going to tilt
        # so we understand how we drew it on the screen
        self.tilt = 0  # degrees to tilt
        # This will be used for physics of the bird like going up down or just fall down.
        self.tick_count = 0
        # Zero because it is not moving
        self.vel = 0
        # use for tilting and moving our birds
        self.height = self.y
        # which image we are showing the bird
        # so we can keep track of the animations
        self.img_count = 0
        # will reference bird images on line 32
        # It also references the bird image (Bird1.png)
        self.img = self.IMGS[0]

    # This function will be for when the bird flaps up ward and down ward
    def jump(self):
        # technically how fast and how it move up and down.
        self.vel = -10.5

        # when we are changing direction
        # also will be used for the games base physics
        self.tick_count = 0

        # This will keep track of where the bird jumped from or where is
        self.height = self.y

    # This function will call every single frame to move our bird
    def move(self):
        # How many times we moved since the last jump.
        self.tick_count += 1
        # calculate for displacement
        # also will calculate how the bird will move up and down on the y axis.
        # YES THIS IS A PHYSICS EQUATION
        # Overall tell us the current velocity of the bird.
        # tick_count = how many seconds we have being moving.
        # when it hits zero goes positive it technically going positive down and negative is up.
        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement
        # terminal velocity
        # fail safe, Meaning we dont want it going to far down or to far off where we cant see it.
        # made to where it doesnt move down to have so we will keep it at 16 pixels.
        # terminal velocity
        if displacement >= 16:

            # move down 16 pixels
            displacement = (displacement/abs(displacement)) * 16

        # if we go up keep moving up
        if displacement < 0:
            displacement -= 2

        # changing our y displacement based off y value
        # Overall we
        self.y = self.y + displacement
        # Now we start the overall tilt of the bird
        # Checking if bird
        if displacement < 0 or self.y < self.height + 50:
            # tilt up
            # Making sure it doesnt tilt all the away backwards or something or it doesnt do a full flip
            if self.tilt < self.MAX_ROTATION:
                # setting max rotation to 25 overall so it only tilt to 25 degrees
                self.tilt = self.MAX_ROTATION
        # if the bird is not moving upward else the bird moves downward
        else:  # tilt down
            if self.tilt > -90:
                # How much we are going to be rotating the bird downward
                self.tilt -= self.ROT_VEL
    # Draws bird on the screen
    def draw(self, win):

        # Keep track of how many ticks. like how many times have we have already shown per image
        self.img_count += 1

        # Basically what image should be shown based on anamation count
        # displaying first flappy bird image
        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        # if flappy bird image is less than ten the it shows bird 1
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        # if we are less than 15 then we show the last image
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping/ also this will be inbetween the up and down
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    # used to get collision from objects in the game
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

# To put the pipes in the game
class Pipe():
    GAP = 200
    # Velocity of the pipes
    # Because its not the bird itself that moves it is the actual background that does
    VEL = 5
    # didnt put y because each tude is randomly placed.
    def __init__(self, x):

        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0
        # Used to flip the pipe upside down. because the pipe image start upward.
        # Why we use flip
        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img
        # Used to check if the bird passed the pipe or not
        self.passed = False
        # So this will tell how tall the pipe is and how low the pipe is
        self.set_height()

    def set_height(self):
        # where the top of out pipe
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
    # Changing the x position on how much our velocity and framerates
    def move(self):
        self.x -= self.VEL

    # Draws the pipes on the board
    # this will draw the pipes on the top and the bottom of the pipes
    def draw(self, win):
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # collide
    # pixel point position
    # check if bird collides with the pipe
    # calling mask which makes a 2D list
    def collide(self, bird, win):

        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Now we are checking that if any pixels collide with each other
        # all in all we about to do some math so hardcore math lol!!!
        # Tells us the point of the overlap between the bird mask and the pipe mask
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)
        # if not none
        if b_point or t_point:
            return True

        return False
# This will be the ground of the game itself
# We will provide movement for the ground meaning its not the bird that moves its actually is the background an ground
class Base:
    # this will be set at the same speed the pips are moving.
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        self.y = y
        # Starting position of one image
        self.x1 = 0
        self.x2 = self.WIDTH

    # just like in the other class this function will be used for movement of the background image
    def move(self):
        # How the image moves we use VEL as velocity of the image itself
        # all in all we using the image to move
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        # Checking if any of the images fell of the screen or is not showing thus the program crashing
        # or not working
        # Well it wont crash but will refresh the game the
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

     # Like always  our draw function is used to draw the the objects/picture on the game
    def draw(self, win):

        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):

    # Rotates the images and angles
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

# Which will draw our window for our AI
def draw_window(win, birds, pipes, base, score, gen, pipe_ind):

    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)
    # Draws pipe animation
    base.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # Calls the draw method which deals with out animation and other stuff lol
        bird.draw(win)

    # score added
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations tag
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    # Draw at 10 pixels x 10 pixels
    win.blit(score_label, (10, 10))

    # how many are alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    # Updates the game board
    pygame.display.update()


def eval_genomes(genomes, config):

    global WIN, gen
    win = WIN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    # Floor and pipes
    base = Base(FLOOR)
    pipes = [Pipe(700)]
    # Keeps score from zero
    score = 0

    clock = pygame.time.Clock()
    # Run game
    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        # basic pygame
        # this will keep track of user interaction,example would be clicking a mouse or something
        for event in pygame.event.get():
            # Quits pygame overall
            # this is for when we click the exit window part of our window
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            # determine whether to use the first or second
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                # pipe on the screen for neural network input
                pipe_ind = 1
        # give each bird a fitness of 0.1 for each frame it stays alive
        for x, bird in enumerate(birds):
            # Fitness of birds
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        # Sets the movement for the base/floor
        base.move()
        # remove list
        rem = []
        # Add this because the add pipes function wont work
        add_pipe = False
        # implements birds movement.
        for pipe in pipes:
            pipe.move()
            # check for collision with pipes
            for bird in birds:
                # If a bird collides the minus 1 bird
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            # Checks if pipes are off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                # if pipe is off the screen then remove it
                rem.append(pipe)

            # Checks if the bird has passed the pipe
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
        # Adds pipes
        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            for genome in ge:
                genome.fitness += 2
            pipes.append(Pipe(WIN_WIDTH))

        # Removes pipes because the are off the screen
        for r in rem:
            pipes.remove(r)

        for bird in birds:
            # Checks if bird hit the floor
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        # break if score gets large enough
        '''if score > 20:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break'''


def run(config_file):
    # Runs neat algorithm
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
