# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 21:45:09 2024

@author: lcuev
"""
import pygame

vertical = (0, 1)
horizontal = (1, 0)
left_diag = (0.707, 0.707)
right_diag = (0.707, -0.707)


class GUI:
    bg_col = (0, 0, 0)
    fg_col = (255, 255, 255)
    pen_col = (255, 255, 0)
    erase_col = (255, 0, 255)
    directions = {vertical: '|',
                  horizontal: '-',
                  left_diag: '\\',
                  right_diag: '/'}

    def __init__(self, length=32, block_size=32):
        pygame.init()
        self.length = length
        self.area = length ** 2
        self.block_size = block_size
        self.surface = pygame.display.set_mode((length * block_size,)*2)
        self.font = pygame.font.Font('CascadiaMono.ttf', 32)
        self.chars = [' ' for a in range(self.area)]
        self.pen_down = False
        self.erase = False
        self.running = True
        self.last_change = None
        self.cursor_pos = pygame.mouse.get_pos()
        pygame.display.set_caption('Hopfield')

    def __del__(self):
        pygame.quit()

    def flatten(self, left, right):
        return left // self.block_size * self.length + right // self.block_size

    def unflatten(self, index):
        return index // self.length * self.block_size, index % self.length * self.block_size

    def clear(self):
        self.chars = [' ' for a in range(self.area)]

    def abs_dot(self, a, b):
        return abs(a[0] * b[0] + a[1] * b[1])

    def get_char(self, direction):
        char = '·'
        global_max = 0
        for key, value in self.directions.items():
            local_max = self.abs_dot(direction, key)
            if local_max > global_max:
                char = value
                global_max = local_max
        return char

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.pen_down = True
                self.cursor_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP:
                self.pen_down = False
                self.last_change = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    self.clear()
                if event.key == pygame.K_e:
                    self.erase = not self.erase

    def update(self):
        if self.pen_down:
            if self.erase:
                left, right = pygame.mouse.get_pos()
                index = self.flatten(right, left)
                dleft = left - self.cursor_pos[0]
                dright = right - self.cursor_pos[1]
                self.chars[index] = ' '
            else:
                left, right = pygame.mouse.get_pos()
                index = self.flatten(right, left)
                if self.last_change != index:
                    dleft = left - self.cursor_pos[0]
                    dright = right - self.cursor_pos[1]
                    self.chars[index] = self.get_char((dleft, dright))
                    self.last_change = index
                self.cursor_pos = (left, right)

    def display(self):
        self.surface.fill(self.bg_col)
        for index in range(self.area):
            left, right = self.unflatten(index)
            char_surf = self.font.render(self.chars[index], True, self.fg_col)
            char_rect = char_surf.get_rect()
            char_rect.topleft = (right, left)
            self.surface.blit(char_surf, char_rect)

        if self.erase:
            mode = self.font.render('eraser', True, self.erase_col)
        else:
            mode = self.font.render('pen', True, self.pen_col)

        mode_rect = mode.get_rect()
        mode_rect.topleft = (5, 0)
        self.surface.blit(mode, mode_rect)
        pygame.display.update()

    def loop(self):
        self.handle_events()
        self.update()
        self.display()
        return self.running


if __name__ == '__main__':
    gui = GUI()
    while gui.loop():
        pass
    del gui
