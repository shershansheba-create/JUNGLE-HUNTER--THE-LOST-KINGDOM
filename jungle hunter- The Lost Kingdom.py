
import pygame
import random
import math
import sys

pygame.init()

# GAME SETTINGS
WIDTH, HEIGHT = 900, 550
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jungle Hunter - Lost Kingdom")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 23, bold=True)
bigfont = pygame.font.SysFont("Arial", 48, bold=True)

# COLORS
WHITE = (255,255,255)
GREEN = (25,110,50)
GOLD = (255,205,40)
BLUE = (50,210,255)
BROWN = (110,70,35)
RED = (210,50,40)

# GAME VARIABLES
player = pygame.Rect(100, 400, 35, 50)
speed = 5
velocity_y = 0
gravity = 0.7
jump = -14
ground = 480

score = 0
lives = 3
crystals = 0
camera = 0
game_state = "menu"
facing = 1
invincible = 0

# WORLD
platforms = [
    pygame.Rect(0,480,700,100),
    pygame.Rect(850,420,200,20),
    pygame.Rect(1150,360,200,20),
    pygame.Rect(1450,420,200,20),
    pygame.Rect(1750,350,220,20),
    pygame.Rect(2100,410,200,20),
    pygame.Rect(2400,480,600,100)
]

coins = [
    pygame.Rect(x,y,20,20)
    for x,y in [
        (250,440),(400,440),(550,440),
        (900,380),(1200,320),(1300,320),
        (1500,380),(1800,310),
        (2200,370),(2500,440),(2700,440)
    ]
]

crystal_locations = [
    (650,420),(1100,360),(1400,320),
    (2050,370),(2350,430)
]

crystal_items = [
    pygame.Rect(x,y,24,30)
    for x,y in crystal_locations
]

enemies = [
    {"rect":pygame.Rect(500,440,40,40),
     "min":450,"max":650,"speed":2,"alive":True},
    {"rect":pygame.Rect(900,380,40,40),
     "min":850,"max":1000,"speed":2,"alive":True},
    {"rect":pygame.Rect(1500,380,40,40),
     "min":1450,"max":1600,"speed":3,"alive":True},
    {"rect":pygame.Rect(1800,310,40,40),
     "min":1750,"max":1900,"speed":2,"alive":True}
]

arrows = []
particles = []

# RESET
def reset_game():
    global score,lives,crystals,camera
    global game_state,velocity_y,invincible

    score = 0
    lives = 3
    crystals = 0
    camera = 0
    velocity_y = 0
    invincible = 0

    player.x = 100
    player.y = 400

    coins.clear()
    coins.extend([
        pygame.Rect(x,y,20,20)
        for x,y in [
            (250,440),(400,440),(550,440),
            (900,380),(1200,320),(1300,320),
            (1500,380),(1800,310),
            (2200,370),(2500,440),(2700,440)
        ]
    ])

    crystal_items.clear()
    crystal_items.extend([
        pygame.Rect(x,y,24,30)
        for x,y in crystal_locations
    ])

    for e in enemies:
        e["alive"] = True

    arrows.clear()
    particles.clear()
    game_state = "playing"


# BACKGROUND
def draw_background():
    screen.fill((90,170,180))

    # Mountains
    for i in range(8):
        x = (i*200-int(camera*0.2))%1200-100
        pygame.draw.polygon(
            screen,(50,105,75),
            [(x,420),(x+100,170),(x+220,420)]
        )

    # Trees
    for i in range(14):
        x = (i*150-int(camera*0.4))%1300-100

        pygame.draw.rect(screen,(80,45,25),
                         (x+35,230,25,260))

        pygame.draw.circle(screen,(15,80,35),
                           (x+45,220),65)

        pygame.draw.circle(screen,(30,115,45),
                           (x+5,250),45)


