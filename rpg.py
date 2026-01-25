import pygame as pg
import time
import keyboard
import random
from pygame_assist import Particles, Particle_Set
import playsound
from threading import Thread

pg.init()
screen = pg.display.set_mode((1000, 520), pg.RESIZABLE)
pg_screen = [screen]
pg.display.set_caption("Teletubbies Strike Back")


def collide(x1, y1, w1, h1, x2, y2, w2, h2):
    if (x2 < (x1 + w1) < (x2 + w2)) or (x1 < (x2 + w2) < (x1 + w1)):
        if (y2 <= (y1 + h1) <= (y2 + h2)) or (y1 <= (y2 + h2) <= (y1 + h1)):
            return True
    else:
        return False


def split(word):
    return [char for char in word]


def play_song():
    playsound.playsound('thatched.mp3', 1)


def click(x, y, x1, y2, w, h):
    if x1 < x < (x1 + w) and y2 < y < (y2 + h):
        return True
    return False


class Items:
    def __init__(self, x, y, pic, down):
        self.x = x
        self.y = y
        self.picture = pic
        self.down = down

    def display(self, scroll):
        screen.blit(self.picture, (self.x + scroll, self.y + self.down))

    def pickup_check(self, player, key, area, scroll):
        if key[pg.K_e] and collide(self.x + scroll, self.y + self.down, self.picture.get_width(), self.picture.get_height(),
                                   player.x, player.y, player.char.get_width(), player.char.get_height()):
            player.items[area.area - 1] += 1
            return True


