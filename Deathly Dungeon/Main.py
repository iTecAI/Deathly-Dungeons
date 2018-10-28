import pygame
import easygui
import math
import random
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.best_first import BestFirst
from time import time, sleep
import sys

#initialize graphics library
pygame.init()

#init global vars
st = None
coins = 0

class Item:
    def __init__(self,pos,typ):
        self.x = pos[0]
        self.y = pos[1]
        self.type = typ
        self.img = pygame.image.load('sprites\\' + typ + '.png')
        self.onmap = True
    def rem(self):
        self.onmap = False

class Map: #map class
    def __init__(self, array): #init
        self.map = array
        self.imgs = {'0':None,'1':None,'2':None,'3':None} #0:path, 1:wall, 2:door, 3:hole
        for i in list(self.imgs.keys()):
            self.imgs[i] = pygame.image.load('sprites\\' + i + '.png')
        self.checks = []
    def render(self): #render
        #print(self.checks)
        surface = pygame.Surface((500,500))
        for x in range(len(self.map)):
            for y in range(len(self.map[x])):
                if (x,y) in self.checks:
                    surface.blit(self.imgs['3'], (x*10,y*10))
                else:
                    surface.blit(self.imgs[self.map[x][y]], (x*10,y*10))
        self.checks = []
        return surface
    def get_at(self, pos): #gets block at position
        '''if pos[0] < 49 or pos[1] < 49:
            self.checks.append((int(pos[0]),int(pos[1])))
        else:
            self.checks.append((int(pos[0] / 10),int(pos[1] / 10)))'''
        try:
            #print(pos)
            return self.map[int(pos[0])][int(pos[1])]
        except IndexError:
            return self.map[int(pos[0] / 10)][int(pos[1] / 10)]

def pathfind(Map, start, end):
    transarray = []
    for y in range(len(Map)-1):
        transarray.append([])
        for x in range(len(Map[y])-1):
            if Map[x][y] == '0' or Map[x][y] == '2':
                transarray[y].append(1)
            else:
                transarray[y].append(0)
    matrix = Grid(matrix=transarray)
    s = matrix.node(int(start[0]),int(start[1]))
    e = matrix.node(int(end[0]),int(end[1]))
    finder = BestFirst(diagonal_movement=DiagonalMovement.never)
    path, runs = finder.find_path(s, e, matrix)
    if len(path) == 0:
        #print(matrix.grid_str(path=path,start=s,end=e))
        pass
    #print(path)
    return path

