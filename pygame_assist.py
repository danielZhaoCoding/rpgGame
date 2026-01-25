import pygame
import random
import time
import playsound
import os

pygame.init()


def write(font, font_size, text, x, y, color, screen):
    new_font = pygame.font.SysFont(str(font), font_size)
    screen.blit(new_font.render(str(text), True, color), (x, y))


def draw_character(image, x, y, screen):
    picture = pygame.image.load(image)
    screen(picture, (x, y))


def click(event, x1, y1, w, h):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if x1 < pygame.mouse.get_pos()[0] < x1 + w and y1 < pygame.mouse.get_pos()[1] < y1 + h:
            return True
        else:
            return False


def collide(x1, y1, w1, h1, x2, y2, w2, h2):
    if w1 > w2:
        if x1 > x2 or (x1 + w1) > (x2 + w2):
            if h1 > h2:
                if y2 > y1 or (y1 + h1) > (y2 + w2):
                    return True
            if h2 > h1:
                if y2 < y1 or (y1 + h1) < (y2 + w2):
                    return True


class Particles:
    def __init__(self, x, y, size, color, start_y, back_scroll=0):
        self.floor = start_y
        size = int(round(size, 1))
        self.x = x - back_scroll
        self.y = y - (size * random.randint(100, 150))
        self.color = color
        self.cords = {0: x, 1: y}
        self.size = (size * random.randint(80, 120) / 100)
        self.move_x = random.randint(-105, 105)
        self.create_time = time.time()
        self.alive_time = random.randint(200, 400) / 100
        if int(self.alive_time / 0.05) % 2 == 0:
            self.set = ((int(self.alive_time / 0.05)) / 2)
        else:
            self.set = ((int((self.alive_time / 0.05) - 1)) / 2)
        self.picture = pygame.Rect(self.cords[0], self.cords[1], self.size, self.size)
        self.reps = 0 - (self.set / 3.4)  # 2.5
        self.cords[0] -= random.randint(-40, 40)
        self.cords[1] -= random.randint(-15, 15)

    def moving(self, scroll=0):
        if self.reps <= 0:
            self.cords[1] -= ((self.reps ** 2) / 400) * 20
        elif (self.cords[1] + ((self.reps ** 2) / 100) + 2) < self.floor:
            self.cords[1] += ((self.reps ** 2) / 30) + 2
        if self.cords[1] > self.floor - 20:
            self.cords[0] += ((self.move_x / (int(self.alive_time / 0.05))) * 1.5) / 5
        else:
            self.cords[0] += ((self.move_x / (int(self.alive_time / 0.05))) * 1.5)
        if self.cords[1] > self.floor:
            self.cords[1] = self.floor
        self.picture = (self.cords[0] + scroll, self.cords[1], self.size, self.size)
        self.reps += 1


class Particle_Set:
    def __init__(self, x, y, count, size, color, start_y, back_scroll=0, randomcolor=False):
        #Backscroll is for scrolling windows
        #start_y is the 'floor' y value
        self.particle_list = []
        self.back_setx = back_scroll
        for i in range(int(count * (random.randint(80, 120) / 100))):
            if not randomcolor:
                particle = Particles(x, y, size, color, start_y, back_scroll)
            else:
                particle = Particles(x, y, size, (random.randint(0,255),random.randint(0,255),random.randint(0,255)), start_y, back_scroll)
            self.particle_list.append(particle)
        self.real_start = time.time()
        self.start = time.time()

    def particle_check(self, screen, scroll=0):
        if time.time() - self.start > 0.05:
            for var in self.particle_list:
                var.moving(scroll)
                if (time.time() - var.create_time) > var.alive_time:
                    self.particle_list.remove(var)
            self.start = time.time()
        for var in self.particle_list:
            pygame.draw.rect(screen, var.color, pygame.Rect(var.picture))