class Materials:
    def __init__(self, text, p):
        self.materials = [p.items[0:2], p.items[1:3]]
        self.texts = [text(25, f'{sum(p.items[0:2])}', 507, 85, (0, 0, 0)),
                      text(25, f'{sum(p.items[1:3])}', 507, 115, (0, 0, 0)), 'SlimeBalls', 'Fox Food']
        self.show = False
        self.show_close = time.time()
        self.text = text(30, 'Materials', 507, 20, (0, 0, 0))

    def list_mat(self, player):
        pass

    def draw(self, p):
        pg.draw.rect(pg_screen[0], (113, 120, 230), [504, 24, 162, 32])
        pg.draw.rect(pg_screen[0], (0, 0, 0), [500, 20, 170, 40], 4, 10)
        self.text.draw_font()
        self.materials = [sum(p.items[0:2]), sum(p.items[1:3])]
        if self.show:
            pg.draw.rect(pg_screen[0], (113, 120, 230), [504, 84, 162, 92])
            pg.draw.rect(pg_screen[0], (0, 0, 0), [500, 80, 170, 100], 4, 10)
            for i, var in enumerate(self.texts[0:2]):
                var.text = f'{self.texts[i + 2]}: {self.materials[i]}'
                var.draw_font()

    def event_check(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and click(*pg.mouse.get_pos(), 500, 20, 170, 40):
            self.show = not self.show
            if self.show:
                self.show_close = time.time()
        if time.time() - self.show_close > 3:
            self.show = not self.show
        if not self.show:
            self.show_close = time.time()


class Tiles:
    def __init__(self):
        self.images = [pg.transform.scale(pg.image.load('grass.png'), (40, 40)),
                       pg.transform.scale(pg.image.load('sky.png'), (40, 40))]
        self.tile_list = []

    def tile_check(self, player, area):
        pass
        # for tile in area.areas[area.area + 1]['map_pic'][5]:
        #   print(tile)


class Power:
    def __init__(self, text):
        self.show_close = time.time()
        self.text = text(30, 'Boosters', 307, 20, (0, 0, 0))
        self.show = False
        self.boosters = [
            {'Use': False, 'Time': time.time(), 'text': text(25, 'Speed[20]: + | =', 307, 85, (0, 0, 0)), 'Count': 0,
             'Money': 20, 'Buy': (420, 95), 'Consume': (445, 96)},
            {'Use': False, 'Time': time.time(), 'text': text(25, 'Power[40]: + | =', 307, 115, (0, 0, 0)), 'Count': 0,
             'Money': 40, 'Buy': (420, 125), 'Consume': (448, 126)},
            {'Use': False, 'Time': time.time(), 'text': text(25, 'Health[30]: + | =', 307, 145, (0, 0, 0)), 'Count': 0,
             'Money': 30, 'Buy': (420, 155), 'Consume': (452, 156)}
        ]

    def boost(self, player):
        if self.boosters[0]['Use']:
            player.vel = 8
            player.shift_vel = 12.8
            if time.time() - self.boosters[0]['Time'] > 120:
                self.boosters[0]['Use'] = False
                self.boosters[0]['Time'] = time.time()
                player.vel = 5
                player.shift_vel = 8
        if self.boosters[1]['Use']:
            player.power = 10
            if time.time() - self.boosters[1]['Time'] > 120:
                self.boosters[1]['Use'] = False
                player.power = 5
                self.boosters[1]['Time'] = time.time()
        if self.boosters[2]['Use']:
            player.health += 40
            if player.health > 100:
                player.health = 100
            self.boosters[2]['Use'] = False

    def event_check(self, event, player, money):
        if event.type == pg.MOUSEBUTTONDOWN and click(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1], 300, 20, 130, 40):
            if not self.show:
                self.show_close = time.time()
            self.show = not self.show
            event.cooldown = time.time()
        if time.time() - self.show_close > 5 and self.show:
            self.show = False
        for i in range(len(self.boosters)):
            if event.type == pg.MOUSEBUTTONDOWN and click(pg.mouse.get_pos()[0], pg.mouse.get_pos()[1],
                                                          self.boosters[i]['Buy'][0], self.boosters[i]['Buy'][1], 10,
                                                          10) and money.money - self.boosters[i]['Money'] >= 0:
                self.boosters[i]['Count'] += 1
                money.spend(self.boosters[i]['Money'])
            if event.type == pg.MOUSEBUTTONDOWN and self.boosters[i]['Count'] >= 1 and click(pg.mouse.get_pos()[0],
                                                                                             pg.mouse.get_pos()[1],
                                                                                             self.boosters[i][
                                                                                                 'Consume'][0],
                                                                                             self.boosters[i][
                                                                                                 'Consume'][1], 15,
                                                                                             15) and self.boosters[i][
                'Use'] != True:
                self.boosters[i]['Use'] = True
                self.boosters[i]['Count'] -= 1
        self.boost(player)

    def simplify_vis(self):
        if self.show:
            pg.draw.rect(pg_screen[0], (113, 120, 230), [304, 84, 162, 92])
            pg.draw.rect(pg_screen[0], (0, 0, 0), [300, 80, 170, 100], 4, 10)
            for var in self.boosters:
                var['text'].draw_font()
        self.text.draw_font()

    def visual(self):
        pg.draw.rect(pg_screen[0], (113, 120, 230), [304, 24, 162, 32])
        pg.draw.rect(pg_screen[0], (0, 0, 0), [300, 20, 170, 40], 4, 10)
        self.simplify_vis()


class Text:
    def __init__(self, size, text, x, y, color):  # SET TEXT
        self.size = size
        self.text = text
        self.x = x
        self.y = y
        self.color = color

    def draw_font(self):  # DRAW TEXT
        font = pg.font.SysFont('impact', self.size)
        display_text = font.render(f'{self.text}', True, self.color)
        screen.blit(display_text, (self.x, self.y))