# PLAYER DESIGN
def draw_player():
    x = player.x-camera
    y = player.y

    if invincible > 0 and pygame.time.get_ticks()%150 < 75:
        return

    # Legs
    pygame.draw.rect(screen,(65,40,20),(x+5,y+32,10,17))
    pygame.draw.rect(screen,(65,40,20),(x+22,y+32,10,17))

    # Body
    pygame.draw.rect(screen,(150,90,35),(x+4,y+15,27,22))

    # Backpack
    pygame.draw.rect(screen,(80,45,20),(x+26,y+18,10,20))

    # Face
    pygame.draw.circle(screen,(220,155,105),(x+18,y+10),12)

    # Hair
    pygame.draw.arc(screen,(30,20,10),
                    (x+5,y-3,26,20),math.pi,math.pi*2,7)

    # Headband
    pygame.draw.rect(screen,RED,(x+5,y+7,26,4))

    # Eye
    eye = x+24 if facing == 1 else x+11
    pygame.draw.circle(screen,(0,0,0),(eye,y+11),2)

    # Bow
    bow_x = x+36 if facing == 1 else x
    pygame.draw.arc(screen,GOLD,
                    (bow_x-8,y+17,18,30),
                    -math.pi/2,math.pi/2,3)


# PLATFORM DRAWING
def draw_platforms():
    for p in platforms:
        x = p.x-camera

        pygame.draw.rect(screen,BROWN,
                         (x,p.y,p.width,p.height))

        pygame.draw.rect(screen,GREEN,
                         (x,p.y,p.width,9))

        for i in range(0,p.width,30):
            pygame.draw.line(screen,(110,170,60),
                             (x+i,p.y),(x+i+7,p.y-5),2)


# COINS
def draw_coins():
    for c in coins:
        x = c.x-camera

        pygame.draw.circle(screen,GOLD,(x+10,c.y+10),11)
        pygame.draw.circle(screen,(255,245,150),(x+10,c.y+10),5)


# CRYSTALS
def draw_crystals():
    for c in crystal_items:
        x = c.x-camera

        points = [
            (x+12,c.y),(x+24,c.y+15),
            (x+12,c.y+30),(x,c.y+15)
        ]

        pygame.draw.polygon(screen,BLUE,points)
        pygame.draw.polygon(screen,WHITE,points,2)


# ENEMIES
def draw_enemies():
    for e in enemies:
        if not e["alive"]:
            continue

        r = e["rect"]
        x = r.x-camera

        pygame.draw.ellipse(screen,(150,55,35),
                            (x,r.y,40,40))

        pygame.draw.circle(screen,WHITE,(x+12,r.y+13),5)
        pygame.draw.circle(screen,WHITE,(x+29,r.y+13),5)

        pygame.draw.circle(screen,(0,0,0),(x+12,r.y+13),2)
        pygame.draw.circle(screen,(0,0,0),(x+29,r.y+13),2)


# TEMPLE
def draw_temple():
    x = 2800-camera

    pygame.draw.rect(screen,(140,115,65),(x,350,130,130))
    pygame.draw.rect(screen,(90,70,40),(x-15,335,160,18))
    pygame.draw.rect(screen,(30,65,45),(x+40,410,50,70))
    pygame.draw.circle(screen,GOLD,(x+65,380),12)


# UI
def draw_ui():
    pygame.draw.rect(screen,(10,40,25),(0,0,WIDTH,50))

    screen.blit(font.render("Lives: "+str(lives),True,WHITE),(15,12))
    screen.blit(font.render("Score: "+str(score),True,GOLD),(180,12))
    screen.blit(font.render("Crystals: "+str(crystals)+"/5",True,BLUE),(350,12))


# SHOOTING
def shoot():
    arrows.append({
        "rect":pygame.Rect(player.centerx,player.centery,20,5),
        "direction":facing
    })


