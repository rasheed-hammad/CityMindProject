
# CityMind Real-Time City Simulation Renderer

import pygame
import math
import random
from collections import deque

# particle system

class Particle:
  
    def __init__(self, x, y, vx, vy, color, lifetime, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color[:3], alpha)
        pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
        screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

# managing effect of particles
class ParticleSystem:
    
    def __init__(self):
        self.particles = []
    
    def emit_explosion(self, x, y, color=(255, 200, 0), count=20):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2
            self.particles.append(
                Particle(x, y, vx, vy, color, 40, size=random.randint(2, 4))
            )
    
    def emit_water_splash(self, x, y):
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append(
                Particle(x, y, vx, vy, (59, 130, 246), 60, size=random.randint(3, 6))
            )
    
    def emit_siren_pulse(self, x, y):
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 2)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = (255, 0, 0) if random.random() > 0.5 else (59, 130, 246)
            self.particles.append(Particle(x, y, vx, vy, color, 30, size=2))
    # industry smoke
    def emit_smoke(self, x, y):
        if random.random() > 0.6:  # Rate limit
            vx = random.uniform(-0.5, 0.5)
            vy = random.uniform(-1.5, -0.5)
            color = (200, 200, 200)
            self.particles.append(Particle(x, y, vx, vy, color, 60, size=random.randint(2, 5)))
    # electric sparks
    def emit_sparks(self, x, y):
        for _ in range(2):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = (150, 255, 255) if random.random() > 0.5 else (255, 255, 255)
            self.particles.append(Particle(x, y, vx, vy, color, 15, size=random.randint(1, 3)))
            
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)


# water animation

class FloodAnimation:
    def __init__(self):
        self.floods = {}
    
    def add_flood(self, edge, x1, y1, x2, y2):
        self.floods[edge] = {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'progress': 0,
            'wave': 0
        }
    
    def remove_flood(self, edge):
        if edge in self.floods:
            del self.floods[edge]
    
    def update(self):
        for edge in self.floods:
            self.floods[edge]['progress'] = min(
                100,
                self.floods[edge]['progress'] + 2
            )
            self.floods[edge]['wave'] += 0.1
    
    def draw(self, screen):
        for edge, data in self.floods.items():
            for i in range(5):
                offset = (data['wave'] + i * 20) % 100
                progress = data['progress'] / 100

                x = data['x1'] + (data['x2'] - data['x1']) * (offset / 100) * progress
                y = data['y1'] + (data['y2'] - data['y1']) * (offset / 100) * progress

                size = 8 - i
                alpha = int(180 - i * 30)

                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    s,
                    (59, 130, 246, alpha),
                    (size, size),
                    size
                )

                screen.blit(s, (int(x - size), int(y - size)))


# buttons

