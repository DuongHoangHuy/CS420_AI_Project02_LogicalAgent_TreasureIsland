import pygame
pygame.init()
from helpers.constant import WIN_W, MAP_W, LOG_W, LOG_H
from helpers.textrect import render_textrect
from Grid import Grid

LOG_X = MAP_W + (WIN_W - MAP_W - LOG_W)//2
LOG_Y = 20

LOG_LINES = 10
LOG_COLOR = (222, 222, 222)

class Logger:
    def __init__(self, fout_path):
        self.messages = []
        self.area = pygame.Rect(LOG_X, LOG_Y, LOG_W, LOG_H)
        self.font = pygame.font.SysFont('Arial', 12)
        self.fout_path = fout_path

    def export_log(self):
        f = open(self.fout_path, "w")
        for turn_log in self.messages:
            f.write(turn_log)
        print('Save logs successfully')
        f.close()

    def recieve_message(self, messages, cur_turn):
        if not messages:
            return
        if cur_turn > len(self.messages)-1:
            self.messages.append('')
        splitted_messages = messages.split('\n')
        splitted_messages = [s for s in splitted_messages if s != '']
        if '' in splitted_messages:
            splitted_messages = splitted_messages.remove('')
        
        for message in splitted_messages:
            self.messages[cur_turn] += '\n> ' + message

    def draw(self, cur_turn, win):
        rendered_text = render_textrect(self.messages[cur_turn], self.font, self.area, (0,0,0), LOG_COLOR)
        win.blit(rendered_text, self.area.topleft)