#person class - defines Victims and Killer
class Person:
    def __init__(self, position, victim, Map): #init person
        self.victim = victim
        self.map = Map
        self.x = position[0]
        self.y = position[1]
        self.ax = self.x * 10
        self.ay = self.y * 10
        self.rot = 0
        self.alive = True
        self.ai = {'priority':random.choice('nesw')} #defines AI settings
        self.dir = self.ai['priority']
        self.name = ''
        for i in range(random.randint(4,11)):
            self.name += random.choice('qwertyuiopasdfghjklzxcvbnm')
        self.name = self.name[0].upper() + self.name[1:]
        if self.victim: #if victim:
            self.sprite = pygame.image.load('sprites\\victim.png') #load sprite img
            self.has_key = False
        else: #if killer:
            self.sprite = pygame.image.load('sprites\\killer.png') #load sprite img
            self.target = None
            self.path = []
            self.name = 'MURD' + self.name
    def move(self, hdg,opp=False): #move Person
        if not opp:
            if hdg == 'n':
                self.ay += 10
                self.y += 1
                self.rot = 180
                self.dir = 'n'
            elif hdg == 'e':
                self.ax += 10
                self.x += 1
                self.rot = 270
                self.dir = 'e'
            elif hdg == 's':
                self.ay -= 10
                self.y -= 1
                self.rot = 0
                self.dir = 's'
            elif hdg == 'w':
                self.ax -= 10
                self.x -= 1
                self.rot = 90
                self.dir = 'w'
        else:
            if hdg == 'n':
                self.ay -= 10
                self.y -= 1
                self.rot = 0
                self.dir = 'n'
            elif hdg == 'e':
                self.ax -= 10
                self.x -= 1
                self.rot = 90
                self.dir = 'e'
            elif hdg == 's':
                self.ay += 10
                self.y += 1
                self.rot = 180
                self.dir = 's'
            elif hdg == 'w':
                self.ax += 10
                self.x += 1
                self.rot = 270
                self.dir = 'w'
    def pickup(self, item): #Pick up item
        global st, coins
        if self.victim:
            item.rem()
            if item.type == 'key':
                self.has_key = True
                self.sprite = pygame.image.load('sprites\\victim-key.png') #load sprite img with key
            if item.type == 'clock':
                st -= 2
            if item.type == 'coin':
                coins += 1
    def die(self, r):
        self.alive = False
        self.reason = r
    def item_intersect(self, pos, items):
        for i in items:
            if pos[0] == i.x and pos[1] == i.y:
                return i
    def person_intersect(self, pos, persons):
        for i in persons:
            #print(pos)
            #print(i.x,i.y)
            if pos[0] == i.x and pos[1] == i.y and self.name != i.name:
                #print(i.name)
                return i
    def dist(self, player):
        return math.sqrt((abs(self.x-player.x)**2)+(abs(self.y-player.y)**2))
    def run_ai(self, players, items): #run AI task
        if self.victim:
            #run victim AI tasks
            tdir = self.dir
            if random.randint(0,1) == 1:
                if tdir == 'n':
                    ilist = 'nesw'
                if tdir == 'e':
                    ilist = 'eswn'
                if tdir == 's':
                    ilist = 'swne'
                if tdir == 'w':
                    ilist = 'wnes'
            else:
                if tdir == 'n':
                    ilist = 'nwse'
                if tdir == 'e':
                    ilist = 'enws'
                if tdir == 's':
                    ilist = 'senw'
                if tdir == 'w':
                    ilist = 'wsen'
            for i in ilist:
                self.move(i)
                adj= self.map.get_at((self.x,self.y))
                if adj == '0' and random.randint(0,50) > 2 or adj == '2' and self.has_key or adj == '3' and random.randint(0,10) == 10:
                    break
                else:
                    self.move(i,opp=True)
            intersects = [self.item_intersect((self.x,self.y),items),self.person_intersect((self.x,self.y),players)]
            if intersects[0] and random.randint(0,5) == 5:
                self.pickup(intersects[0])
            if intersects[1]:
                #print(intersects[1])
                if intersects[1].victim == False:
                    self.die('murd')
            if self.map.get_at((self.x,self.y)) == '3':
                self.die('hole')

        else:
            #run killer hunt algorithm
            pdists = {}
            for i in players:
                if i.alive and i.victim:
                    pdists[self.dist(i)] = i
            dlist = sorted(list(pdists.keys()),reverse=True)
            pids = []
            for i in pdists.values():
                if i.victim:
                    pids.append(i.name)
            if self.target == None:
                self.target = pdists[dlist[0]]
            elif not self.target.name in pids:
                self.target = pdists[random.choice(dlist)]
            elif len(self.path) == 0:
                self.target = pdists[random.choice(dlist)]
            else:
                tdir = self.dir
                if random.randint(0,1) == 1:
                    if tdir == 'n':
                        ilist = 'nesw'
                    if tdir == 'e':
                        ilist = 'eswn'
                    if tdir == 's':
                        ilist = 'swne'
                    if tdir == 'w':
                        ilist = 'wnes'
                else:
                    if tdir == 'n':
                        ilist = 'nwse'
                    if tdir == 'e':
                        ilist = 'enws'
                    if tdir == 's':
                        ilist = 'senw'
                    if tdir == 'w':
                        ilist = 'wsen'
                for i in ilist:
                    self.move(i)
                    adj= self.map.get_at((self.x,self.y))
                    if adj == '0' and random.randint(0,50) > 2:
                        break
                    else:
                        self.move(i,opp=True)
            path = pathfind(self.map.map, (self.x,self.y), (self.target.x,self.target.y))
            self.path = path
            pos = (self.x,self.y)
            c = 0
            try:
                while (self.x, self.y) == pos and c < 50:
                    try:
                        if self.map.get_at((path[1][0],path[1][1])) in '02':
                            self.x = path[1][0]
                            self.y = path[1][1]
                            self.ax = self.x * 10
                            self.ay = self.y * 10
                    except:
                        pass
                    
                    c += 1
            except:
                pass
    def check_dead(self,players):
        if not self.victim:
            return
        if self.map.get_at((self.x,self.y)) == '3':
                self.die('hole')
        try:
            i = self.person_intersect((self.x,self.y),players)
            if not i.victim:
                self.die('murd')
        except:
            return
    def check_pick(self,items):
        intersect = self.item_intersect((self.x,self.y),items)
        if intersect:
            self.pickup(intersect)
            

