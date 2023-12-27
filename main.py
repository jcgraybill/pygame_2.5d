import pygame, math
from catppuccin import Flavour
from shape import Shape

FPS                  = 60
STEP                 = 8
TURN_STEP            = math.pi / 360
WIDTH, HEIGHT        = 640,480
XPOS, YPOS           = 0,1
ANGLEPOS, COLORPOS   = 2,3
PLAYER_RADIUS        = 10
BOUNDINGBOX_SIZE     = PLAYER_RADIUS * 1.5
CLIPDEPTH            = 0.1
WALLHEIGHT           = 100

SHAPEFILE            = "shapes.txt"

COLORS               = Flavour.mocha()
OUTLINE_COLOR        = COLORS.mantle.rgb
HORIZON_COLOR        = COLORS.surface2.rgb

g_player  = [0,0,0,COLORS.blue.rgb]
g_3d_view = True
g_clear_v = True
g_shapes  = list()

def main():
    load_shapes()
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("3D")
    fps =  pygame.time.Clock()
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
                return
        update(pygame.key.get_pressed(), pygame.mouse.get_rel())
        draw(screen)
        pygame.display.update()
        fps.tick(FPS)

def load_shapes():
    global g_shapes
    f = open(SHAPEFILE, 'r')
    data = list(f.readlines())
    f.close()

    for row in data:
        g_shapes.append(Shape(row=row))
    
def update(keys, mouse):
    global g_player, g_3d_view, g_clear_v

    if keys[pygame.K_v] and g_clear_v: 
        g_3d_view = not g_3d_view
        g_clear_v = False
    
    if not keys[pygame.K_v] and not g_clear_v:
        g_clear_v = True

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        (hx, hy) = rotate(0, STEP, g_player[ANGLEPOS])
        if not is_collision(g_player[XPOS] + hx, g_player[YPOS] + hy):
            g_player[XPOS] += hx
            g_player[YPOS] += hy

    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        (hx, hy) = rotate(0, -STEP, g_player[ANGLEPOS])
        if not is_collision(g_player[XPOS] + hx, g_player[YPOS] + hy):
            g_player[XPOS] += hx
            g_player[YPOS] += hy

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        (hx, hy) = rotate(-STEP, 0, g_player[ANGLEPOS])
        if not is_collision(g_player[XPOS] + hx, g_player[YPOS] + hy):
            g_player[XPOS] += hx
            g_player[YPOS] += hy

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        (hx, hy) = rotate(STEP, 0, g_player[ANGLEPOS])
        if not is_collision(g_player[XPOS] + hx, g_player[YPOS] + hy):
            g_player[XPOS] += hx
            g_player[YPOS] += hy

    if keys[pygame.K_q]: g_player[ANGLEPOS] += TURN_STEP * STEP
    if keys[pygame.K_e]: g_player[ANGLEPOS] -= TURN_STEP * STEP

    if mouse[XPOS] != 0: g_player[ANGLEPOS] -= TURN_STEP * mouse[XPOS]

def is_collision(x,y):
    bounding_box = pygame.Rect( x - BOUNDINGBOX_SIZE // 2, y - BOUNDINGBOX_SIZE // 2, BOUNDINGBOX_SIZE, BOUNDINGBOX_SIZE)
    for shape in g_shapes:
        for from_point in range(len(shape.walls)):
            to_point = from_point + 1 if from_point < len(shape.walls) - 1 else 0
            if bounding_box.clipline(shape.walls[from_point], shape.walls[to_point]):
                return True
    return False

def draw(screen):
    screen.fill(COLORS.base.rgb)
    if g_3d_view:
        draw_3d(screen)
    else: # 2D view 
        draw_2d(screen)

def draw_3d(screen):
    vcenter = HEIGHT / 2
    pygame.draw.aaline(screen, HORIZON_COLOR, (0, vcenter), (WIDTH, vcenter), True )

    walls = list()

    for shape in g_shapes:
        for from_point in range(len(shape.walls)):
            to_point = from_point + 1 if from_point < len(shape.walls) - 1 else 0
            if wall := clip(shape.walls[from_point], shape.walls[to_point], shape.color):
                walls.append(wall)
    walls.sort(key=furthest_wall, reverse=True)

    for wall in walls:
        p0 = to_screen_3d(*wall[0])
        p1 = to_screen_3d(*wall[1])
        pygame.draw.polygon(screen, wall[COLORPOS],
                        [ (p0[XPOS], vcenter + p0[YPOS]), 
                        (p1[XPOS], vcenter + p1[YPOS]), 
                        (p1[XPOS], vcenter - p1[YPOS]), 
                        (p0[XPOS], vcenter - p0[YPOS]), 
                        ], 0 )
        pygame.draw.aalines(screen, OUTLINE_COLOR, True,
                        [ (p0[XPOS], vcenter + p0[YPOS]), 
                        (p1[XPOS], vcenter + p1[YPOS]), 
                        (p1[XPOS], vcenter - p1[YPOS]), 
                        (p0[XPOS], vcenter - p0[YPOS]), 
                        ], True )

def furthest_wall(wall):
    return max(math.dist((0,0), wall[0]), math.dist((0,0), wall[1]))

def draw_2d(screen):
    for shape in g_shapes:
        points = list()
        for point in shape.walls:
            points.append(to_screen_2d(*translate(*point)))
        pygame.draw.polygon(screen,shape.color,points,0)
        pygame.draw.aalines(screen, OUTLINE_COLOR, True,points, True)

    pygame.draw.circle(screen, g_player[COLORPOS], to_screen_2d(*translate(g_player[XPOS], g_player[YPOS])), PLAYER_RADIUS, 1)
    heading_line = rotate(0,PLAYER_RADIUS * 1.5, g_player[ANGLEPOS])
    pygame.draw.aaline(screen, g_player[COLORPOS], to_screen_2d(*translate(g_player[XPOS], g_player[YPOS])), 
                    to_screen_2d(*translate(g_player[XPOS] + heading_line[XPOS], g_player[YPOS] + heading_line[YPOS])), True)

def to_screen_3d(x,y):
    depth_scale = 1 / y * HEIGHT
    x *= depth_scale
    x += WIDTH // 2
    y = depth_scale * WALLHEIGHT // 2
    return x,y

def to_screen_2d(x,y):
    return WIDTH // 2 + x, HEIGHT // 2 - y

def clip(from_point,to_point, color):
    f = translate(from_point[XPOS], from_point[YPOS])
    t = translate(to_point[XPOS], to_point[YPOS])

    if f[YPOS] >= CLIPDEPTH and t[YPOS] >= CLIPDEPTH:
        return f,t,0,color
    if f[YPOS] < CLIPDEPTH and t[YPOS] < CLIPDEPTH:
        return False
    return clip_wall(f,t,color)

def clip_wall(f,t,color):
    if f[YPOS] >= CLIPDEPTH:
        front = f
        back = t
    else:
        front = t
        back = f
    size = front[YPOS] - back[YPOS]
    percent_visible = front[YPOS] / size
    clip_x = front[XPOS] + ( back[XPOS] - front[XPOS] ) * percent_visible
    return front, (clip_x, CLIPDEPTH), 0, color

def translate(x,y):
    x -= g_player[XPOS]
    y -= g_player[YPOS]
    x, y = rotate(x,y,-g_player[ANGLEPOS])
    return x,y

def rotate(x,y,angle):
    return x * math.cos(angle) - y * math.sin(angle), \
           y * math.cos(angle) + x * math.sin(angle)

pygame.init()
main()
pygame.quit()