# MAIN LOOP
running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if game_state == "menu":
                if event.key == pygame.K_RETURN:
                    reset_game()

            elif game_state == "playing":

                if event.key == pygame.K_SPACE:
                    if player.bottom >= ground or any(
                        player.bottom == p.top and
                        player.right > p.left and
                        player.left < p.right
                        for p in platforms
                    ):
                        velocity_y = jump

                if event.key == pygame.K_x:
                    if len(arrows) < 5:
                        shoot()

                if event.key == pygame.K_p:
                    game_state = "paused"

            elif game_state == "paused":
                if event.key == pygame.K_p:
                    game_state = "playing"

            elif game_state in ("gameover","victory"):
                if event.key == pygame.K_r:
                    reset_game()

    # GAME UPDATE
    if game_state == "playing":

        keys = pygame.key.get_pressed()

        old_bottom = player.bottom

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.x -= speed
            facing = -1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.x += speed
            facing = 1

        player.x = max(0,min(2900,player.x))

        velocity_y += gravity
        player.y += int(velocity_y)

        on_ground = False

        for p in platforms:
            if (
                player.colliderect(p)
                and velocity_y >= 0
                and old_bottom <= p.top+8
            ):
                player.bottom = p.top
                velocity_y = 0
                on_ground = True

        if player.bottom >= ground:
            player.bottom = ground
            velocity_y = 0
            on_ground = True

        # Collect coins
        for c in coins[:]:
            if player.colliderect(c):
                coins.remove(c)
                score += 50

        # Collect crystals
        for c in crystal_items[:]:
            if player.colliderect(c):
                crystal_items.remove(c)
                crystals += 1
                score += 150

        # Enemy movement
        for e in enemies:
            if not e["alive"]:
                continue

            r = e["rect"]
            r.x += e["speed"]

            if r.x < e["min"] or r.x > e["max"]:
                e["speed"] *= -1

            if player.colliderect(r) and invincible <= 0:
                lives -= 1
                invincible = 90
                velocity_y = -8

                if lives <= 0:
                    game_state = "gameover"

        if invincible > 0:
            invincible -= 1

        # Arrows
        for a in arrows[:]:
            a["rect"].x += 10*a["direction"]

            if a["rect"].x < 0 or a["rect"].x > 3000:
                arrows.remove(a)
                continue

            for e in enemies:
                if e["alive"] and a["rect"].colliderect(e["rect"]):
                    e["alive"] = False
                    score += 200
                    if a in arrows:
                        arrows.remove(a)
                    break

        # Camera
        camera = max(0,min(3000-WIDTH,player.centerx-WIDTH//2))

        # Temple mission
        if player.x >= 2800:
            if crystals >= 5:
                game_state = "victory"
            else:
                player.x = 2790

        if player.top > HEIGHT+100:
            lives -= 1
            player.x = max(100,player.x-100)
            player.y = 350
            velocity_y = 0
            invincible = 90

            if lives <= 0:
                game_state = "gameover"

    # DRAW
    draw_background()
    draw_platforms()
    draw_temple()
    draw_coins()
    draw_crystals()
    draw_enemies()
    draw_player()

    for a in arrows:
        x = a["rect"].x-camera
        pygame.draw.line(screen,GOLD,
                         (x,a["rect"].y),
                         (x+15*a["direction"],a["rect"].y),4)

    draw_ui()

    # MENU
    if game_state == "menu":
        shade = pygame.Surface((WIDTH,HEIGHT))
        shade.set_alpha(190)
        shade.fill((0,20,10))
        screen.blit(shade,(0,0))

        title = bigfont.render("JUNGLE HUNTER",True,GOLD)
        sub = font.render("THE LOST KINGDOM",True,WHITE)
        instruction = font.render(
            "Collect 5 blue crystals to unlock the temple!",True,BLUE
        )
        start = font.render("PRESS ENTER TO START",True,WHITE)

        screen.blit(title,title.get_rect(center=(450,200)))
        screen.blit(sub,sub.get_rect(center=(450,270)))
        screen.blit(instruction,instruction.get_rect(center=(450,340)))
        screen.blit(start,start.get_rect(center=(450,420)))

    elif game_state == "paused":
        title = bigfont.render("GAME PAUSED",True,GOLD)
        info = font.render("Press P to continue",True,WHITE)
        screen.blit(title,title.get_rect(center=(450,250)))
        screen.blit(info,info.get_rect(center=(450,320)))

    elif game_state == "gameover":
        title = bigfont.render("GAME OVER",True,RED)
        info = font.render("Final Score: "+str(score),True,WHITE)
        restart = font.render("PRESS R TO RESTART",True,GOLD)

        screen.blit(title,title.get_rect(center=(450,220)))
        screen.blit(info,info.get_rect(center=(450,300)))
        screen.blit(restart,restart.get_rect(center=(450,370)))

    elif game_state == "victory":
        title = bigfont.render("MISSION COMPLETED!",True,GOLD)
        info = font.render("Final Score: "+str(score),True,WHITE)
        restart = font.render("PRESS R TO PLAY AGAIN",True,BLUE)

        screen.blit(title,title.get_rect(center=(450,220)))
        screen.blit(info,info.get_rect(center=(450,300)))
        screen.blit(restart,restart.get_rect(center=(450,370)))

    pygame.display.update()

pygame.quit()
sys.exit()