def map_from(imgloc):
    img = pygame.image.load(imgloc)
    array = []
    for x in range(img.get_width()):
        array.append([])
        for y in range(img.get_height()):
            array[x].append('')
            color_obj = img.get_at((x,y))
            color = (color_obj.r, color_obj.g, color_obj.b)
            if color == (255,255,255):
                array[x][y] = '0'
            elif color == (0,0,0):
                array[x][y] = '1'
            elif color == (100,100,0):
                array[x][y] = '2'
            elif color == (255,0,0):
                array[x][y] = '3'
    return array

#main ----------------------------------------------------------------------------------------------------------------------------------------------
#start screen
pygame.display.set_caption('Deathly Dungeon')
pygame.display.set_icon(pygame.image.load('other_assets\\icon.png'))
screen = pygame.display.set_mode((500,500), pygame.HWSURFACE)
scrn = (500,500)
mloop = pygame.mixer.Sound('other_assets\\loop.wav')
mloop.play()
while True:
    run = True
    selected = None
    paused = False
    ptime = 0

    #load settings
    default_options = {'victims':'5','killers':'1'}

    ofile = open('options.txt','r')
    try:
        options = eval(ofile.read())
    except:
        options = default_options
    ofile.close()
    for i in default_options.keys():
        if not i in options.keys():
            options[i] = default_options[i]
    ofile = open('options.txt','w')
    ofile.write(str(options))
    ofile.close()
    run_mode = 'main'
    MAP = Map(map_from('maps\\map2.png'))
    #populate items
    items = []
    for i in range(random.randint(5,15)):
        sugg_pos = (random.randint(0,49),random.randint(0,49))
        if MAP.get_at(sugg_pos) == '0':
            items.append(Item((sugg_pos[0],sugg_pos[1]),random.choice(['key','clock','coin'])))
    #Start Screen
    while run:
        _screen = pygame.Surface((500,500))
        if run_mode == 'main':
            _screen.fill((127,127,127))
            _screen.blit(MAP.render(),(0,0))
            for item in items:
                if item.onmap:
                    _screen.blit(item.img,(item.x * 10,item.y * 10))
            font = pygame.font.Font('other_assets\\font.ttf', 60)
            title = font.render('Deathly Dungeon', True, (255,0,0))
            _screen.blit(title, (30,50))
            collide_rect_start = pygame.draw.rect(_screen, (100,100,100), pygame.Rect(10, 250, 480, 100))
            begin = font.render('BEGIN', True, (255,0,0))
            _screen.blit(begin, (155,273))
            collide_rect_opts = pygame.draw.rect(_screen, (100,100,100), pygame.Rect(10, 375, 480, 100))
            options_t = font.render('OPTIONS', True, (255,0,0))
            _screen.blit(options_t, (125,398))
            collide_rect_help = pygame.draw.rect(_screen, (100,100,100), pygame.Rect(0, 0, 50, 50))
            help_t = font.render('?', True, (255,0,0))
            _screen.blit(help_t, (15,1))
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if collide_rect_start.collidepoint((int(event.pos[0] * 500/scrn[0]),int(event.pos[1] * 500/scrn[1]))):
                        run = False
                    if collide_rect_opts.collidepoint((int(event.pos[0] * 500/scrn[0]),int(event.pos[1] * 500/scrn[1]))):
                        run_mode = 'settings'
                    if collide_rect_help.collidepoint((int(event.pos[0] * 500/scrn[0]),int(event.pos[1] * 500/scrn[1]))):
                        run_mode = 'help'
                if event.type == pygame.VIDEORESIZE:
                    scrn = (event.w,event.h)
                    screen = pygame.display.set_mode(scrn, pygame.HWSURFACE | pygame.RESIZABLE)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        elif run_mode == 'settings': #settings menu
            _screen.fill((200,200,200))
            font = pygame.font.Font('other_assets\\emulogic.ttf', 24)
            ot = font.render('Options',True, (255,255,255))
            _screen.blit(ot, (10,10))
            backb = pygame.draw.rect(_screen, (180,180,180), pygame.Rect(250,0,250,40))
            _screen.blit(font.render('Back ->', True, (255,255,255)), (255,5))
            options_info = {'victims':('Number of Victims','Enter # of Victims to use.'),
                           'killers':('Number of Killers','Enter # of Killers to use.')}
            y = 40
            collides = {}
            for opt in options_info.keys():
                collides[opt] = pygame.draw.rect(_screen, (180,180,180), pygame.Rect(0, y, 500, 50))
                _screen.blit(font.render(options_info[opt][0], True, (255,255,255)), (10, y+10))
                y += 50
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if backb.collidepoint((int(event.pos[0] * 500/scrn[0]),int(event.pos[1] * 500/scrn[1]))):
                        run_mode = 'main'
                    else:
                        for i in collides.keys():
                            if collides[i].collidepoint((int(event.pos[0] * 500/scrn[0]),int(event.pos[1] * 500/scrn[1]))):
                                oi = options_info[i]
                                q = oi[1]
                                screen = pygame.display.set_mode((1,1))
                                new = easygui.enterbox(q)
                                screen = pygame.display.set_mode(scrn, pygame.HWSURFACE | pygame.RESIZABLE)
                                if new and len(new) > 0:
                                    options[i] = new
                                    ofile = open('options.txt','w')
                                    ofile.write(str(options))
                                    ofile.close()
                if event.type == pygame.VIDEORESIZE:
                    scrn = (event.w,event.h)
                    screen = pygame.display.set_mode(scrn, pygame.HWSURFACE | pygame.RESIZABLE)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        elif run_mode == 'help':
            _screen.fill((200,200,200))
            font = pygame.font.Font('other_assets\\emulogic.ttf', 24)
            ot = font.render('Help',True, (255,255,255))
            _screen.blit(ot, (10,10))
            backb = pygame.draw.rect(_screen, (180,180,180), pygame.Rect(250,0,250,40))
            _screen.blit(font.render('Back ->', True, (255,255,255)), (255,5))
            y = 40
            font = pygame.font.Font('other_assets\\emulogic.ttf', 12)
            help_lines = ['Controls:',
                          'Space: Pause',
                          'K: End current game',
                          'Click mouse on victim to select',
                          'Arrow keys to control selected',
                          ' ',
                          'How to Play:',
                          'Control individual victims to keep',
                          'them away from the murderer.',
                          'The murderer is the black-haired,',
                          'red-eyed person.',
                          'The victims are the other ones.',
                          'Collect keys to open doors.',
                          'Collect clocks to add 2 seconds to',
                          'your survival time.',
                          'Collect coins to increase your,',
                          'time-based score.',
                          'Dont fall in holes (dark gray',
                          'gradient tiles).',
                          ' ',
                          'Tips:',
                          'Pause the game when selecting.']
            scrolly = 0
            for line in help_lines:
                _screen.blit(font.render(line, True, (255,255,255)), (10,y))
                y += 20
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if backb.collidepoint((int(event.pos[0] * 500/scrn[0]),int(event.pos[1] * 500/scrn[1]))):
                        run_mode = 'main'
                if event.type == pygame.VIDEORESIZE:
                    scrn = (event.w,event.h)
                    screen = pygame.display.set_mode(scrn, pygame.HWSURFACE | pygame.RESIZABLE)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            

        if scrn != (500,500):
            screen.blit(pygame.transform.scale(_screen, scrn),(0,0))
        else:
            screen.blit(_screen,(0,0))
        pygame.display.flip()
        if not pygame.mixer.get_busy():
            mloop.play()

    victims = int(options['victims'])
    killers = int(options['killers'])

    #populate people
    people = []
    for i in range(victims):
        sugg_pos = (random.randint(0,49),random.randint(0,49))
        while not MAP.get_at(sugg_pos) == '0':
            sugg_pos = (random.randint(0,49),random.randint(0,49))
        people.append(Person((sugg_pos[0],sugg_pos[1]),True,MAP))
    k = 0#pop killers
    for i in range(killers):
        k += 1
        sugg_pos = (random.randint(0,49),random.randint(0,49))
        while not MAP.get_at(sugg_pos) == '0':
            sugg_pos = (random.randint(0,49),random.randint(0,49))
        people.append(Person((sugg_pos[0],sugg_pos[1]),False,MAP))
    #main game start
    st = time()
    run = True
    screen = pygame.display.set_mode(scrn, pygame.HWSURFACE | pygame.RESIZABLE)
    sel_sprites = (pygame.image.load('sprites\\victim-sel.png'), pygame.image.load('sprites\\victim-key-sel.png'))
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #if window closed
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN: 
                if event.key == 32:#detect pause
                    if paused:
                        paused = False
                        ptime += time() - cptime
                    else:
                        cptime = time()
                        paused = True
                if event.unicode == 'k':
                    run = False
            if event.type == pygame.MOUSEBUTTONDOWN: #play-as selector
                if event.button == 1:
                    sel_bool = False
                    for i in people:
                        pos = (event.pos[0] * 500/scrn[0],event.pos[1] * 500/scrn[1])
                        if i.victim and int(i.x) == int(pos[0] / 10) and int(i.y) == int(pos[1] / 10):
                            selected = i
                            #print(selected)
                            sel_bool = True
                            break
                    if not sel_bool:
                        selected = None
            if event.type == pygame.VIDEORESIZE:
                scrn = (event.w,event.h)
                screen = pygame.display.set_mode(scrn, pygame.HWSURFACE | pygame.RESIZABLE)
            if event.type == pygame.ACTIVEEVENT:
                if event.gain == 0 and not paused:
                    screen = pygame.display.set_mode(scrn, pygame.HWSURFACE | pygame.RESIZABLE)

        #selected player drive controls 273:up, 275:right, 274:down, 276:left
        if selected:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and (MAP.get_at((selected.x,selected.y - 1)) in ['0','3'] or (MAP.get_at((selected.x,selected.y - 1)) == '2' and selected.has_key)):
                selected.move('s')
            if keys[pygame.K_RIGHT] and (MAP.get_at((selected.x + 1,selected.y)) in ['0','3'] or (MAP.get_at((selected.x + 1,selected.y)) == '2' and selected.has_key)):
                selected.move('e')
            if keys[pygame.K_DOWN] and (MAP.get_at((selected.x,selected.y + 1)) in ['0','3'] or (MAP.get_at((selected.x,selected.y + 1)) == '2' and selected.has_key)):
                selected.move('n')
            if keys[pygame.K_LEFT] and (MAP.get_at((selected.x - 1,selected.y)) in ['0','3'] or (MAP.get_at((selected.x - 1,selected.y)) == '2' and selected.has_key)):
                selected.move('w')
        if not paused:
            _screen = pygame.Surface((500,500))
            _screen.fill((127,127,127))
            _screen.blit(MAP.render(),(0,0))
            for item in items:
                if item.onmap:
                    _screen.blit(item.img,(item.x * 10,item.y * 10))
            alive_people = 0
            try:
                for p in people:
                    if not p.alive:
                        #print(p.reason)
                        pass
                    if p.alive:
                        alive_people += 1
                        if not selected or not selected.name == p.name:
                            p.run_ai(people,items)
                        if selected:
                            if selected.name == p.name:
                                if p.has_key:
                                    psurf = sel_sprites[1]
                                else:
                                    psurf = sel_sprites[0]
                            else:
                                psurf = p.sprite
                        else:
                            psurf = p.sprite
                        psurf = pygame.transform.rotate(psurf,p.rot)
                        _screen.blit(psurf,(p.ax,p.ay))
                for p in people:
                    p.check_dead(people)
                    p.check_pick(items)
                if alive_people == k:
                    run = False
                    break
            except:
                break
        if scrn != (500,500):
            screen.blit(pygame.transform.scale(_screen, scrn),(0,0))
        else:
            screen.blit(_screen,(0,0))
        pygame.display.flip()
        if not pygame.mixer.get_busy():
            mloop.play()
        pygame.time.Clock().tick(40)

    #endloop
    ttime = time() - st - ptime
    try:
        score = str(round((killers / victims * ttime) + (coins / 4), 5))
    except:
        score = '0.00000'
    font = pygame.font.Font('other_assets\\emulogic.ttf', 24)
    _screen = pygame.Surface((500,500))
    _screen.fill((127,127,127))
    score_text = font.render('Your score was: ', True, (255,255,255))
    score = font.render(score, True, (255,255,255))
    _screen.blit(score_text, (10,10))
    _screen.blit(score, (10,40))
    replay = pygame.image.load('other_assets\\replay.png')
    replay_rect = pygame.Rect(125,125,250,250)
    _screen.blit(replay, (125,125))
    run = True
    replayb = False
    while run:
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                scrn = (event.w,event.h)
                screen = pygame.display.set_mode(scrn, pygame.HWSURFACE | pygame.RESIZABLE)
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if replay_rect.collidepoint((int(event.pos[0] * 500/scrn[0]),int(event.pos[1] * 500/scrn[1]))):
                    run = False
                    replayb = True
        if scrn != (500,500):
            screen.blit(pygame.transform.scale(_screen, scrn),(0,0))
        else:
            screen.blit(_screen,(0,0))
        pygame.display.flip()
        if not pygame.mixer.get_busy():
            mloop.play()
    if not replayb:
        break
pygame.quit()