class Player:
    def __init__(self):  # ALL PLAYER VARIABLE
        self.gun_img = (pg.transform.scale(pg.image.load('pistol1.png'), (40, 32)))
        self.set_img = pg.transform.flip(pg.transform.scale(pg.image.load('armor1.png'), (130, 100)), True, False)
        self.char = self.set_img
        self.gun = self.gun_img
        self.health = 100
        self.power = 5
        self.x = 1
        self.y = 340
        self.vel = 5
        self.shift_vel = 8
        self.right = True
        self.jumpCount = 10
        self.isJump = False
        self.neg = 0
        self.items = [0, 0, 0, 0]
        self.item = {}

    def flip(self, right):  # FLIPING
        if right != self.right and right:
            self.right = True
            self.char = self.set_img
            self.gun = self.gun_img
        if right != self.right and right == False:
            self.right = False
            self.char = pg.transform.flip(self.set_img, True, False)
            self.gun = pg.transform.flip(self.gun_img, True, False)

    def display_gun(self):  # DRAwing
        self.guny = self.y + (self.char.get_height() / 2)
        if self.right:
            self.gunx = self.x + 75
        else:
            self.gunx = self.x + 13
        screen.blit(self.gun, (self.gunx, self.guny))

    def knockback(self):
        if self.right:
            self.x -= 1
        else:
            self.x += 1

    def damage(self, dmg):
        self.health -= dmg

    def jump(self, keys, fps):
        if not self.isJump and (keys[pg.K_UP] or keys[pg.K_w]):
            self.isJump = True
            self.jumpy = 340
        if self.isJump:
            if self.jumpCount >= - 10:
                neg = 1
                if self.jumpCount < 0:
                    neg = -1
                self.y -= ((self.jumpCount ** 2) / 3 * neg) / (fps.showing / 35) / 2
                self.jumpCount -= (1 / (fps.showing / 35)) / 2
            else:
                self.isJump = False
                self.jumpCount = 10
                self.y = self.jumpy

    def try_death(self, money, area, fps):
        if money.death(self.health, fps):
            self.health = 100
            self.x = 0
            area.scroll = 0

    def move(self, neg, sprint, fps, flip, area):
        if sprint:
            self.x += (self.shift_vel * neg) / (fps.showing / 25)
        else:
            self.x += (self.vel * neg) / (fps.showing / 25)
        if self.x - area.scroll > 3000:
            area.scroll = -2000
        if self.x - area.scroll < 0:
            self.x = 1
            area.scroll = 0
        if self.x > 800 and not abs(area.scroll) > 1999:
            area.scroll -= self.x - 800
            self.x = 800
        if abs(area.scroll) > 1999 and self.x > 900:
            self.x = 900
        if self.x < 0:
            area.scroll += 0 - self.x
            self.x = 0
        self.flip(flip)

    def item_display(self, scroll):
        for values in self.item.values():
            values.display(scroll)

    def item_checking(self, area, key):
        i = 0
        for values in self.item.values():
            if values.pickup_check(self, key, area, area.scroll):
                self.item.pop(list(self.item.keys())[i])
                break
            i += 1


class Monster:
    def __init__(self, pic, drop, scroll, health):
        self.pic = pic
        self.drop = drop
        self.x = random.randint(100, 900) - scroll
        self.p1 = self.x - random.randint(30, 50)
        self.p2 = self.x + random.randint(30, 50)
        self.y = 440 - pic.get_height()
        self.health = health
        self.right = random.choice([True, False])

    def display(self, fps, damage, scroll, area, player, particle):
        if self.right:
            self.x += 1 / (fps.showing / 25)
        if self.right == False:
            self.x -= 1 / (fps.showing / 25)
        if self.x <= self.p1 or self.x >= self.p2:
            self.right = not self.right
        screen.blit(self.pic, (self.x + int(round(scroll, 2)), self.y))
        val = list(area.bullet_list.values())
        for i in range(len(val)):
            val[i].collision(self, i, area, particle, player)
        if collide(player.x, player.y, player.char.get_width(), player.char.get_height(), self.x + scroll, self.y,
                   self.pic.get_width(), self.pic.get_height()):
            player.damage(damage)

    def death(self, particles, area, player, scroll):
        if self.health <= 0:
            string = f'particle{len(particles.keys())}'
            color = (list(area.areas[area.area - 1].values()))[2][4]
            particles[string] = Particle_Set(self.x + (self.pic.get_width() / 2), self.y, 10, 6, color, 440,
                                             area.scroll)
            if random.randint(1, 3) == 1:
                new_item_name = len(player.item.values())
                player.item[new_item_name] = Items(self.x, self.y, area.areas[area.area - 1]['monster_info'][3], area.areas[area.area - 1]['monster_info'][5])
            return True
        return False


