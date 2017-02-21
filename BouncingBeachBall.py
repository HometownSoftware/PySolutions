'''
The MIT License (MIT)

Copyright (c) 2014, 2017 Hometown Software Solutions

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import time, math

import pygame, random
import pygame.gfxdraw
from pygame.locals import *
from numpy import array


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 153, 0)
GREY = (128, 128, 128)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)

# Custom colors (four time phases)
# Morning, afternoon, dusk, night
COLORS_SKY = [(120, 120, 224), (32, 92, 192),(64, 64, 175), (0, 0, 64)]
COLORS_OCEAN = [(8, 8, 128), (16, 16, 96), (16, 6, 64), (0, 0, 32)]
COLORS_OCEAN_WAVES = [(0, 0, 96),(12, 12, 64), (12, 12, 32), (0, 0, 16)]
COLORS_WAVE_CRASH = [(32, 32, 218, 244), (32, 32, 192, 244), (32, 32, 128, 244), (32, 32, 108, 244)]
COLORS_WATER_REFLECT = [(255, 153, 0, 192), (32, 192, 224, 192), (150, 153, 0, 192), (192, 224, 224, 192)]
COLORS_HORIZON = [(192, 120, 192),(92, 128, 192), (128, 92, 145), (0, 0, 16)]
COLORS_SAND = [(96, 96, 64), (150, 150, 64), (108, 108, 64), (80, 80, 64)]
COLORS_SANDPARTICLES = [(64, 64, 32),(64, 64, 16), (64, 64, 16), (32, 32, 24)]
COLORS_CELESTIAL = [(255, 153, 0),(255, 255, 64), (230, 180, 25), (255, 225, 255)]
COLORS_CELESTIAL_OUTLINE = [(255, 153, 0), (128, 128, 0), (255, 153, 0), BLACK]
COLORS_TEXT = [ORANGE, ORANGE, WHITE, WHITE]
COLORS_BEACH_BALL = [(192, 32, 32), (192, 192, 32), (32, 32, 192)]
LIGHTGREY = (192, 192, 192)

# States
STATE_INTRO = 0
STATE_RUN = 1
STATE_GAMEOVER = 2

# Window
W_WIDTH = 640
W_HEIGHT = 480

# Mechanics
SPEED = 2
GRAVITY = .5

class Main():
    def __init__(self):
        self.state = STATE_INTRO
        pygame.display.set_caption('Bouncing Beach Ball')
        self.FPS = 60
        self.fpsClock = pygame.time.Clock()
        self.score = 0
        hour = time.localtime()[3]
        if 6 <= hour <= 9:
            self.timecycle = 0
        elif 10 <= hour <= 16:
            self.timecycle = 1
        elif 17 <= hour <= 19:
            self.timecycle = 2
        else:
            self.timecycle = 3
        self.moonphase = random.randint(0, 15) % 8
        self.moon_offsets = [-20, -3, -2, -1, 0, 1, 2, 3]
        self.canvas = pygame.display.set_mode((W_WIDTH, W_HEIGHT), 0, 32)
        self.bg_objects = []
        self.lvl_objects = []
        self.txt = []
        self._create_bg()
        self.font = pygame.font.SysFont('miriam', 48)
        self._create_txt()
        self.ini_time = 0
        self.time_passed = 0
        self.bg_cam = [0, 0]
        self.lvl_cam = [0, 0]
        self.ui_cam = [0, 0]
        self.create_sounds()

    def _create_bg(self):
        bg_total_img = pygame.Surface([W_WIDTH * 2, W_HEIGHT], pygame.SRCALPHA, 32)
        bg_img = pygame.Surface([W_WIDTH, W_HEIGHT], pygame.SRCALPHA, 32)
        bg_img = bg_img.convert_alpha()
        rect_horizon = Rect(0, int(7 * W_HEIGHT/24), W_WIDTH, W_HEIGHT - int(7 * W_HEIGHT/24))
        rect_ocean = Rect(0, int(W_HEIGHT/3), W_WIDTH, W_HEIGHT - int(W_HEIGHT/3))
        rect_sand = Rect(0, int(7 * W_HEIGHT/12), W_WIDTH, W_HEIGHT - int(7 * W_HEIGHT/12))
        bg_img.fill(COLORS_SKY[self.timecycle])
        # Horizon
        bg_img.fill(COLORS_HORIZON[self.timecycle], rect_horizon)
        bg_img.fill(COLORS_OCEAN[self.timecycle], rect_ocean)
        bg_img.fill(COLORS_SAND[self.timecycle], rect_sand)
        # Sand particles
        for i in range(2048):
            x_range = random.randint(0, W_WIDTH)
            y_range = random.randint(int(7 * W_HEIGHT/12), W_HEIGHT)
            pygame.gfxdraw.pixel(bg_img, x_range, y_range, COLORS_SANDPARTICLES[self.timecycle])
        # Waves in ocean (4/12 to 7/12 exclusive) or (17/24 to 27/48)
        for i in range(128):
            x_range = random.randint(0, W_WIDTH - int(W_WIDTH/32))
            y_range = random.randint(int(17 * W_HEIGHT/48), int(27 * W_HEIGHT/48))
            pygame.gfxdraw.hline(bg_img, x_range, int(x_range + W_WIDTH/4), y_range, COLORS_OCEAN_WAVES[self.timecycle])
            if int(x_range + W_WIDTH/4 >= W_WIDTH):
                pygame.gfxdraw.hline(bg_img, 0, int(W_WIDTH/8), y_range, COLORS_OCEAN_WAVES[self.timecycle])
        # "Wave crashes"
        _wave_crash = pygame.Surface([W_WIDTH, int(W_HEIGHT/16)], pygame.SRCALPHA, 32)
        _wave_crash = _wave_crash.convert_alpha()
        _w_rect = _wave_crash.get_rect()
        pygame.gfxdraw.filled_ellipse(_wave_crash, int(_w_rect.width/4),0,
                                      int(_w_rect.width/4), int(_w_rect.height), COLORS_WAVE_CRASH[self.timecycle])
        pygame.gfxdraw.filled_ellipse(_wave_crash, int(3*_w_rect.width/4),0,
                                      int(_w_rect.width/4), int(_w_rect.height), COLORS_WAVE_CRASH[self.timecycle])
        # Finalizing the background
        bg_img.blit(_wave_crash, (0, int(7 * W_HEIGHT/12)), None, BLEND_MAX)
        bg_total_img.blit(bg_img, (0,0))
        bg_total_img.blit(bg_img, (W_WIDTH, 0))
        self.bg = bg_total_img
        # Ground
        gnd_img = pygame.Surface([W_WIDTH, 1], pygame.SRCALPHA, 32)
        gnd_img = gnd_img.convert_alpha()
        self.bg_objects.append({'name': 'ground', 'image': gnd_img,
                                'rect': Rect(0, W_HEIGHT - 1, W_WIDTH, 1), 'active': True})
        # Sun/Moon
        _r = int(W_WIDTH/8) if W_WIDTH < W_HEIGHT else int(W_HEIGHT/16)
        _d = _r * 2
        sun_img = pygame.Surface([_d, _d], pygame.SRCALPHA, 32)
        sun_img = sun_img.convert_alpha()
        _orig = (int(sun_img.get_width()/2), int(sun_img.get_height()/2))
        pygame.gfxdraw.filled_circle(sun_img, _orig[0], _orig[1], _r, COLORS_CELESTIAL[self.timecycle])
        # Moon cycles
        if self.timecycle == 3 and self.moonphase != 0:
            _moon_phase_img = pygame.Surface([_d, _d], pygame.SRCALPHA, 32)
            _moon_phase_img = _moon_phase_img.convert_alpha()
            pygame.gfxdraw.filled_circle(_moon_phase_img, _orig[0] +
                                         int(self.moon_offsets[self.moonphase] * _r/3), _orig[1], _r,
                                         (240, 240, 192, 255))
            sun_img.blit(_moon_phase_img, _moon_phase_img.get_rect(), None, BLEND_RGB_SUB)
        pygame.gfxdraw.aacircle(sun_img, _orig[0], _orig[1], _r, COLORS_CELESTIAL_OUTLINE[self.timecycle])
        _sun_rect = Rect(int(2 * W_WIDTH/3), int(W_HEIGHT/16), _d, _d)
        self.bg_objects.append({'name': 'sun', 'image': sun_img, 'rect': _sun_rect, 'active': True})
        # Water reflection
        _reflect_img = pygame.Surface([2 * W_WIDTH/5, W_HEIGHT/4], pygame.SRCALPHA, 32)
        _reflect_img = _reflect_img.convert_alpha()
        _reflect_width = 5
        _reflect_x_offset = 0
        _reflect_pivot = int(_reflect_img.get_rect().width/2)
        for i in range(0, int(_reflect_img.get_rect().height), 2):
            _reflect_pt = _reflect_pivot - _reflect_x_offset
            pygame.gfxdraw.hline(_reflect_img, _reflect_pt,
                                 _reflect_pt + _reflect_width, i, COLORS_WATER_REFLECT[self.timecycle])
            _reflect_width += random.randint(0, 4)
            _reflect_x_offset += random.randint(0, 2)
        _reflect_rect_offset = int(3 * W_WIDTH/5) if W_WIDTH < W_HEIGHT else int(W_WIDTH/2)
        _reflect_rect = Rect(_reflect_rect_offset, W_HEIGHT/3,
                             _reflect_img.get_rect().width, _reflect_img.get_rect().height)
        self.bg_objects.append({'name': 'water_reflect', 'image': _reflect_img, 'rect': _reflect_rect, 'active': True})

    def _create_ball(self):
        _r = int(W_WIDTH/12) if W_WIDTH < W_HEIGHT else int(W_HEIGHT/16)
        _d = _r * 2
        ball_img = pygame.Surface([_d, _d], pygame.SRCALPHA, 32)
        ball_img = ball_img.convert_alpha()
        _orig = (int(ball_img.get_width()/2), int(ball_img.get_height()/2))
        pygame.gfxdraw.filled_circle(ball_img, _orig[0], _orig[1], _orig[0], WHITE)
        pattern_angle = 30
        for i in range(0, pattern_angle):
            pygame.gfxdraw.pie(ball_img, _orig[0], _orig[1], _r, -65 + i, -65 + pattern_angle, COLORS_BEACH_BALL[0])
            pygame.gfxdraw.pie(ball_img, _orig[0], _orig[1], _r, 165 + i, 165 + pattern_angle, COLORS_BEACH_BALL[1])
            pygame.gfxdraw.pie(ball_img, _orig[0], _orig[1], _r, 45 + i, 45 + pattern_angle, COLORS_BEACH_BALL[2])
        pygame.gfxdraw.filled_circle(ball_img, _orig[0], _orig[1], int(_orig[0]/4), WHITE)
        # Simple shading
        _ball_shadow = pygame.Surface([_d, _d], pygame.SRCALPHA, 32)
        _ball_shadow = _ball_shadow.convert_alpha()
        pygame.gfxdraw.filled_circle(_ball_shadow , _orig[0], _orig[1], _r, (255, 255, 255, 128))
        pygame.gfxdraw.filled_circle(_ball_shadow , _orig[0], _orig[1], int(2 * _r/3), (255, 255, 255, 0))
        ball_img.blit(_ball_shadow, _ball_shadow.get_rect())
        # Borders
        pygame.gfxdraw.aacircle(ball_img, _orig[0], _orig[1], _r, BLACK)
        _ball_coord_rect = Rect(int(W_WIDTH/2 - _r), int(W_HEIGHT/3), _d, _d)
        _ball_hitbox = Rect(int(W_WIDTH/2 - _r), int(W_HEIGHT/3),
                            int(ball_img.get_width() - _d/10), int(ball_img.get_height() - _d/10))
        self.ball = {'name': 'ball', 'image': ball_img, 'rect': _ball_coord_rect, 'radius': _r, 'hitbox': _ball_hitbox,
                     'active': True,  'velo': 1, 'accel': GRAVITY}

    def _create_poles(self, pos):
        _sizes = [int(W_HEIGHT/4), int(W_HEIGHT/3), int(W_HEIGHT/2)]
        _starts = [int(W_HEIGHT/4), int(W_HEIGHT/3), int(W_HEIGHT/5), int(W_HEIGHT/6)]
        _gap_size = _sizes[random.randint(0, len(_sizes) - 1)]
        # y-position
        _gap_start_pos = _starts[random.randint(0, len(_starts) - 1)]
        _pole_width = W_WIDTH/8 if W_WIDTH < W_HEIGHT else int(W_HEIGHT/12)
        # Scoring area
        score = pygame.Surface([_pole_width/2, _gap_size], pygame.SRCALPHA, 32)
        score = score.convert_alpha()
        score_rect = Rect(pos + _pole_width/4, _gap_start_pos, _pole_width/2, _gap_size)
        self.lvl_objects.append({'name': 'pole_score', 'image': score, 'rect': score_rect, 'active': True})
        # Top pole
        pole_top = pygame.Surface([_pole_width, _gap_start_pos], pygame.SRCALPHA, 32)
        pole_top = pole_top.convert_alpha()
        pole_top.fill(GREY)
        # Bottom pole
        _bottom_size = W_HEIGHT - (_gap_start_pos + _gap_size)
        pole_bottom = pygame.Surface([_pole_width, _bottom_size], pygame.SRCALPHA, 32)
        pole_bottom = pole_bottom.convert_alpha()
        pole_bottom.fill(GREY)
        # Shadows
        _shadow_top = Rect(int(2 * _pole_width/3), pole_top.get_rect().y, _pole_width/3, _gap_start_pos)
        _shadow_bottom = Rect(int(2 * _pole_width/3), pole_bottom.get_rect().y, _pole_width/3, _bottom_size)
        pygame.gfxdraw.box(pole_top, _shadow_top, LIGHTGREY)
        pygame.gfxdraw.box(pole_bottom, _shadow_bottom, LIGHTGREY)
        # Borders
        pygame.draw.rect(pole_top, BLACK, pole_top.get_rect(), 5)
        pygame.draw.rect(pole_bottom, BLACK, pole_bottom.get_rect(), 5)
        # Pole positions
        pole_top_rect = Rect(pos, 0, _pole_width, _gap_start_pos)
        pole_bottom_rect = Rect(pos, _gap_start_pos + _gap_size, _pole_width, _bottom_size)
        self.lvl_objects.append({'name': 'pole', 'image': pole_top, 'rect': pole_top_rect, 'active': True})
        self.lvl_objects.append({'name': 'pole', 'image': pole_bottom, 'rect': pole_bottom_rect, 'active': True})

    def _create_txt(self):
        txt_logo_line1 = self.font.render('Bouncing', 1, GOLD)
        _rect = txt_logo_line1.get_rect()
        _rect.centerx = W_WIDTH/2
        _rect.y = int(W_HEIGHT/2) - int(W_HEIGHT/4)
        self.txt.append({'name': 'logo line 1', 'image': txt_logo_line1, 'rect': _rect})
        # Line 2
        txt_logo_line2 = self.font.render('Beach Ball', 1, GOLD)
        _rect = txt_logo_line2.get_rect()
        _rect.centerx = W_WIDTH/2
        _rect.y = int(W_HEIGHT/2) - int(W_HEIGHT/4) + txt_logo_line1.get_rect().height
        self.txt.append({'name': 'logo line 2', 'image': txt_logo_line2, 'rect': _rect})
        # Instructions
        txt_tap_start = self.font.render('Tap to start', 1, BLACK)
        _rect = txt_tap_start.get_rect()
        _rect.centerx = W_WIDTH/2
        _rect.y = int(W_HEIGHT/2) + int(W_HEIGHT/8)
        self.txt.append({'name': 'instructions', 'image': txt_tap_start, 'rect': _rect})

    def create_sounds(self):
        pygame.mixer.init()
        snd1 = [[100*random.randint(220,440) for x in range(2)] for x in range(2)]
        snd2 = [[100*random.randint(660,880) for x in range(2)] for x in range(2)]
        self.snd_bounce = pygame.sndarray.make_sound(array(snd1))
        self.snd_fail = pygame.sndarray.make_sound(array(snd2))

    def _intersect_bounds(self, rect):
        r = self.ball['radius']
        ball = self.ball['rect']
        center = (ball.x + ball.width/2, ball.y + ball.height/2)
        # left, top, bottom, right
        return rect.collidepoint(center) or rect.collidepoint((center[0]-r, center[1])) or \
               rect.collidepoint((center[0], center[1]-r)) or rect.collidepoint((center[0], center[1]+r)) or \
               rect.collidepoint((center[0]+r, center[1]))

    def _intersect_ball(self, p1, p2):
        r2 = self.ball['radius'] ** 2
        ball = self.ball['rect']
        origin = (ball.x + ball.width/2, ball.y + ball.height/2)
        dx1, dx2 = p1[0] - origin[0], p2[0] - origin[0]
        dy1, dy2 = p1[1] - origin[1], p2[1] - origin[1]
        mid_dx, mid_dy = (p1[0] + p2[0])/2 - origin[0], (p1[1] + p2[1])/2 - origin[1]
        dist_p1 = dx1 ** 2 + dy1 ** 2
        dist_p2 = dx2 ** 2 + dy2 ** 2
        dist_mid = mid_dx ** 2 + mid_dy ** 2
        return dist_p1 <= r2 or dist_p2 <= r2 or dist_mid <= r2

    # Not working properly
    def _test_intersect_ball(self, p1, p2):
        # Formula:
        # https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
        r = self.ball['radius']
        ball = self.ball['rect']
        origin = (ball.x + ball.width/2, ball.y + ball.height/2)
        top = abs((p2[1] - p1[1]) * origin[0] - (p2[0] - p1[0]) * origin[1] + p2[0] * p1[1] - p2[1] * p1[0])**2
        bottom = (p2[1]-p1[1])**2 + (p2[0]-p1[0])**2
        print(top/bottom)
        return top/bottom <= r

    def collideball(self, rect):
        ball = self.ball['rect']
        center = (ball.x + ball.width/2, ball.y + ball.height/2)
        #if rect.collidepoint(center):
        #    print(rect)
        #    print(self._test_intersect_ball((rect.x, rect.y + rect.height), (rect.x, rect.y)))
        return self._intersect_bounds(rect) or\
            self._intersect_ball((rect.x, rect.y), (rect.x + rect.width, rect.y)) or\
            self._intersect_ball((rect.x + rect.width, rect.y), (rect.x + rect.width, rect.y + rect.height)) or \
            self._intersect_ball((rect.x + rect.width, rect.y + rect.height), (rect.x, rect.y + rect.height)) or \
            self._intersect_ball((rect.x, rect.y + rect.height), (rect.x, rect.y))

    def reset(self):
        self.ini_time = 0
        self.time_passed = 0
        self.timecycle = (self.timecycle + 1) % 4
        if self.timecycle == 3:
            self.moonphase = (self.moonphase + 1) % 8
        self.score = 0
        self.bg_objects = []
        self.lvl_objects = []
        self._create_bg()
        self._create_ball()

    def update(self):
        self.bg_objects[:] = [o for o in self.bg_objects if o['active']]
        self.lvl_objects[:] = [o for o in self.lvl_objects if o['active']]
        # ball handling
        if self.state == STATE_GAMEOVER and self.ball['rect'].y < W_HEIGHT - self.ball['rect'].height/2:
            self.ball['velo'] += self.ball['accel']
            self.ball['rect'].y = max(self.ball['rect'].y + self.ball['velo'], -int(self.ball['rect'].height/2))
        if self.state == STATE_RUN:
            self.ball['velo'] += self.ball['accel']
            self.ball['rect'].x += SPEED
            self.ball['rect'].y = max(self.ball['rect'].y + self.ball['velo'], -int(self.ball['rect'].height/2))
            # Determine when the poles are made
            if self.ini_time > int(self.FPS):
                if self.time_passed > int(3 * self.FPS/2):
                    self._create_poles(self.ball['rect'].x + self.ball['rect'].width + W_WIDTH/2)
                    self.time_passed = 0
                self.time_passed += 1
            self.ini_time += 1
            for o in self.lvl_objects:
                if o['name'] == 'pole' or o['name'] == 'pole_score':
                    if self.ball['rect'].x - o['rect'].x > W_WIDTH:
                        o['active'] = False
                if o['name'] == 'pole':
                    if self.collideball(o['rect']):
                        self.state = STATE_GAMEOVER
                        self.snd_fail.play()
                elif o['name'] == 'pole_score':
                    if o['active'] and self.collideball(o['rect']):
                        self.score += 1
                        o['active'] = False
            for o in self.bg_objects:
                if o['name'] == 'ground':
                    o['rect'].x = self.ball['rect'].x - W_WIDTH/2
                    if self.ball['rect'].colliderect(o['rect']):
                        self.state = STATE_GAMEOVER
                        self.snd_fail.play()
    def draw(self):
        self.canvas.fill(BLACK)
        # Background
        self.canvas.blit(self.bg, (self.bg_cam[0], self.bg_cam[1]))
        if not self.state == STATE_GAMEOVER:
            self.bg_cam[0] -= 1
            if self.bg_cam[0] < -W_WIDTH:
                self.bg_cam[0] = 0
        # Background objects
        for o in self.bg_objects:
            self.canvas.blit(o['image'], o['rect'])
        # Ball
        if self.state == STATE_RUN or self.state == STATE_GAMEOVER:
            # Poles
            for o in self.lvl_objects:
                x_dist = o['rect'].x - self.ball['rect'].x - self.ball['rect'].width/2 + W_WIDTH/2
                self.canvas.blit(o['image'], (x_dist, o['rect'].y))
            self.canvas.blit(self.ball['image'], (W_WIDTH/2 - self.ball['rect'].width/2, self.ball['rect'].y))
        if self.state == STATE_INTRO:
            for o in self.txt:
                self.canvas.blit(o['image'], o['rect'])
        # Tap to retry
        if self.state == STATE_GAMEOVER:
            gameover_txt = self.font.render('Tap to retry', 1, COLORS_TEXT[self.timecycle])
            gameover_txt_rect = gameover_txt.get_rect()
            gameover_txt_rect.x = int(W_WIDTH/2 - gameover_txt_rect.width/2)
            gameover_txt_rect.y = int(W_HEIGHT/2)
            self.canvas.blit(gameover_txt, gameover_txt_rect)
        # Score
        score_txt = self.font.render('Score: ' + str(self.score), 1, COLORS_TEXT[self.timecycle])
        score_txt_rect = score_txt.get_rect()
        score_txt_rect.x = W_WIDTH - score_txt_rect.width
        score_txt_rect.y = 0
        self.canvas.blit(score_txt, score_txt_rect)
        self.fpsClock.tick(self.FPS)
        pygame.display.update()
        pygame.display.flip()

    def render(self):
        self.update()
        self.draw()

    def get_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                import sys
                pygame.mixer.quit()
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                keys=pygame.key.get_pressed()
                if keys[K_r]:
                    self.reset()
                    self.state = STATE_RUN
            elif event.type == MOUSEBUTTONDOWN:
                if self.state == STATE_INTRO:
                    self._create_ball()
                    self.state = STATE_RUN
                elif self.state == STATE_GAMEOVER:
                    self.reset()
                    self.state = STATE_RUN
                elif self.state == STATE_RUN:
                    self.ball['velo'] = -GRAVITY * 10
                    self.snd_bounce.play()

if __name__ == "__main__":
    pygame.init()
    f = Main()
    while True:
        f.render()
        f.get_input()
    pygame.mixer.quit()