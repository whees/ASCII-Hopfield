# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 21:45:09 2024

@author: lcuev
"""
import pygame
from numpy import tanh

vertical = (0, 1)
horizontal = (1, 0)
left_diag = (0.707, 0.707)
right_diag = (0.707, -0.707)


class Hopfield:
    def __init__(self, length=16**2, neuron_length=5):
        self.length = length
        self.area = self.flatten(length)
        self.dict = self.get_dict(self.area)
        self.neuron_length = neuron_length
        self.neuron_area = self.flatten(neuron_length)
        self.neuron_dict = self.get_dict(self.neuron_area)
        self.weights = [[0 for n in range(self.neuron_area)]
                        for a in range(self.area)]

    def get_dict(self, length):
        dict = {}
        for i in range(length):
            dict[i] = self.unflatten(i)
        return dict

    def unflatten(self, index):
        f = int(0.5 * (8 * index + 1) ** 0.5 + 0.5)
        return f, index - f * (f - 1) // 2

    def flatten(self, left, right=0):
        return left * (left - 1) // 2 + right

    def activate(self, input):
        for i in range(self.length):
            for j in range(self.neuron_length):
                input[i][j] = tanh(input[i][j])
        return input

    def memorize(self, output):
        for key, value in self.dict.items():
            left, right = value
            for n_key, n_value in self.neuron_dict.items():
                n_left, n_right = n_value
                self.weights[key][n_key] += output[left][n_left] * \
                    output[right][n_right]

    def recall(self, input, rate=2**-2):
        output = [[input[i][j]
                   for j in range(self.neuron_length)] for i in range(self.length)]
        for key, value in self.dict.items():
            left, right = value
            for n_key, n_value in self.neuron_dict.items():
                n_left, n_right = n_value
                output[left][n_left] += self.weights[key][n_key] * \
                    input[right][n_right] * rate
                output[right][n_right] += self.weights[key][n_key] * \
                    input[left][n_left] * rate
        return self.activate(output)


class GUI:
    bg_col = (0, 0, 0)
    fg_col = (255, 255, 255)
    pen_col = (255, 255, 0)
    erase_col = (255, 0, 255)
    recall_col = (255, 0, 0)
    directions = {vertical: '|',
                  horizontal: '—',
                  left_diag: '\\',
                  right_diag: '/'}
    indices = {'·': 0,
               '|': 1,
               '—': 2,
               '\\': 3,
               '/': 4}
    symbols = ['·', '|', '—', '\\', '/']

    def __init__(self, length=16, block_size=64):
        pygame.init()
        self.length = length
        self.area = length ** 2
        self.block_size = block_size
        self.surface = pygame.display.set_mode((length * block_size,) * 2)
        self.font = pygame.font.Font('CascadiaMono.ttf', block_size)
        self.chars = [' ' for a in range(self.area)]
        self.array = self.get_array()
        self.pen_down = False
        self.erase = False
        self.recall = False
        self.running = True
        self.last_change = None
        self.cursor_pos = pygame.mouse.get_pos()
        self.hopfield = Hopfield(self.area)
        pygame.display.set_caption('Hopfield')

    def __del__(self):
        pygame.quit()

    def get_array(self):
        array = [[-1] * 5 for a in range(self.area)]
        for a in range(self.area):
            index = self.indices.get(self.chars[a])
            if index is not None:
                array[a][index] = 1
        return array

    def get_chars(self):
        chars = [' ' for a in range(self.area)]
        for a in range(self.area):
            maximum = max(self.array[a])
            if maximum > 0.5:
                chars[a] = self.symbols[self.array[a].index(maximum)]
            else:
                chars[a] = ' '
        return chars

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
                if event.key == pygame.K_m:
                    self.hopfield.memorize(self.array)
                if event.key == pygame.K_r:
                    self.recall = not self.recall

    def update(self):
        if self.recall:
            self.array = self.hopfield.recall(self.array)
            self.chars = self.get_chars()
        elif self.pen_down:
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
            self.array = self.get_array()

    def display(self):
        self.surface.fill(self.bg_col)
        for index in range(self.area):
            left, right = self.unflatten(index)
            char_surf = self.font.render(self.chars[index], True, self.fg_col)
            char_rect = char_surf.get_rect()
            char_rect.topleft = (right, left)
            self.surface.blit(char_surf, char_rect)

        if self.recall:
            mode = self.font.render('recall', True, self.recall_col)
        elif self.erase:
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