class Bullets:
    def __init__(self, x, y, power, right):
        self.x = x
        self.y = y
        self.velocity = 800
        self.power = power
        if right:
            self.right = 1
            self.img = pg.transform.scale(pg.image.load('bullet.png'), (15, 4))
        else:
            self.right = -1
            self.img = pg.transform.flip(pg.transform.scale(pg.image.load('bullet.png'), (15, 4)), True, False)

    def move(self, fps):
        self.x += self.right * (self.velocity / fps.showing)
        screen.blit(self.img, (self.x, self.y))
        if self.x > 1000 or self.x < 0:
            return True

    def collision(self, monster, index, area, particles, player):
        if collide(self.x, self.y, self.img.get_width(), self.img.get_height(), monster.x + area.scroll, monster.y,
                   monster.pic.get_width(), monster.pic.get_height()):
            try:
                monster.health -= self.power
                string = f'particle{len(particles.keys())}'
                if monster.health > 0:
                    particles[string] = Particle_Set(monster.x + (monster.pic.get_width() / 2), monster.y, 5, 5,
                                                     (255, 0, 0), 440, area.scroll)
                area.bullet_list.pop((list(area.bullet_list.keys()))[index])
            except:
                pass


class Money:
    def __init__(self):
        self.money = 100

    def spend(self, spent):
        self.money -= spent

    def new_area(self):
        self.money += 50

    def death(self, health, fps):
        if health <= 0:
            self.money = int(self.money / 2)
            death_font = pg.font.SysFont('impact', 50, False)
            screen.blit(death_font.render('You have Died', True, (255, 0, 0)), (350, 200))
            pg.display.update()
            start = time.time()
            while True:
                if time.time() - start > 3:
                    break
                else:
                    continue
            fps.showing = 140
            return True


class Event:
    def __init__(self):
        self.space_cooldown = time.time()
        self.cooldown = time.time()

    def area_change(self, player, area, keys):
        if player.x < 10 and area.scroll == 0 and (keys[pg.K_s] or keys[pg.K_DOWN]) and area.area - 1 >= 1:
            area.scroll = -1990
            player.x = 850
            area.area -= 1
            screen.fill((176, 176, 176))
            screen.blit((pg.image.load("loading.png")), (0, 0))
            pg.display.update()
            time.sleep(2)
            player.item.clear()
        if player.x > 800 and abs(area.scroll) > 1990 and (keys[pg.K_s] or keys[pg.K_DOWN]) and area.area + 1 <= len(
                area.areas):
            area.scroll = 0
            player.x = 10
            area.area += 1
            screen.fill((176, 176, 176))
            screen.blit((pg.image.load("loading.png")), (0, 0))
            pg.display.update()
            time.sleep(2)
            player.item.clear()

    def event_check(self, player, fps, particles, area, money, power, materials):  # CHECKS ALL PLAYER EVENTS
        for events in pg.event.get():
            if events.type == pg.QUIT:
                run = False
                return run
            if events.type == pg.VIDEORESIZE:
                pg_screen[0] = pg.display.set_mode((events.w, events.h), pg.RESIZABLE)
            power.event_check(events, player, money)
            materials.event_check(events)
        keys = pg.key.get_pressed()
        if (keys[pg.K_d] or keys[pg.K_RIGHT]) and not keyboard.is_pressed('shift'):
            player.move(1, False, fps, True, area)
        if (keys[pg.K_a] or keys[pg.K_LEFT]) and not keyboard.is_pressed('shift'):
            player.move(-1, False, fps, False, area)
        if (keys[pg.K_d] or keys[pg.K_RIGHT]) and keyboard.is_pressed('shift'):
            player.move(1, True, fps, True, area)
        if (keys[pg.K_a] or keys[pg.K_LEFT]) and keyboard.is_pressed('shift'):
            player.move(-1, True, fps, False, area)
        if keys[pg.K_SPACE] and time.time() - self.space_cooldown > (60 * (1 / 2)) / 60:
            player.knockback()
            self.space_cooldown = time.time()
            string = f'particle{len(particles.keys())}'
            particles[string] = Particle_Set(player.x + (player.set_img.get_width() / 2) - area.scroll, player.y, 1, 4,
                                             (255, 255, 0), 440, area.scroll)
            name_bullet = f'bullet{len(area.bullet_list)}'
            bullet_name = Bullets(player.gunx, player.guny + 10, player.power, player.right)
            area.bullet_list[name_bullet] = bullet_name
        player.item_checking(area, keys)
        self.area_change(player, area, keys)
        player.jump(keys, fps)
        player.try_death(money, area, fps)
        return True