class Button:
    def __init__(self, x, y, width, height, text, icon="", color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.hovered = False
        self.active = False
        self.color = color
        self.scale = 1.0

    def draw(self, screen, font):
        target_scale = 1.03 if self.hovered else 1.0
        self.scale += (target_scale - self.scale) * 0.12

        scaled_w = int(self.rect.width * self.scale)
        scaled_h = int(self.rect.height * self.scale)

        draw_rect = pygame.Rect(
            self.rect.centerx - scaled_w // 2,
            self.rect.centery - scaled_h // 2,
            scaled_w,
            scaled_h
        )

        if self.color:
            base = self.color
        else:
            base = (42, 52, 72)

        if self.active:
            glow = (59, 130, 246)
        else:
            glow = base

        # shadow
        shadow = pygame.Surface((draw_rect.width + 20, draw_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*glow, 45), (10, 10, draw_rect.width, draw_rect.height), border_radius=20)
        screen.blit(shadow, (draw_rect.x - 10, draw_rect.y - 10))

        button_surface = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, (*base, 255), (0, 0, draw_rect.width, draw_rect.height), border_radius=18)
        
        # glass effect
        pygame.draw.rect(button_surface, (255, 255, 255, 25), (0, 0, draw_rect.width, draw_rect.height // 2), border_top_left_radius=18, border_top_right_radius=18)
        
        pygame.draw.rect(button_surface, (255, 255, 255, 40), (0, 0, draw_rect.width, draw_rect.height), width=1, border_radius=18)

        screen.blit(button_surface, draw_rect)

        if self.active:
            pygame.draw.rect(screen, (125, 211, 252), draw_rect, width=2, border_radius=18)

        text_color = (245, 248, 255)

        label = f"{self.icon}  {self.text}" if self.icon else self.text

        txt = font.render(label, True, text_color)
        txt_rect = txt.get_rect(center=draw_rect.center)

        screen.blit(txt, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True

        return False


# notification system

class Notification:
    def __init__(self, message, type='info'):
        self.message = message
        self.type = type
        self.lifetime = 180
        self.alpha = 0
        self.y_offset = 0
    
    def update(self):
        self.lifetime -= 1

        if self.lifetime > 150:
            self.alpha = min(255, self.alpha + 20)
        elif self.lifetime < 30:
            self.alpha = max(0, self.alpha - 10)

        self.y_offset = max(0, self.y_offset - 0.5)

        return self.lifetime > 0


class NotificationManager:
    def __init__(self):
        self.notifications = deque(maxlen=3)
    
    def add(self, message, type='info'):
        notif = Notification(message, type)
        self.notifications.append(notif)
    
    def update(self):
        self.notifications = deque(
            [n for n in self.notifications if n.update()],
            maxlen=3
        )
    
    def draw(self, screen, font, x, y):
        offset = 0

        for notif in self.notifications:
            color_map = {
                'info': (59, 130, 246),
                'warning': (251, 191, 36),
                'error': (239, 68, 68),
                'success': (34, 197, 94)
            }

            bg_color = color_map.get(notif.type, (59, 130, 246))

            width = 280
            height = 60

            s = pygame.Surface((width, height), pygame.SRCALPHA)

            pygame.draw.rect(
                s,
                (*bg_color, notif.alpha // 2),
                (0, 0, width, height),
                border_radius=12
            )

            pygame.draw.rect(
                s,
                (*bg_color, notif.alpha),
                (0, 0, width, height),
                width=2,
                border_radius=12
            )

            text_surf = font.render(
                notif.message[:35],
                True,
                (255, 255, 255, notif.alpha)
            )

            s.blit(text_surf, (15, 20))

            screen.blit(s, (x, y + offset + notif.y_offset))

            offset += height + 10


# floating orbits

class FloatingOrb:
    def __init__(self, x, y, radius, color, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.offset = random.uniform(0, 100)

    def update(self, time):
        self.y += math.sin((time + self.offset) * self.speed) * 0.08
        self.x += math.cos((time + self.offset) * self.speed) * 0.05

    def draw(self, screen):
        surf = pygame.Surface(
            (self.radius * 4, self.radius * 4),
            pygame.SRCALPHA
        )

        for i in range(4):
            alpha = max(10, 45 - i * 10)

            pygame.draw.circle(
                surf,
                (*self.color, alpha),
                (self.radius * 2, self.radius * 2),
                self.radius + i * 6
            )

        screen.blit(
            surf,
            (self.x - self.radius * 2, self.y - self.radius * 2)
        )


# city renderer

class CityRenderer:
    def __init__(self, city_graph, cell_size=65):
        self.graph = city_graph

        # Static layout constants (panels around the grid)
        self.sidebar_width = 360
        self.top_bar_height = 180
        self.bottom_pad = 30
        chrome_w = self.sidebar_width + 60                      
        chrome_h = self.top_bar_height + self.bottom_pad + 30   

        pygame.init()
        try:
            info = pygame.display.Info()
            screen_w, screen_h = info.current_w, info.current_h
        except Exception:
            screen_w, screen_h = 1366, 768  

        usable_w = screen_w - 40
        usable_h = screen_h - 90

        max_cell_w = (usable_w - chrome_w) // city_graph.cols
        max_cell_h = (usable_h - chrome_h) // city_graph.rows
        max_cell = max(28, min(max_cell_w, max_cell_h))  
        self.cell_size = min(cell_size, max_cell)
        cell_size = self.cell_size

        self.grid_width = city_graph.cols * cell_size
        self.grid_height = city_graph.rows * cell_size

        self.screen_width = self.grid_width + chrome_w
        self.screen_height = self.grid_height + chrome_h

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )

        pygame.display.set_caption(
            "CityMind - Urban Intelligence System"
        )

        self.title_font = pygame.font.Font(None, 42)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Grid is pushed below the new top bar.
        self.grid_x = 30
        self.grid_y = self.top_bar_height + 20

        self.particles = ParticleSystem()
        self.floods = FloodAnimation()
        self.notifications = NotificationManager()

        self.time = 0

        # Orbs drift in events block
        orb_x_min = self.grid_width + 80
        orb_x_max = self.grid_width + 60 + self.sidebar_width - 40
        orb_y_min = self.top_bar_height + 60
        orb_y_max = self.top_bar_height + self.grid_height
        self.orbs = [
            FloatingOrb(random.randint(orb_x_min, orb_x_max),
                        random.randint(orb_y_min, orb_y_max),
                        40, (59, 130, 246), 0.02),
            FloatingOrb(random.randint(orb_x_min, orb_x_max),
                        random.randint(orb_y_min, orb_y_max),
                        30, (168, 85, 247), 0.03),
            FloatingOrb(random.randint(orb_x_min, orb_x_max),
                        random.randint(orb_y_min, orb_y_max),
                        50, (34, 197, 94), 0.015),
            FloatingOrb(random.randint(orb_x_min, orb_x_max),
                        random.randint(orb_y_min, orb_y_max),
                        25, (251, 191, 36), 0.025),
        ]

        # top button layout    
        ctrl_btn_y = 120
        ctrl_btn_h = 42
        ctrl_count = 4   
        view_count = 4
        gap = 10
        
        usable = self.screen_width - 60          
        divider_gap = 40
        group_w = (usable - divider_gap) / 2
        ctrl_btn_w = int((group_w - (ctrl_count - 1) * gap) / ctrl_count)
        view_btn_w = int((group_w - (view_count - 1) * gap) / view_count)

        ctrl_x0 = 30
        view_x0 = int(30 + group_w + divider_gap)

        self.buttons = {
            'play':  Button(ctrl_x0 + 0 * (ctrl_btn_w + gap), ctrl_btn_y, ctrl_btn_w, ctrl_btn_h, "Play",  ""),
            'pause': Button(ctrl_x0 + 1 * (ctrl_btn_w + gap), ctrl_btn_y, ctrl_btn_w, ctrl_btn_h, "Pause", ""),
            'step':  Button(ctrl_x0 + 2 * (ctrl_btn_w + gap), ctrl_btn_y, ctrl_btn_w, ctrl_btn_h, "Step",  ""),
            'chaos': Button(ctrl_x0 + 3 * (ctrl_btn_w + gap), ctrl_btn_y, ctrl_btn_w, ctrl_btn_h, "Chaos", ""),
        }

        self.view_buttons = {
            'city':     Button(view_x0 + 0 * (view_btn_w + gap), ctrl_btn_y, view_btn_w, ctrl_btn_h, "City",     ""),
            'roads':    Button(view_x0 + 1 * (view_btn_w + gap), ctrl_btn_y, view_btn_w, ctrl_btn_h, "Roads",    ""),
            'coverage': Button(view_x0 + 2 * (view_btn_w + gap), ctrl_btn_y, view_btn_w, ctrl_btn_h, "Coverage", ""),
            'crime':    Button(view_x0 + 3 * (view_btn_w + gap), ctrl_btn_y, view_btn_w, ctrl_btn_h, "Crime",    ""),
        }

        self._top_divider_x = int(30 + group_w + divider_gap / 2)

        #"Run Again" button
        run_btn_w = 220
        run_btn_h = 56
        run_btn_x = self.grid_x + (self.grid_width - run_btn_w) // 2
        run_btn_y = self.grid_y + self.grid_height // 2 + 20
        self.run_again_button = Button(
            run_btn_x, run_btn_y, run_btn_w, run_btn_h, "Run Again", ""
        )
        self.run_again_button.active = True

    # glass panel

    def draw_glass_panel(self, rect, border_color=(59, 130, 246)):
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        pygame.draw.rect(
            surface,
            (17, 24, 39, 160),  
            (0, 0, rect.width, rect.height),
            border_radius=24
        )

        pygame.draw.rect(
            surface,
            (255, 255, 255, 15),
            (0, 0, rect.width, rect.height),
            width=1,
            border_radius=24
        )

        shadow = pygame.Surface(
            (rect.width + 20, rect.height + 20),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            shadow,
            (0, 0, 0, 80),
            (10, 10, rect.width, rect.height),
            border_radius=28
        )

        self.screen.blit(shadow, (rect.x - 10, rect.y - 10))
        self.screen.blit(surface, (rect.x, rect.y))

        pygame.draw.rect(
            self.screen,
            (*border_color, 120),
            rect,
            width=2,
            border_radius=24
        )

    def draw_grid(self):
       
        for y in range(0, self.screen_height):
            r = int(10 + (y / self.screen_height) * 8)
            g = int(15 + (y / self.screen_height) * 12)
            b = int(25 + (y / self.screen_height) * 20)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # scan effect
        scan_y = (self.time * 2) % self.screen_height
        scan_surf = pygame.Surface((self.screen_width, 2), pygame.SRCALPHA)
        pygame.draw.rect(scan_surf, (59, 130, 246, 40), (0, 0, self.screen_width, 2))
        self.screen.blit(scan_surf, (0, scan_y))
    
        grid_rect = pygame.Rect(self.grid_x, self.grid_y, self.grid_width, self.grid_height)
        pygame.draw.rect(self.screen, (15, 23, 42), grid_rect, border_radius=16)
        
        pulse = (math.sin(self.time / 45) + 1) / 2
        grid_alpha = int(25 + pulse * 15)
        accent_alpha = int(40 + pulse * 30)
        
        # base grid lines
        for r in range(self.graph.rows + 1):
            y = self.grid_y + r * self.cell_size
            pygame.draw.line(self.screen, (71, 85, 105),
                           (self.grid_x, y), (self.grid_x + self.grid_width, y), 1)
        
        for c in range(self.graph.cols + 1):
            x = self.grid_x + c * self.cell_size
            pygame.draw.line(self.screen, (71, 85, 105),
                           (x, self.grid_y), (x, self.grid_y + self.grid_height), 1)
        
    
        for r in range(self.graph.rows + 1):
            for c in range(self.graph.cols + 1):
                x = self.grid_x + c * self.cell_size
                y = self.grid_y + r * self.cell_size
                pygame.draw.circle(self.screen, (59, 130, 246), (x, y), 2)
     
        for i in range(3):
            border_rect = pygame.Rect(self.grid_x - i, self.grid_y - i, self.grid_width + 2*i, self.grid_height + 2*i)
            pygame.draw.rect(self.screen, (59, 130, 246), border_rect, width=1, border_radius=16)

    # road making
    def draw_roads(self, highlight_mode=False):
        for (u, v, data) in self.graph.graph.edges(data=True):
            if not data.get('exists', False):
                continue
            
            r1, c1 = u
            r2, c2 = v
            
            x1 = self.grid_x + c1 * self.cell_size + self.cell_size // 2
            y1 = self.grid_y + r1 * self.cell_size + self.cell_size // 2
            x2 = self.grid_x + c2 * self.cell_size + self.cell_size // 2
            y2 = self.grid_y + r2 * self.cell_size + self.cell_size // 2
            
            if data.get('blocked', False):
                
                pygame.draw.line(self.screen, (0, 0, 0), (x1+3, y1+3), (x2+3, y2+3), 14)
     
                pulse = (math.sin(self.time / 15) + 1) / 2
                blue_val = int(180 + pulse * 75)

                pygame.draw.line(self.screen, (30, 100, blue_val), (x1, y1), (x2, y2), 12)
                red_pulse = int(150 + (1-pulse) * 105)
                pygame.draw.line(self.screen, (red_pulse, 40, 40), (x1, y1), (x2, y2), 4)
                
                stripe_offset = (self.time % 30) / 30
                segments = 10
                for i in range(segments):
                    t1 = (i + stripe_offset) / segments
                    t2 = (i + 0.4 + stripe_offset) / segments
                    if t1 <= 1 and t2 <= 1:
                        sx1 = x1 + (x2 - x1) * t1
                        sy1 = y1 + (y2 - y1) * t1
                        sx2 = x1 + (x2 - x1) * t2
                        sy2 = y1 + (y2 - y1) * t2
                        pygame.draw.line(self.screen, (255, 230, 0), (int(sx1), int(sy1)), (int(sx2), int(sy2)), 3)
                
                mx, my = (x1 + x2) // 2, (y1 + y2) // 2
                size = int(14 + pulse * 5)
                
                pygame.draw.line(self.screen, (30, 30, 30),
                               (mx-size+2, my-size+2), (mx+size+2, my+size+2), 5)
                pygame.draw.line(self.screen, (30, 30, 30),
                               (mx-size+2, my+size+2), (mx+size+2, my-size+2), 5)
                
                # X mark
                pygame.draw.line(self.screen, (255, 255, 255),
                               (mx-size, my-size), (mx+size, my+size), 5)
                pygame.draw.line(self.screen, (255, 255, 255),
                               (mx-size, my+size), (mx+size, my-size), 5)
            else:
                pygame.draw.line(self.screen, (0, 0, 0), (x1+3, y1+3), (x2+3, y2+3), 10)
                
                # base road
                color = (70, 160, 255) if highlight_mode else (90, 105, 125)
                pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 8)
            
                dashes = 6
                dash_length = 0.4
                for i in range(dashes):
                    t1 = (i * 2) / (dashes * 2)
                    t2 = t1 + dash_length / dashes
                    if t2 <= 1:
                        dx1 = x1 + (x2 - x1) * t1
                        dy1 = y1 + (y2 - y1) * t1
                        dx2 = x1 + (x2 - x1) * t2
                        dy2 = y1 + (y2 - y1) * t2
                        pygame.draw.line(self.screen, (240, 240, 240), (dx1, dy1), (dx2, dy2), 2)

    # ambulance path
    def draw_path(self, path):
    
        if not path or len(path) < 2:
            return
        
        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            
            x1 = self.grid_x + c1 * self.cell_size + self.cell_size // 2
            y1 = self.grid_y + r1 * self.cell_size + self.cell_size // 2
            x2 = self.grid_x + c2 * self.cell_size + self.cell_size // 2
            y2 = self.grid_y + r2 * self.cell_size + self.cell_size // 2
    
            progress = i / len(path)
            color = (
                int(34 + (59 - 34) * progress),
                int(197 + (130 - 197) * progress),
                int(94 + (246 - 94) * progress)
            )

            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 10)
  
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 6)
   
            flow_offset = (self.time % 30) / 30
            for j in range(3):
                t = (j / 3 + flow_offset) % 1
                dx = x1 + (x2 - x1) * t
                dy = y1 + (y2 - y1) * t
                pygame.draw.circle(self.screen, (255, 255, 255), (int(dx), int(dy)), 3)
    
    def draw_building(self, row, col, building_type):
        if building_type not in building_colors:
            return
        
        colors = building_colors[building_type]
        
        x = self.grid_x + col * self.cell_size + self.cell_size // 2
        y = self.grid_y + row * self.cell_size + self.cell_size // 2
        
        size = int(self.cell_size * 0.7)
        
        for i in range(4):
            glow_size = size + 25 - i * 5
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            alpha = 40 - i * 8
            pygame.draw.rect(glow_surface, (*colors['glow'], alpha), 
                        (0, 0, glow_size, glow_size), border_radius=glow_size // 4)
            self.screen.blit(glow_surface, (x - glow_size//2, y - glow_size//2))
        
        # 3D effect
        depth = 4
        for i in range(depth):
            offset = depth - i
            shadow_color = tuple(max(0, c - i * 15) for c in colors['primary'][:3])
            shadow_rect = pygame.Rect(x - size//2 + offset, y - size//2 + offset, size, size)
            pygame.draw.rect(self.screen, shadow_color, shadow_rect, border_radius=10)
      
        rect = pygame.Rect(x - size//2, y - size//2, size, size)
        pygame.draw.rect(self.screen, colors['primary'], rect, border_radius=10)
    
        highlight = pygame.Surface((size, size // 3), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (255, 255, 255, 30), (0, 0, size, size // 3))
        self.screen.blit(highlight, (x - size//2, y - size//2))
     
        pygame.draw.rect(self.screen, colors['secondary'], rect, width=3, border_radius=10)
        
        # pulse for hospitals
        if building_type == 'Hospital':
            pulse = (math.sin(self.time / 30) + 1) / 2
            pulse_color = (*colors['secondary'][:3], int(100 * pulse))
            pygame.draw.rect(self.screen, pulse_color, rect, width=5, border_radius=10)
        
        if building_type == 'Hospital':
            pulse = (math.sin(self.time / 15) + 1) / 2  # 0.0 to 1.0
            alpha = int(50 + 205 * pulse) 
            
            cross_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.rect(cross_surf, (255, 255, 255, alpha), (11, 3, 8, 24), border_radius=2)
            pygame.draw.rect(cross_surf, (255, 255, 255, alpha), (3, 11, 24, 8), border_radius=2)
            self.screen.blit(cross_surf, (x - 15, y - 15))
            
        elif building_type == 'Power':
            bolt = [(x + 2, y - 12), (x - 8, y + 2), (x, y + 2), (x - 4, y + 14), (x + 8, y - 2), (x, y - 2)]
            pygame.draw.polygon(self.screen, (250, 204, 21), bolt)
     
            if random.random() > 0.85:
                arc_color = (125, 211, 252) if random.random() > 0.5 else (255, 255, 255)
                for _ in range(random.randint(1, 3)):
                    points = [(x, y)]
                    curr_x, curr_y = x, y
                    for step in range(3):
                        curr_x += random.randint(-12, 12)
                        curr_y += random.randint(-12, 12)
                        points.append((curr_x, curr_y))
                    pygame.draw.lines(self.screen, arc_color, False, points, 2)
          # industry gear icon      
        elif building_type == 'Industrial':
            pygame.draw.circle(self.screen, (226, 232, 240), (x, y), 8, width=3)
            for angle in range(0, 360, 45):
                rad = math.radians(angle + self.time * 2) 
                x1 = x + math.cos(rad) * 7
                y1 = y + math.sin(rad) * 7
                x2 = x + math.cos(rad) * 11
                y2 = y + math.sin(rad) * 11
                pygame.draw.line(self.screen, (226, 232, 240), (x1, y1), (x2, y2), 4)
            # Inner axle hole
            pygame.draw.circle(self.screen, (203, 213, 225), (x, y), 3)
      
            self.particles.emit_smoke(x, y - 10)
            
        elif building_type == 'School':
            # Open book shape
            book_left = [(x - 12, y - 4), (x - 2, y + 2), (x - 2, y + 12), (x - 12, y + 6)]
            book_right = [(x + 12, y - 4), (x + 2, y + 2), (x + 2, y + 12), (x + 12, y + 6)]
            pygame.draw.polygon(self.screen, (255, 255, 255), book_left)
            pygame.draw.polygon(self.screen, (240, 240, 240), book_right)
            
        elif building_type == 'Residential':
            pygame.draw.polygon(self.screen, (255, 255, 255), [(x, y - 12), (x - 10, y - 2), (x + 10, y - 2)])
            pygame.draw.rect(self.screen, (255, 255, 255), (x - 8, y - 2, 16, 14), width=2)
            # window grid
            for wx in range(2):
                for wy in range(2):
                    if random.random() > 0.3: 
                        pygame.draw.rect(self.screen, (253, 224, 71), (x - 5 + wx*6, y + 2 + wy*5, 4, 4))
                        
        elif building_type == 'Depot':
            pygame.draw.rect(self.screen, (255, 255, 255), (x - 12, y - 8, 24, 20), border_radius=2)
            for gy in range(4):
                pygame.draw.line(self.screen, (100, 116, 139), (x - 10, y - 4 + gy*4), (x + 10, y - 4 + gy*4), 2)
            beacon_color = (96, 165, 250) if (self.time // 10) % 2 == 0 else (30, 58, 138)
            pygame.draw.circle(self.screen, beacon_color, (x, y - 12), 3)
    
   # making all buildigs
    def draw_buildings(self):
        for node in self.graph.graph.nodes():
            btype = self.graph.graph.nodes[node]['type']
            if btype:
                self.draw_building(node[0], node[1], btype)
    
    def draw_ambulance(self, x, y, rotation=0):
       
        x += 10
        y += 10
        
        for i in range(3):
            shadow = pygame.Surface((38 - i * 2, 8 - i), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 40 - i * 10))
            self.screen.blit(shadow, (x - 19 + i, y + 14 + i))
        
        body_rect = pygame.Rect(x - 16, y - 12, 32, 24)
        pygame.draw.rect(self.screen, (255, 255, 255), body_rect, border_radius=4)
        
        window_rect = pygame.Rect(x - 14, y - 9, 14, 8)
        pygame.draw.rect(self.screen, (90, 140, 190), window_rect, border_radius=2)
        
        stripe_rect = pygame.Rect(x - 16, y - 2, 32, 6)
        pygame.draw.rect(self.screen, (239, 68, 68), stripe_rect)
        
        pygame.draw.circle(self.screen, (30, 30, 30), (x - 10, y + 12), 3)
        pygame.draw.circle(self.screen, (30, 30, 30), (x + 10, y + 12), 3)
        
        phase = (self.time // 8) % 2
        light_colors = [(255, 0, 0), (0, 0, 255)]
        
        pygame.draw.circle(self.screen, light_colors[phase], (x - 12, y - 10), 4)
        if phase == 0: # Glow effect
            s = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 0, 0, 100), (6, 6), 6)
            self.screen.blit(s, (x - 18, y - 16))
            
    
        pygame.draw.circle(self.screen, light_colors[1 - phase], (x + 12, y - 10), 4)
        if phase == 1: # Glow effect
            s = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 0, 255, 100), (6, 6), 6)
            self.screen.blit(s, (x + 6, y - 16))

    # cime heatmap with red ornage and yellow color
    def draw_crime_heatmap(self):
       
        overlay = pygame.Surface((self.grid_width, self.grid_height), pygame.SRCALPHA)
        
        for node in self.graph.graph.nodes():
            if self.graph.graph.nodes[node]['type'] is None:
                continue
            
            risk = self.graph.graph.nodes[node]['risk_index']
            r, c = node
           # high risk
            if risk > 0.6:
                base_color = (220, 38, 38)
                alpha = 200
                label = "HIGH"
                label_color = (255, 255, 255)
            elif risk > 0.3:
            # med risk
                base_color = (245, 158, 11)
                alpha = 160
                label = "MED"
                label_color = (255, 255, 255)
            else:
            # low risk
                base_color = (190, 220, 70)
                alpha = 120
                label = "LOW"
                label_color = (40, 60, 20)
            
            pulse = (math.sin(self.time / 40 + risk * 10) + 1) / 2
            final_alpha = min(255, alpha + int(pulse * 40))
            
            # filing cmplete cell
            rect = pygame.Rect(c * self.cell_size, r * self.cell_size, 
                             self.cell_size, self.cell_size)
            pygame.draw.rect(overlay, (*base_color, final_alpha), rect)

            border_alpha = min(255, final_alpha + 30)
            pygame.draw.rect(overlay, (*base_color, border_alpha), rect, 2)
   
            risk_text = self.small_font.render(label, True, label_color)
            text_x = c * self.cell_size + self.cell_size // 2 - risk_text.get_width() // 2
            text_y = r * self.cell_size + self.cell_size // 2 - risk_text.get_height() // 2 - 8
            overlay.blit(risk_text, (text_x, text_y))
            
            pct_text = self.small_font.render(f"{int(risk * 100)}%", True, label_color)
            pct_x = c * self.cell_size + self.cell_size // 2 - pct_text.get_width() // 2
            pct_y = text_y + 18
            overlay.blit(pct_text, (pct_x, pct_y))
            
            # Police shield icon if police are deployed here
            if hasattr(self, '_police_locations') and node in self._police_locations:
                count = self._police_locations[node]
                shield = self.small_font.render(f"🛡{count}", True, (100, 200, 255))
                overlay.blit(shield, (c * self.cell_size + 4, r * self.cell_size + 4))
        
        self.screen.blit(overlay, (self.grid_x, self.grid_y))
    
    def draw_coverage(self, ambulances):

        overlay = pygame.Surface((self.grid_width, self.grid_height), pygame.SRCALPHA)
        
        for amb in ambulances:
            x = amb['col'] * self.cell_size + self.cell_size // 2
            y = amb['row'] * self.cell_size + self.cell_size // 2
            
            # Multi-ring coverage
            for ring in range(3):
                radius = int(self.cell_size * (3.5 - ring * 0.8))
                pulse = (math.sin(self.time / 30 + ring * 2) + 1) / 2
                alpha = int(60 - ring * 15 + pulse * 20)
                
                pygame.draw.circle(overlay, (59, 130, 246, alpha), (x, y), radius)
                pygame.draw.circle(overlay, (147, 197, 253, alpha + 40), (x, y), radius, 2)
        
        self.screen.blit(overlay, (self.grid_x, self.grid_y))
    
    # buttons for handling
    
    def handle_button_events(self, event, finished=False):
        
        if finished and self.run_again_button.handle_event(event):
            return ('control', 'run_again')
        for key, button in self.buttons.items():
            if button.handle_event(event):
                return ('control', key)
        
        for key, button in self.view_buttons.items():
            if button.handle_event(event):
                return ('view', key)
        
        return None
    # matching flood with grid
    def update_floods(self):
        for (u, v, data) in self.graph.graph.edges(data=True):
            if data.get('blocked', False) and (u, v) not in self.floods.floods:
                r1, c1 = u
                r2, c2 = v
                x1 = c1 * self.cell_size + self.cell_size // 2
                y1 = r1 * self.cell_size + self.cell_size // 2
                x2 = c2 * self.cell_size + self.cell_size // 2
                y2 = r2 * self.cell_size + self.cell_size // 2
                self.floods.add_flood((u, v), x1, y1, x2, y2)

        to_remove = []
        for edge in self.floods.floods:
            if not self.graph.graph.edges[edge].get('blocked', False):
                to_remove.append(edge)
        
        for edge in to_remove:
            self.floods.remove_flood(edge)
    # main render function
    def render(self, ambulances, event_log, stats, view_mode, paused, emergencies=None, finished=False):
      
        self.time += 1
     
        self.particles.update()
        self.floods.update()
        self.notifications.update()
        self.update_floods()
      
        self.draw_grid()
      
        if view_mode == 'crime':
            self.draw_crime_heatmap()
        elif view_mode == 'coverage':
            self.draw_coverage(ambulances)
        
        if view_mode == 'roads':
            self.draw_roads(highlight_mode=True)
        else:
            self.draw_roads()
       
        flood_surface = pygame.Surface((self.grid_width, self.grid_height), pygame.SRCALPHA)
        self.floods.draw(flood_surface)
        self.screen.blit(flood_surface, (self.grid_x, self.grid_y))
       
        for amb in ambulances:
            if amb.get('path') and view_mode != 'crime':
                self.draw_path(amb['path'])
        
        self.draw_buildings()
        
        # emergency markers
        if emergencies:
            self.draw_emergencies(emergencies)
        
        for amb in ambulances:
            x = self.grid_x + amb['x']
            y = self.grid_y + amb['y']
            self.draw_ambulance(x, y)
            
            if self.time % 20 == 0:
                self.particles.emit_siren_pulse(x, y)
        
        # Particles
        particle_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.particles.draw(particle_surface)
        self.screen.blit(particle_surface, (0, 0))
        
        self.draw_top_bar(stats, paused, view_mode)
        self.draw_events_panel(event_log)

        if finished:
            self.draw_completion_overlay(stats)
 
        self.notifications.draw(self.screen, self.small_font, 
                              self.screen_width - 300, 20)
        
        pygame.display.flip()

    # run again screen with dim grid

    def draw_completion_overlay(self, stats):
      
        dim = pygame.Surface((self.grid_width, self.grid_height), pygame.SRCALPHA)
        dim.fill((6, 10, 20, 200))
        self.screen.blit(dim, (self.grid_x, self.grid_y))

        card_w = 460
        card_h = 320
        card_x = self.grid_x + (self.grid_width - card_w) // 2
        card_y = self.grid_y + (self.grid_height - card_h) // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        self.draw_glass_panel(card_rect, (34, 197, 94))

        title = self.title_font.render("Simulation Complete", True, (240, 248, 255))
        self.screen.blit(title, (card_x + (card_w - title.get_width()) // 2, card_y + 26))

        sub = self.small_font.render(
            "20-step run finished -- review the stats below", True, (150, 200, 230)
        )
        self.screen.blit(sub, (card_x + (card_w - sub.get_width()) // 2, card_y + 70))

        rows = [
            ("Steps completed",  f"{stats.get('step', 0)} / 20"),
            ("Roads built",      f"{stats.get('roads', 0)}"),
            ("Roads flooded",    f"{stats.get('blocked', 0)}"),
            ("Civilians rescued",f"{stats.get('rescued', 0)}"),
            ("Police deployed",  f"{stats.get('police', 0)} / 10"),
        ]
        ry = card_y + 102
        for label, value in rows:
            lbl = self.small_font.render(label, True, (170, 195, 230))
            val = self.small_font.render(value, True, (255, 255, 255))
            self.screen.blit(lbl, (card_x + 40, ry))
            self.screen.blit(val, (card_x + card_w - 40 - val.get_width(), ry))
            
            sep = pygame.Surface((card_w - 80, 1), pygame.SRCALPHA)
            sep.fill((255, 255, 255, 18))
            self.screen.blit(sep, (card_x + 40, ry + 22))
            ry += 30

        new_x = card_x + (card_w - self.run_again_button.rect.width) // 2
        new_y = card_y + card_h - self.run_again_button.rect.height - 24
        self.run_again_button.rect.x = new_x
        self.run_again_button.rect.y = new_y
        self.run_again_button.draw(self.screen, self.small_font)
    
    def draw_emergencies(self, emergencies):
       
        for location, step_created in emergencies:
            row, col = location
            cx = self.grid_x + col * self.cell_size + self.cell_size // 2
            cy = self.grid_y + row * self.cell_size + self.cell_size // 2
            
            # Pulsing animation
            pulse = (math.sin(self.time / 8) + 1) / 2
         
            ring_surface = pygame.Surface((self.cell_size * 3, self.cell_size * 3), pygame.SRCALPHA)
            ring_cx = self.cell_size * 3 // 2
            ring_cy = self.cell_size * 3 // 2
            
            for ring in range(3):
                radius = int(12 + ring * 10 + pulse * 8)
                alpha = max(0, 180 - ring * 60 - int(pulse * 40))
                pygame.draw.circle(ring_surface, (255, 50, 50, alpha), (ring_cx, ring_cy), radius, 2)
            
            self.screen.blit(ring_surface, (cx - ring_cx, cy - ring_cy))
           
            glow_size = int(16 + pulse * 6)
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 30, 30, 100), (glow_size, glow_size), glow_size)
            self.screen.blit(glow_surface, (cx - glow_size, cy - glow_size))
            
            pygame.draw.circle(self.screen, (255, 60, 60), (cx, cy), int(8 + pulse * 3))
            pygame.draw.circle(self.screen, (255, 200, 200), (cx, cy), 4)
          
            sos_text = self.small_font.render("SOS", True, (255, 80, 80))
            self.screen.blit(sos_text, (cx - sos_text.get_width() // 2, cy - 28))
    
    
    # top bar

    def draw_top_bar(self, stats, paused, view_mode):
      
        bar_rect = pygame.Rect(20, 10, self.screen_width - 40, self.top_bar_height - 5)
        self.draw_glass_panel(bar_rect, (59, 130, 246))

        title = self.title_font.render("CityMind", True, (240, 248, 255))
        self.screen.blit(title, (40, 22))
        sub = self.small_font.render(
            "Urban Intelligence Command Center", True, (130, 170, 220)
        )
        self.screen.blit(sub, (44, 60))

        # Animated live status dot beside subtitle
        pulse = 5 + math.sin(self.time / 8) * 2
        pygame.draw.circle(
            self.screen,
            (220, 60, 60) if paused else (34, 197, 94),
            (44 + sub.get_width() + 14, 68),
            int(pulse),
        )
        status_label = self.small_font.render(
            "PAUSED" if paused else "LIVE", True,
            (220, 60, 60) if paused else (34, 197, 94),
        )
        self.screen.blit(status_label, (44 + sub.get_width() + 26, 62))

        stat_items = [
            ("STEP",        f"{stats['step']:>2} / 20",
                stats['step'] / 20.0,                 (59, 130, 246)),
            ("ROADS",       f"{stats['roads']}",
                min(1, stats['roads'] / 160.0),        (34, 197, 94)),
            ("FLOODED",     f"{stats['blocked']}",
                min(1, stats['blocked'] / 10.0),       (239, 68, 68)),
            ("EMERGENCIES", f"{stats.get('emergencies',0)} / {stats.get('rescued',0)}",
                min(1, stats.get('rescued',0) /
                    max(1, stats.get('rescued',0) + stats.get('emergencies',1))),
                (255, 100, 100)),
            ("POLICE",      f"{stats.get('police',0)} / 10",
                min(1, stats.get('police',0) / 10.0),  (100, 180, 255)),
        ]

        cards_x0 = 320
        cards_w = self.screen_width - 40 - cards_x0
        n = len(stat_items)
        gap = 8
        card_w = int((cards_w - (n - 1) * gap) / n)
        card_h = 78
        card_y = 22

        for i, (label, value, progress, color) in enumerate(stat_items):
            x = cards_x0 + i * (card_w + gap)
            rect = pygame.Rect(x, card_y, card_w, card_h)

            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card, (255, 255, 255, 12), (0, 0, card_w, card_h), border_radius=12)
            pygame.draw.rect(card, (*color, 90), (0, 0, card_w, card_h), width=1, border_radius=12)
            # Top accent strip
            pygame.draw.rect(card, (*color, 200), (0, 0, card_w, 3), border_radius=2)
            self.screen.blit(card, (x, card_y))

            lbl = self.small_font.render(label, True, (170, 195, 230))
            self.screen.blit(lbl, (x + 12, card_y + 8))
     
            val_font = self.font
            val = val_font.render(value, True, (255, 255, 255))
            self.screen.blit(val, (x + 12, card_y + 26))
            
            bar_y = card_y + card_h - 14
            bar_w = card_w - 24
            pygame.draw.rect(self.screen, (40, 50, 70),
                             (x + 12, bar_y, bar_w, 5), border_radius=4)
            fill = max(0, min(bar_w, int(bar_w * progress)))
            if fill > 0:
                pygame.draw.rect(self.screen, color,
                                 (x + 12, bar_y, fill, 5), border_radius=4)

        dx = self._top_divider_x
        for i in range(4):
            alpha = 80 - i * 18
            line = pygame.Surface((1, 30), pygame.SRCALPHA)
            line.fill((130, 170, 220, max(alpha, 0)))
            self.screen.blit(line, (dx + i, 126))
            self.screen.blit(line, (dx - i, 126))

        ctrl_lbl = self.small_font.render("CONTROLS", True, (130, 170, 220))
        self.screen.blit(ctrl_lbl, (30, 105))
        view_lbl = self.small_font.render("VIEW MODE", True, (130, 170, 220))
        self.screen.blit(view_lbl, (
            self._top_divider_x + 28, 105
        ))

        # buttons 
        self.buttons['play'].active = not paused
        self.buttons['pause'].active = paused
        self.buttons['chaos'].active = bool(stats.get('chaos', False))
        for key in self.view_buttons:
            self.view_buttons[key].active = (key == view_mode)
        for b in self.buttons.values():
            b.draw(self.screen, self.small_font)
        for b in self.view_buttons.values():
            b.draw(self.screen, self.small_font)

    # events panel

    def draw_events_panel(self, event_log):
        
        sidebar_x = self.grid_width + 60

        for orb in self.orbs:
            orb.update(self.time)
            orb.draw(self.screen)

        events_rect = pygame.Rect(
            sidebar_x,
            self.grid_y,
            self.sidebar_width,
            self.grid_height,
        )
        self.draw_glass_panel(events_rect, (168, 85, 247))

        live_title = self.title_font.render("Live Events", True, (240, 248, 255))
        self.screen.blit(live_title, (sidebar_x + 24, self.grid_y + 18))

        status_dot = 8 + math.sin(self.time / 8) * 2
        pygame.draw.circle(
            self.screen,
            (34, 197, 94),
            (sidebar_x + self.sidebar_width - 50, self.grid_y + 36),
            int(status_dot),
        )
        ticker = self.small_font.render(
            f"{len(event_log)} events logged", True, (130, 170, 220)
        )
        self.screen.blit(ticker, (sidebar_x + 26, self.grid_y + 56))

        y = self.grid_y + 90
        max_y = self.grid_y + self.grid_height - 60
        events_to_show = list(reversed(event_log[-40:]))

        for event in events_to_show:
            if y + 56 > max_y:
                break

            if "FLOODED" in event:
                accent = (239, 68, 68); icon = "!"
            elif "cleared" in event:
                accent = (34, 197, 94); icon = "OK"
            elif "Trapped" in event or "SOS" in event:
                accent = (255, 80, 80); icon = "SOS"
            elif "rescued" in event.lower():
                accent = (50, 205, 50); icon = "OK"
            elif "dispatched" in event.lower() or "ambulance" in event.lower():
                accent = (59, 130, 246); icon = "AMB"
            elif "police" in event.lower() or "officer" in event.lower():
                accent = (100, 180, 255); icon = "POL"
            elif "===" in event:
                accent = (180, 190, 210); icon = ">>"
            else:
                accent = (180, 190, 210); icon = "*"

            card_rect = pygame.Rect(
                sidebar_x + 18, y, self.sidebar_width - 36, 48
            )
            card = pygame.Surface(
                (card_rect.width, card_rect.height), pygame.SRCALPHA
            )
            pygame.draw.rect(card, (255, 255, 255, 10),
                             (0, 0, card_rect.width, card_rect.height),
                             border_radius=14)
            pygame.draw.rect(card, (*accent, 80),
                             (0, 0, card_rect.width, card_rect.height),
                             width=1, border_radius=14)
            # left accent strip
            pygame.draw.rect(card, (*accent, 200),
                             (0, 8, 3, card_rect.height - 16),
                             border_radius=2)
            self.screen.blit(card, (card_rect.x, card_rect.y))

            pygame.draw.circle(
                self.screen, accent,
                (card_rect.x + 22, card_rect.y + 24), 5
            )

            txt_str = event
            if len(txt_str) > 50:
                txt_str = txt_str[:47] + "..."
            txt = self.small_font.render(
                f"[{icon}] {txt_str}", True, (235, 240, 250)
            )
            self.screen.blit(txt, (card_rect.x + 36, card_rect.y + 16))

            y += 56

# building Colors

building_colors = {
    'Hospital': {
        'primary': (220, 38, 38),
        'secondary': (185, 28, 28),
        'icon': 'HOSP',
        'glow': (255, 100, 100)
    },

    'Depot': {
        'primary': (37, 99, 235),
        'secondary': (29, 78, 216),
        'icon': 'DEP',
        'glow': (147, 197, 253)
    },

    'Residential': {
        'primary': (34, 197, 94),
        'secondary': (22, 163, 74),
        'icon': 'RES',
        'glow': (134, 239, 172)
    },

    'Industrial': {
        'primary': (100, 116, 139),
        'secondary': (71, 85, 105),
        'icon': 'IND',
        'glow': (148, 163, 184)
    },

    'School': {
        'primary': (251, 146, 60),
        'secondary': (249, 115, 22),
        'icon': 'SCH',
        'glow': (253, 186, 116)
    },

    'Power': {
        'primary': (168, 85, 247),
        'secondary': (147, 51, 234),
        'icon': 'PWR',
        'glow': (216, 180, 254)
    }
}