class Area:
    def __init__(self):
        all_maps = []
        mapping = []
        with open('maps.txt', 'r+') as maps:
            for i, info in enumerate(maps):
                if i == 2:
                    count = int(info.strip())
                    break
            current_count = 0
            new_map = []

            for i, map in enumerate(maps):
                if map.strip() == '':
                    current_count += 1
                    all_maps.append(new_map)
                    new_map = []
                if current_count + 13 * (current_count - 1) <= i <= current_count + 13 * (current_count - 1) + 19:
                    new_map.append(map.strip())

        all_maps.remove(all_maps[0])

        b1 = pg.transform.scale(pg.image.load('grass.png'), (40, 40))
        b2 = pg.transform.scale(pg.image.load('sky.png'), (40, 40))
        b3 = pg.transform.scale(pg.image.load('dirt.png'), (40, 40))
        skyline = [b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2,
                   b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2,
                   b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2, b2]
        grassline = [b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1,
                     b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1,
                     b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1, b1]
        dirtline = [b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3,
                    b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3,
                    b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3, b3]
        self.area = 1
        for var in all_maps:
            area_info = []
            for tiles in var:
                tiles = tiles.strip()
                if '0' in tiles or '1' in tiles or '2' in tiles:
                    tile_set = []
                    for tile in split(tiles):
                        if tile == '0':
                            tile_set.append(b2)
                        elif tile == '1':
                            tile_set.append(b1)
                        elif tile == '2':
                            tile_set.append(b3)
                    area_info.append(tile_set)
                elif tiles == '3':
                    area_info.append(skyline)
                elif tiles == '4':
                    area_info.append(grassline)
                elif tiles == '5':
                    area_info.append(dirtline)
            mapping.append(area_info)
        map1 = [skyline, skyline, skyline, skyline, skyline, skyline, skyline, skyline, skyline, skyline, skyline,
                grassline, dirtline]
        first_mon = [pg.transform.scale(pg.image.load('monster_1.png'), (60, 40)), 10, 3,
                     pg.transform.scale(pg.image.load('monster_1_drop.png'), (30, 30)),
                     (25, 160, 70), 10]  # pic, health, dps, drop, down_blit
        second_mon = [pg.transform.scale(pg.image.load('monster_2.png'), (120, 58)), 15, 5,
                      pg.transform.scale(pg.image.load('monster_2_drop.png'), (27, 22)), (255, 128, 0), 32]

        self.areas = [
            {'area': 1, 'map_pic': map1, 'monster_info': first_mon, 'monster_list': [], 'cap': 20},
            {'area': 2, 'map_pic': map1, 'monster_info': first_mon, 'monster_list': [], 'cap': 20},
            {'area': 3, 'map_pic': map1, 'monster_info': second_mon, 'monster_list': [], 'cap': 20},
            {'area': 4, 'map_pic': map1, 'monster_info': second_mon, 'monster_list': [], 'cap': 20},
        ]
        for i, var in enumerate(mapping[:len(self.areas)]):
            self.areas[i]['map_pic'] = var
        self.bullet_list = {}
        self.scroll = 0

    def spawning(self, fps, player, area, particles, money):
        val = list(self.areas[self.area - 1].values())
        if random.randint(1, 200) == 1 and len(val[3]) + 1 <= val[4]:
            new_mon = Monster((self.areas[self.area - 1]['monster_info'])[0],
                              (self.areas[self.area - 1]['monster_info'])[3], self.scroll,
                              (self.areas[self.area - 1]['monster_info'])[1])
            self.areas[self.area - 1]['monster_list'].append(new_mon)
        for var in self.areas[self.area - 1]['monster_list']:
            var.display(fps, ((self.areas[self.area - 1])['monster_info'][2]) / fps.showing, self.scroll, area, player,
                        particles)
            if var.death(particles, area, player, self.scroll):
                self.areas[self.area - 1]['monster_list'].remove(var)

    def area_draw(self):
        val = list(self.areas[self.area - 1].values())
        for i in range(len(val[1])):
            for l in range(len(val[1][i])):
                screen.blit(val[1][i][l], ((l * 40) + self.scroll, i * 40))


class Database:
    pass


class Visual:
    def __init__(self, area):
        self.area_text = Text(20, f'Area: {area.area} /  {len(area.areas)}', 20, 75, (255, 0, 0))
        self.color = [0, 0, 0]
        # self.rocks = pg.transform.scale(pg.image.load('rock.png'), (random.randint(30, 60), random.randint(30, 60)))

    def particles(self, particle, back_cor=0):
        for var in particle.items():
            if time.time() - var[1].start > 4:
                particle.pop(var[0])
                break
            var[1].particle_check(screen, back_cor)

    def health_draw(self, player):
        self.health_text.draw_font()
        pg.draw.rect(screen, (255, 0, 0), [23, 45, (player.health / 100) * 160, 10])  # x, y, len, wid
        pg.draw.line(screen, (0, 0, 0), (20, 45), (185, 45), 3)  # x, y, len, wid
        pg.draw.line(screen, (0, 0, 0), (20, 55), (185, 55), 3)  # x, y, len, wid
        pg.draw.line(screen, (0, 0, 0), (21, 45), (21, 55), 3)  # x, y, len, wid
        pg.draw.line(screen, (0, 0, 0), (184.8, 45), (184.8, 55), 3)  # x, y, len, wid

    def bullets(self, area, fps):
        val = list(area.bullet_list.values())
        key = list(area.bullet_list.keys())
        for i in range(len(val)):
            if val[i].move(fps):
                (area.bullet_list).pop(key[i])
                break

    def draw(self, area, player, money, fps, particle, power, materials):  # DISPLAYS PICTURES
        screen.fill(self.color)
        self.area_text = Text(20, f'Area: {area.area} /  {len(area.areas)}', 20, 75, (255, 0, 0))
        self.coins_text = Text(20, f'Money: {money.money}', 20, 55, (255, 255, 0))
        self.fps_count = Text(25, f'{fps.showing}' + 'FPS', 900, 50, (0, 0, 0))
        self.health_text = Text(20, f'Health: {int(round(player.health, 0))}/100', 20, 20, (0, 0, 0))
        area.area_draw()
        screen.blit(player.char, (player.x, player.y))
        player.display_gun()
        materials.draw(player)
        self.bullets(area, fps)
        self.area_text.draw_font()
        self.coins_text.draw_font()
        self.fps_count.draw_font()
        self.particles(particle, area.scroll)
        player.item_display(area.scroll)
        self.health_draw(player)
        power.visual()  # - IMPROVE CODE
        area.spawning(fps, player, area, particle, money)
        pg.draw.rect(pg_screen[0], self.color, [1000, 0, 1000, 1000])
        pg.display.update()


class Timing:
    def __init__(self):  # SETS FPS VARIABLES
        self.times = time.time()
        self.counting = 0
        self.showing = 250
        self.asd = []
        self.bruh = 0

    def fps_counting(self):  # TESTS FPS
        if time.time() - self.times > 1:
            self.showing = self.counting
            self.times = time.time()
            self.counting = 0
            self.asd.append(self.showing)
            self.bruh += 1
        self.counting += 1


def main():
    run = True
    event = Event()
    area = Area()
    money = Money()
    visual = Visual(area)
    player = Player()
    fps = Timing()
    particles = {}
    materials = Materials(Text, player)
    power = Power(Text)
    tile = Tiles()
    play = Thread(target=play_song)
    #play.start()
    while run:
        visual.draw(area, player, money, fps, particles, power, materials)  # DRAW
        fps.fps_counting()  # TRY FPS
        run = event.event_check(player, fps, particles, area, money, power, materials)  # CHECK EVENTS
        tile.tile_check(player, area)
    x = 0
    for i in range(len(fps.asd)):
        x += fps.asd[i]
    print(x / fps.bruh)


if __name__ == '__main__':
    main()
    pg.quit()
