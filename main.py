import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()
pygame.font.init()

# Setup Screen for Mobile / Desktop
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w if info.current_w > 0 else 720
SCREEN_HEIGHT = info.current_h if info.current_h > 0 else 1280
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cosmic Abyss: 60 Seconds")

clock = pygame.time.Clock()
font_small = pygame.font.SysFont("sans-serif", int(SCREEN_HEIGHT * 0.022))
font_large = pygame.font.SysFont("sans-serif", int(SCREEN_HEIGHT * 0.035))

# World Size for Survivor Exploration
WORLD_WIDTH = 2500
WORLD_HEIGHT = 2500

# --- GAME CLASSES ---

class GlitchOrb:
    def __init__(self, x=None, y=None):
        self.x = x if x is not None else random.uniform(100, WORLD_WIDTH - 100)
        self.y = y if y is not None else random.uniform(100, WORLD_HEIGHT - 100)
        
        self.is_gold = random.random() < 0.12
        if self.is_gold:
            self.base_radius = random.uniform(22, 28)
            self.color = (255, 215, 0)
            self.value = 45
        else:
            self.base_radius = random.uniform(12, 20)
            self.color = (random.randint(80, 180), random.randint(100, 220), random.randint(130, 240))
            self.value = random.randint(5, 15)

        self.radius = self.base_radius
        self.max_radius = self.base_radius * 1.8
        self.growth_rate = random.uniform(4.0, 8.0)
        self.sides = random.randint(3, 8)

    def update(self, dt):
        if self.radius < self.max_radius:
            self.radius += dt * self.growth_rate

    def draw(self, surface, cam_x, cam_y, phase_time):
        screen_x = self.x - cam_x
        screen_y = self.y - cam_y
        if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
            pts = []
            for s in range(self.sides):
                angle = (s * 2 * math.pi / self.sides) + phase_time * 0.3
                px = screen_x + math.cos(angle) * self.radius
                py = screen_y + math.sin(angle) * self.radius
                pts.append((px, py))
            if len(pts) > 2:
                pygame.draw.polygon(surface, self.color, pts, 3)

class TrailDroplet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 2.5
        self.radius = 14

    def update(self, dt):
        self.timer -= dt

    def draw(self, surface, cam_x, cam_y):
        sx = self.x - cam_x
        sy = self.y - cam_y
        if -50 < sx < SCREEN_WIDTH + 50 and -50 < sy < SCREEN_HEIGHT + 50:
            alpha_radius = int(self.radius * (self.timer / 2.5))
            if alpha_radius > 2:
                pygame.draw.circle(surface, (50, 200, 80), (int(sx), int(sy)), alpha_radius)

class EnemyProjectile:
    def __init__(self, start_pos, target_pos):
        self.x, self.y = start_pos[0], start_pos[1]
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        speed = SCREEN_HEIGHT * 0.45
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed
        self.radius = 6
        self.finished = False

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if not (0 <= self.x <= WORLD_WIDTH and 0 <= self.y <= WORLD_HEIGHT):
            self.finished = True

    def draw(self, surface, cam_x, cam_y):
        sx = self.x - cam_x
        sy = self.y - cam_y
        if -50 < sx < SCREEN_WIDTH + 50 and -50 < sy < SCREEN_HEIGHT + 50:
            pygame.draw.circle(surface, (255, 80, 80), (int(sx), int(sy)), self.radius)

class BaseEnemy:
    def __init__(self, player_x, player_y):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'left':
            self.x = player_x - SCREEN_WIDTH/2 - 100
            self.y = random.uniform(player_y - SCREEN_HEIGHT, player_y + SCREEN_HEIGHT)
        elif side == 'right':
            self.x = player_x + SCREEN_WIDTH/2 + 100
            self.y = random.uniform(player_y - SCREEN_HEIGHT, player_y + SCREEN_HEIGHT)
        elif side == 'top':
            self.x = random.uniform(player_x - SCREEN_WIDTH, player_x + SCREEN_WIDTH)
            self.y = player_y - SCREEN_HEIGHT/2 - 100
        else:
            self.x = random.uniform(player_x - SCREEN_WIDTH, player_x + SCREEN_WIDTH)
            self.y = player_y + SCREEN_HEIGHT/2 + 100

        self.x = max(50, min(WORLD_WIDTH - 50, self.x))
        self.y = max(50, min(WORLD_HEIGHT - 50, self.y))

class JudgmentEye(BaseEnemy):
    def __init__(self, player_x, player_y, difficulty_mult):
        super().__init__(player_x, player_y)
        self.base_speed = random.uniform(1.3, 2.2)
        self.size = SCREEN_HEIGHT * 0.065
        self.hp = max(1, int(1 * difficulty_mult))
        self.pupil_offset = [0, 0]

    def update(self, target_x, target_y, difficulty_mult):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        speed = self.base_speed * difficulty_mult
        self.x += (dx / dist) * speed
        self.y += (dy / dist) * speed
        self.pupil_offset = [(dx / dist) * (self.size * 0.2), (dy / dist) * (self.size * 0.2)]

    def draw(self, surface, cam_x, cam_y):
        screen_x = self.x - cam_x
        screen_y = self.y - cam_y
        if -100 < screen_x < SCREEN_WIDTH + 100 and -100 < screen_y < SCREEN_HEIGHT + 100:
            rect = pygame.Rect(screen_x - self.size/2, screen_y - self.size*0.3, self.size, self.size*0.6)
            pygame.draw.ellipse(surface, (230, 230, 240), rect)
            px = screen_x + self.pupil_offset[0]
            py = screen_y + self.pupil_offset[1]
            pupil_rect = pygame.Rect(px - self.size*0.18, py - self.size*0.18, self.size*0.36, self.size*0.36)
            pygame.draw.ellipse(surface, (200, 30, 30), pupil_rect)
            pygame.draw.rect(surface, (0, 0, 0), (px - 2, py - self.size*0.12, 4, self.size*0.24))

class VoidSeeker(BaseEnemy):
    def __init__(self, player_x, player_y, difficulty_mult):
        super().__init__(player_x, player_y)
        self.base_speed = random.uniform(2.8, 3.8)
        self.size = SCREEN_HEIGHT * 0.035
        self.hp = max(1, int(1 * difficulty_mult))

    def update(self, target_x, target_y, difficulty_mult):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        speed = self.base_speed * difficulty_mult
        self.x += (dx / dist) * speed
        self.y += (dy / dist) * speed

    def draw(self, surface, cam_x, cam_y):
        screen_x = self.x - cam_x
        screen_y = self.y - cam_y
        if -100 < screen_x < SCREEN_WIDTH + 100 and -100 < screen_y < SCREEN_HEIGHT + 100:
            pygame.draw.circle(surface, (180, 50, 220), (int(screen_x), int(screen_y)), int(self.size))
            pygame.draw.circle(surface, (255, 200, 255), (int(screen_x), int(screen_y)), int(self.size * 0.4))

class GorgonCore(BaseEnemy):
    def __init__(self, player_x, player_y, difficulty_mult):
        super().__init__(player_x, player_y)
        self.base_speed = random.uniform(0.8, 1.2)
        self.size = SCREEN_HEIGHT * 0.09
        self.hp = max(2, int(3 * difficulty_mult))

    def update(self, target_x, target_y, difficulty_mult):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        speed = self.base_speed * difficulty_mult
        self.x += (dx / dist) * speed
        self.y += (dy / dist) * speed

    def draw(self, surface, cam_x, cam_y):
        screen_x = self.x - cam_x
        screen_y = self.y - cam_y
        if -100 < screen_x < SCREEN_WIDTH + 100 and -100 < screen_y < SCREEN_HEIGHT + 100:
            pygame.draw.circle(surface, (220, 120, 30), (int(screen_x), int(screen_y)), int(self.size))
            pygame.draw.circle(surface, (50, 0, 0), (int(screen_x), int(screen_y)), int(self.size * 0.6))
            pygame.draw.circle(surface, (255, 50, 50), (int(screen_x), int(screen_y)), int(self.size * 0.2))

class ShooterEye(BaseEnemy):
    def __init__(self, player_x, player_y, difficulty_mult):
        super().__init__(player_x, player_y)
        self.base_speed = random.uniform(1.0, 1.5)
        self.size = SCREEN_HEIGHT * 0.055
        self.hp = max(1, int(1 * difficulty_mult))
        self.shoot_cooldown = random.uniform(1.5, 3.0)

    def update(self, target_x, target_y, difficulty_mult, projectiles_list):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        speed = self.base_speed * difficulty_mult

        if dist > 350:
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
        elif dist < 220:
            self.x -= (dx / dist) * speed
            self.y -= (dy / dist) * speed

        self.shoot_cooldown -= 1.0 * (1.0 / 60.0)
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = random.uniform(1.8, 3.5) / difficulty_mult
            projectiles_list.append(EnemyProjectile([self.x, self.y], [target_x, target_y]))

    def draw(self, surface, cam_x, cam_y):
        screen_x = self.x - cam_x
        screen_y = self.y - cam_y
        if -100 < screen_x < SCREEN_WIDTH + 100 and -100 < screen_y < SCREEN_HEIGHT + 100:
            rect = pygame.Rect(screen_x - self.size/2, screen_y - self.size*0.3, self.size, self.size*0.6)
            pygame.draw.ellipse(surface, (250, 150, 50), rect)
            pygame.draw.circle(surface, (100, 0, 150), (int(screen_x), int(screen_y)), int(self.size * 0.25))

class TentacleShot:
    def __init__(self, start_pos, target_pos, max_reach):
        self.start = list(start_pos)
        self.current_tip = list(start_pos)
        self.max_reach = max_reach
        self.progress = 0.0
        self.speed = 4.0
        self.finished = False

        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        self.dir = [dx / dist, dy / dist]

    def update(self, dt):
        self.progress += dt * self.speed
        if self.progress >= 1.0:
            self.finished = True
            return

        reach_pct = math.sin(self.progress * math.pi)
        reach_dist = self.max_reach * reach_pct
        self.current_tip[0] = self.start[0] + self.dir[0] * reach_dist
        self.current_tip[1] = self.start[1] + self.dir[1] * reach_dist

    def draw(self, surface, cam_x, cam_y, phase_time):
        start_sx = self.start[0] - cam_x
        start_sy = self.start[1] - cam_y
        tip_sx = self.current_tip[0] - cam_x
        tip_sy = self.current_tip[1] - cam_y

        t_points = [(start_sx, start_sy)]
        segments = 5
        for seg in range(1, segments + 1):
            pct = seg / segments
            sx = start_sx + (tip_sx - start_sx) * pct
            sy = start_sy + (tip_sy - start_sy) * pct
            wigg = math.sin(phase_time * 5 + seg) * (8 * (1 - pct))
            t_points.append((sx + wigg, sy + wigg))
        if len(t_points) > 1:
            pygame.draw.lines(surface, (50, 230, 130), False, t_points, 5)

class AcidSpitProjectile:
    def __init__(self, start_pos, target_pos):
        self.x, self.y = start_pos[0], start_pos[1]
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = max(1, math.sqrt(dx * dx + dy * dy))
        speed = SCREEN_HEIGHT * 0.6
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed
        self.radius = 8
        self.finished = False

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if not (0 <= self.x <= WORLD_WIDTH and 0 <= self.y <= WORLD_HEIGHT):
            self.finished = True

    def draw(self, surface, cam_x, cam_y):
        sx = self.x - cam_x
        sy = self.y - cam_y
        pygame.draw.circle(surface, (80, 240, 50), (int(sx), int(sy)), self.radius)

# --- MAIN GAME STATE ---

class Game:
    def __init__(self):
        self.dna_bank = 0
        self.control_mode = "TOUCH"  # Options: "TOUCH" or "JOYSTICK"

        self.skills = {
            "lash": {"name": "Tentacle Lash", "lvl": 1, "base_cost": 40, "desc": "Shoots fast tentacles"},
            "armor": {"name": "Membrane Armor", "lvl": 1, "base_cost": 30, "desc": "Increases max HP"},
            "acid": {"name": "Acid Spit", "lvl": 0, "base_cost": 60, "desc": "Auto-fires venom at eyes"},
            "damage": {"name": "Neural Spikes", "lvl": 0, "base_cost": 45, "desc": "Increases attack damage"},
            "trail": {"name": "Venom Trail", "lvl": 0, "base_cost": 55, "desc": "Leaves damaging toxic slime trail"},
            "magnet": {"name": "DNA Magnet", "lvl": 0, "base_cost": 50, "desc": "Attracts nearby shapes"},
            "reach": {"name": "Strike Reach", "lvl": 1, "base_cost": 35, "desc": "Extends tentacle range"},
            "shatter": {"name": "Shatter Burst", "lvl": 0, "base_cost": 70, "desc": "Bonus DNA on kills"},
            "time_boost": {"name": "Chronos Field", "lvl": 0, "base_cost": 50, "desc": "Slows down timer drain"},
            "shape_swarm": {"name": "Prism Influx", "lvl": 0, "base_cost": 45, "desc": "Increases map shape spawn"}
        }

        self.state = "HOME"
        self.round_won = False
        self.bg_scroll_offset = 0
        self.btn_rects = {}
        self.joystick_center = None
        self.joystick_current = None
        self.reset_run()

    def reset_run(self):
        self.player_pos = [WORLD_WIDTH / 2, WORLD_HEIGHT / 2]
        self.target_pos = list(self.player_pos)
        self.blob_radius = SCREEN_HEIGHT * 0.04

        self.max_health = 2 + self.skills["armor"]["lvl"]
        self.health = self.max_health
        self.max_active_tentacles = self.skills["lash"]["lvl"]
        self.tentacle_reach = SCREEN_HEIGHT * (0.16 + self.skills["reach"]["lvl"] * 0.04)
        self.magnet_range = self.skills["magnet"]["lvl"] * (SCREEN_HEIGHT * 0.08)

        self.run_dna_collected = 0
        self.phase_time = 0
        self.time_remaining = 60.0
        
        self.tentacle_cooldown = 0
        self.acid_cooldown = 0
        self.trail_spawn_timer = 0
        self.joystick_center = None
        self.joystick_current = None

        orb_count = 25 + (self.skills["shape_swarm"]["lvl"] * 15)
        self.orbs = [GlitchOrb() for _ in range(orb_count)]
        self.enemies = []
        self.trail_droplets = []
        self.enemy_projectiles = []
        self.active_shots = []
        self.active_acid = []
        self.enemy_spawn_timer = 0

    def start_new_game(self):
        self.dna_bank = 0
        for k in self.skills:
            self.skills[k]["lvl"] = 1 if k in ["lash", "armor", "reach"] else 0
        self.reset_run()
        self.state = "PLAYING"

    def continue_game(self):
        self.reset_run()
        self.state = "PLAYING"

    def buy_skill(self, key):
        sk = self.skills[key]
        cost = (sk["lvl"] + 1) * sk["base_cost"]
        if self.dna_bank >= cost:
            self.dna_bank -= cost
            sk["lvl"] += 1
            self.max_health = 2 + self.skills["armor"]["lvl"]
            self.max_active_tentacles = self.skills["lash"]["lvl"]
            self.tentacle_reach = SCREEN_HEIGHT * (0.16 + self.skills["reach"]["lvl"] * 0.04)
            self.magnet_range = self.skills["magnet"]["lvl"] * (SCREEN_HEIGHT * 0.08)

    def update(self, dt):
        if self.state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1

        if move_x != 0 or move_y != 0:
            mag = math.sqrt(move_x**2 + move_y**2)
            move_speed = SCREEN_HEIGHT * 0.007
            self.player_pos[0] += (move_x / mag) * move_speed * (dt * 60)
            self.player_pos[1] += (move_y / mag) * move_speed * (dt * 60)
            self.target_pos = list(self.player_pos)
        elif self.control_mode == "JOYSTICK" and self.joystick_center and self.joystick_current:
            jdx = self.joystick_current[0] - self.joystick_center[0]
            jdy = self.joystick_current[1] - self.joystick_center[1]
            jdist = math.sqrt(jdx**2 + jdy**2)
            if jdist > 5:
                max_jdist = 60.0
                pull = min(jdist, max_jdist) / max_jdist
                move_speed = SCREEN_HEIGHT * 0.007 * pull
                self.player_pos[0] += (jdx / jdist) * move_speed * (dt * 60)
                self.player_pos[1] += (jdy / jdist) * move_speed * (dt * 60)
                self.target_pos = list(self.player_pos)
        else:
            dx = self.target_pos[0] - self.player_pos[0]
            dy = self.target_pos[1] - self.player_pos[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 4:
                speed = min(dist * 0.1, SCREEN_HEIGHT * 0.014)
                self.player_pos[0] += (dx / dist) * speed
                self.player_pos[1] += (dy / dist) * speed

        # --- MAP BORDER TELEPORTERS ---
        if self.player_pos[0] <= 10:
            self.player_pos[0] = WORLD_WIDTH - 20
        elif self.player_pos[0] >= WORLD_WIDTH - 10:
            self.player_pos[0] = 20

        if self.player_pos[1] <= 10:
            self.player_pos[1] = WORLD_HEIGHT - 20
        elif self.player_pos[1] >= WORLD_HEIGHT - 10:
            self.player_pos[1] = 20
        # -----------------------------

        time_elapsed = 60.0 - self.time_remaining
        difficulty_mult = 1.0 + (time_elapsed / 60.0) * 1.2

        time_drain_multiplier = max(0.4, 1.0 - (self.skills["time_boost"]["lvl"] * 0.12))
        self.time_remaining -= dt * time_drain_multiplier
        
        if self.time_remaining <= 0:
            self.time_remaining = 0.0
            self.dna_bank += 150
            self.round_won = True
            self.state = "SKILL_TREE"
            return

        self.phase_time += dt * 2.5
        self.bg_scroll_offset = (self.bg_scroll_offset + dt * 25) % 80
        px, py = self.player_pos

        if self.skills["trail"]["lvl"] > 0:
            self.trail_spawn_timer += dt
            if self.trail_spawn_timer >= 0.15:
                self.trail_spawn_timer = 0
                self.trail_droplets.append(TrailDroplet(px, py))

        for droplet in self.trail_droplets[:]:
            droplet.update(dt)
            if droplet.timer <= 0:
                self.trail_droplets.remove(droplet)
            else:
                for enemy in self.enemies[:]:
                    tdist = math.sqrt((droplet.x - enemy.x)**2 + (droplet.y - enemy.y)**2)
                    if tdist < enemy.size + droplet.radius:
                        trail_damage = 0.5 + (self.skills["trail"]["lvl"] * 0.3)
                        enemy.hp -= trail_damage * dt * 10
                        if enemy.hp <= 0:
                            if enemy in self.enemies:
                                self.enemies.remove(enemy)
                                reward = 10 + (self.skills["shatter"]["lvl"] * 5)
                                self.dna_bank += reward

        for orb in self.orbs[:]:
            orb.update(dt)
            odx = px - orb.x
            ody = py - orb.y
            odist = math.sqrt(odx * odx + ody * ody)

            if self.magnet_range > 0 and odist < self.blob_radius + self.magnet_range:
                pull_speed = (1.0 - (odist / (self.blob_radius + self.magnet_range))) * 150 * dt
                orb.x += (odx / odist) * pull_speed
                orb.y += (ody / odist) * pull_speed

            if odist < self.blob_radius + orb.radius:
                self.orbs.remove(orb)
                self.dna_bank += orb.value
                self.run_dna_collected += orb.value
                # Increased maximum growth cap and growth amount per orb!
                self.blob_radius = min(SCREEN_HEIGHT * 0.14, self.blob_radius + 0.8)

                max_orbs = 30 + (self.skills["shape_swarm"]["lvl"] * 20)
                if len(self.orbs) < max_orbs:
                    self.orbs.append(GlitchOrb())

        self.enemy_spawn_timer += dt
        spawn_rate = max(0.25, (2.0 - (time_elapsed / 25.0)) - (self.run_dna_collected * 0.005))
        if self.enemy_spawn_timer > spawn_rate:
            self.enemy_spawn_timer = 0
            enemy_type = random.choices(
                [JudgmentEye, VoidSeeker, GorgonCore, ShooterEye], 
                weights=[35, 25, 15, 25], 
                k=1
            )[0]
            self.enemies.append(enemy_type(px, py, difficulty_mult))

        for proj in self.enemy_projectiles[:]:
            proj.update(dt)
            pdist = math.sqrt((proj.x - px)**2 + (proj.y - py)**2)
            if pdist < self.blob_radius + proj.radius:
                self.enemy_projectiles.remove(proj)
                self.health -= 1
                if self.health <= 0:
                    time_survived = 60.0 - max(0.0, self.time_remaining)
                    self.dna_bank += int(time_survived)
                    self.round_won = False
                    self.state = "SKILL_TREE"
                break
            elif proj.finished:
                self.enemy_projectiles.remove(proj)

        if self.skills["acid"]["lvl"] > 0:
            self.acid_cooldown += dt
            acid_rate = max(0.4, 2.0 - (self.skills["acid"]["lvl"] * 0.3))
            if self.acid_cooldown >= acid_rate and self.enemies:
                target_enemy = random.choice(self.enemies)
                self.active_acid.append(AcidSpitProjectile(self.player_pos, [target_enemy.x, target_enemy.y]))
                self.acid_cooldown = 0

        attack_damage = 1 + self.skills["damage"]["lvl"]

        for acid in self.active_acid[:]:
            acid.update(dt)
            for enemy in self.enemies[:]:
                adx = acid.x - enemy.x
                ady = acid.y - enemy.y
                if math.sqrt(adx * adx + ady * ady) < enemy.size * 0.8:
                    enemy.hp -= attack_damage
                    acid.finished = True
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
                        reward = 10 + (self.skills["shatter"]["lvl"] * 5)
                        self.dna_bank += reward
                    break
            if acid.finished:
                self.active_acid.remove(acid)

        if self.skills["lash"]["lvl"] > 0:
            self.tentacle_cooldown += dt
            if self.tentacle_cooldown >= 0.25 and len(self.active_shots) < self.max_active_tentacles:
                closest_enemy = None
                min_e_dist = self.tentacle_reach

                for enemy in self.enemies:
                    edx = enemy.x - px
                    edy = enemy.y - py
                    edist = math.sqrt(edx * edx + edy * edy)
                    if edist < min_e_dist:
                        min_e_dist = edist
                        closest_enemy = enemy

                if closest_enemy:
                    self.active_shots.append(TentacleShot(self.player_pos, [closest_enemy.x, closest_enemy.y], self.tentacle_reach))
                    self.tentacle_cooldown = 0

        for shot in self.active_shots[:]:
            shot.start = list(self.player_pos)
            shot.update(dt)

            for enemy in self.enemies[:]:
                tdx = shot.current_tip[0] - enemy.x
                tdy = shot.current_tip[1] - enemy.y
                if math.sqrt(tdx * tdx + tdy * tdy) < enemy.size * 0.8:
                    enemy.hp -= attack_damage
                    shot.finished = True
                    if enemy.hp <= 0:
                        self.enemies.remove(enemy)
                        reward = 10 + (self.skills["shatter"]["lvl"] * 5)
                        self.dna_bank += reward
                    break

            if shot.finished:
                self.active_shots.remove(shot)

        for enemy in self.enemies[:]:
            if isinstance(enemy, ShooterEye):
                enemy.update(px, py, difficulty_mult, self.enemy_projectiles)
            else:
                enemy.update(px, py, difficulty_mult)

            edx = px - enemy.x
            edy = py - enemy.y
            edist = math.sqrt(edx * edx + edy * edy)

            if edist < (self.blob_radius * 0.85 + enemy.size * 0.4):
                self.enemies.remove(enemy)
                self.health -= 1
                if self.health <= 0:
                    time_survived = 60.0 - max(0.0, self.time_remaining)
                    self.dna_bank += int(time_survived)
                    self.round_won = False
                    self.state = "SKILL_TREE"

    def draw(self, surface):
        surface.fill((20, 22, 32))

        if self.state == "HOME":
            self.draw_home_screen(surface)
            return
        elif self.state == "SKILL_TREE":
            self.draw_skill_tree_screen(surface)
            return

        cam_x = self.player_pos[0] - SCREEN_WIDTH / 2
        cam_y = self.player_pos[1] - SCREEN_HEIGHT / 2

        start_x = int(cam_x // 80) * 80
        start_y = int(cam_y // 80) * 80
        for x_pos in range(start_x, start_x + SCREEN_WIDTH + 160, 80):
            pygame.draw.line(surface, (35, 45, 65), (x_pos - cam_x, 0), (x_pos - cam_x, SCREEN_HEIGHT), 1)
        for y_pos in range(start_y, start_y + SCREEN_HEIGHT + 160, 80):
            pygame.draw.line(surface, (35, 45, 65), (0, y_pos - cam_y), (SCREEN_WIDTH, y_pos - cam_y), 1)

        for droplet in self.trail_droplets:
            droplet.draw(surface, cam_x, cam_y)

        for orb in self.orbs:
            orb.draw(surface, cam_x, cam_y, self.phase_time)

        for acid in self.active_acid:
            acid.draw(surface, cam_x, cam_y)

        for proj in self.enemy_projectiles:
            proj.draw(surface, cam_x, cam_y)

        for shot in self.active_shots:
            shot.draw(surface, cam_x, cam_y, self.phase_time)

        px_screen = SCREEN_WIDTH / 2
        py_screen = SCREEN_HEIGHT / 2
        blob_pts = []
        num_vertices = 18
        for i in range(num_vertices):
            angle = i * (2 * math.pi / num_vertices)
            wobble = math.sin(self.phase_time * 2 + i) * (self.blob_radius * 0.18)
            r = self.blob_radius + wobble
            vx = px_screen + math.cos(angle) * r
            vy = py_screen + math.sin(angle) * r
            blob_pts.append((vx, vy))
        if len(blob_pts) > 2:
            pygame.draw.polygon(surface, (40, 190, 150), blob_pts, 4)

        for n in range(min(12 + self.run_dna_collected // 10, 35)):
            n_angle = n * 0.8 + self.phase_time * 0.5
            n_dist = (n * 3) % (self.blob_radius * 0.65)
            nx = px_screen + math.cos(n_angle) * n_dist
            ny = py_screen + math.sin(n_angle) * n_dist
            pygame.draw.circle(surface, (230, 80, 130), (int(nx), int(ny)), 4)

        for enemy in self.enemies:
            enemy.draw(surface, cam_x, cam_y)

        if self.control_mode == "JOYSTICK" and self.joystick_center:
            pygame.draw.circle(surface, (100, 100, 100), self.joystick_center, 45, 2)
            if self.joystick_current:
                pygame.draw.circle(surface, (150, 150, 150), self.joystick_current, 20)

        mins = int(self.time_remaining // 60)
        secs = int(self.time_remaining % 60)
        ms = int((self.time_remaining % 1) * 10)
        hud_txt1 = font_small.render(f"TIME: {mins:02d}:{secs:02d}.{ms} | DNA: {self.dna_bank}", True, (240, 240, 100))
        hud_txt2 = font_small.render(f"HP: {self.health}/{self.max_health}", True, (250, 100, 100))
        surface.blit(hud_txt1, (20, 20))
        surface.blit(hud_txt2, (20, 50))

    def draw_home_screen(self, surface):
        surface.fill((15, 15, 22))

        title = font_large.render("COSMIC ABYSS: 60 SECONDS", True, (100, 240, 150))
        sub = font_small.render("Choose controls & dive into the abyss!", True, (180, 180, 180))
        
        surface.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, SCREEN_HEIGHT * 0.18))
        surface.blit(sub, ((SCREEN_WIDTH - sub.get_width()) // 2, SCREEN_HEIGHT * 0.25))

        self.btn_rects = {}

        ctrl_rect = pygame.Rect(SCREEN_WIDTH * 0.15, SCREEN_HEIGHT * 0.34, SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.075)
        self.btn_rects["toggle_control"] = ctrl_rect
        pygame.draw.rect(surface, (70, 70, 120), ctrl_rect, border_radius=10)
        ctrl_txt = font_large.render(f"CONTROLS: {self.control_mode} / WASD", True, (255, 255, 255))
        surface.blit(ctrl_txt, (ctrl_rect.x + (ctrl_rect.width - ctrl_txt.get_width()) // 2, ctrl_rect.y + 16))

        start_rect = pygame.Rect(SCREEN_WIDTH * 0.15, SCREEN_HEIGHT * 0.44, SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.075)
        self.btn_rects["start_game"] = start_rect
        pygame.draw.rect(surface, (40, 160, 90), start_rect, border_radius=10)
        start_txt = font_large.render("START GAME", True, (255, 255, 255))
        surface.blit(start_txt, (start_rect.x + (start_rect.width - start_txt.get_width()) // 2, start_rect.y + 16))

        continue_rect = pygame.Rect(SCREEN_WIDTH * 0.15, SCREEN_HEIGHT * 0.54, SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.075)
        self.btn_rects["continue_game"] = continue_rect
        pygame.draw.rect(surface, (50, 90, 140), continue_rect, border_radius=10)
        continue_txt = font_large.render("CONTINUE", True, (255, 255, 255))
        surface.blit(continue_txt, (continue_rect.x + (continue_rect.width - continue_txt.get_width()) // 2, continue_rect.y + 16))

        shop_rect = pygame.Rect(SCREEN_WIDTH * 0.15, SCREEN_HEIGHT * 0.64, SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.075)
        self.btn_rects["open_shop"] = shop_rect
        pygame.draw.rect(surface, (140, 100, 40), shop_rect, border_radius=10)
        shop_txt = font_large.render("PERMANENT SKILL TREE", True, (255, 255, 255))
        surface.blit(shop_txt, (shop_rect.x + (shop_rect.width - shop_txt.get_width()) // 2, shop_rect.y + 16))

        exit_rect = pygame.Rect(SCREEN_WIDTH * 0.15, SCREEN_HEIGHT * 0.74, SCREEN_WIDTH * 0.7, SCREEN_HEIGHT * 0.075)
        self.btn_rects["exit_game"] = exit_rect
        pygame.draw.rect(surface, (140, 40, 40), exit_rect, border_radius=10)
        exit_txt = font_large.render("EXIT GAME", True, (255, 255, 255))
        surface.blit(exit_txt, (exit_rect.x + (exit_rect.width - exit_txt.get_width()) // 2, exit_rect.y + 16))

    def draw_skill_tree_screen(self, surface):
        surface.fill((15, 15, 22))

        header_text = "=== ROUND CLEARED! VICTORY! ===" if self.round_won else "=== PERMANENT SKILL TREE ==="
        header_color = (100, 240, 150) if self.round_won else (240, 220, 100)

        title = font_large.render(header_text, True, header_color)
        sub = font_small.render(f"TOTAL DNA BANK: {self.dna_bank}", True, (100, 240, 150))
        surface.blit(title, (SCREEN_WIDTH * 0.08, SCREEN_HEIGHT * 0.025))
        surface.blit(sub, (SCREEN_WIDTH * 0.08, SCREEN_HEIGHT * 0.065))

        y_offset = 0.10
        keys = list(self.skills.keys())
        self.btn_rects = {}

        for key in keys:
            sk = self.skills[key]
            cost = (sk["lvl"] + 1) * sk["base_cost"]
            btn_rect = pygame.Rect(SCREEN_WIDTH * 0.08, SCREEN_HEIGHT * y_offset, SCREEN_WIDTH * 0.84, SCREEN_HEIGHT * 0.058)
            self.btn_rects[key] = btn_rect

            color = (50, 80, 120) if self.dna_bank >= cost else (40, 45, 55)
            pygame.draw.rect(surface, color, btn_rect, border_radius=8)
            pygame.draw.rect(surface, (100, 150, 200), btn_rect, width=2, border_radius=8)

            txt1 = font_small.render(f"{sk['name']} (Lvl {sk['lvl']}) - Cost: {cost} DNA", True, (255, 255, 255))
            txt2 = font_small.render(f"[{sk['desc']}]", True, (180, 180, 180))
            surface.blit(txt1, (btn_rect.x + 12, btn_rect.y + 3))
            surface.blit(txt2, (btn_rect.x + 12, btn_rect.y + 23))

            y_offset += 0.062

        next_rect = pygame.Rect(SCREEN_WIDTH * 0.08, SCREEN_HEIGHT * 0.78, SCREEN_WIDTH * 0.84, SCREEN_HEIGHT * 0.08)
        self.btn_rects["next_round"] = next_rect
        pygame.draw.rect(surface, (40, 180, 90), next_rect, border_radius=10)
        next_txt = font_large.render("START NEXT RUN", True, (255, 255, 255))
        surface.blit(next_txt, (next_rect.x + (next_rect.width - next_txt.get_width()) // 2, next_rect.y + 16))

        menu_rect = pygame.Rect(SCREEN_WIDTH * 0.08, SCREEN_HEIGHT * 0.88, SCREEN_WIDTH * 0.84, SCREEN_HEIGHT * 0.08)
        self.btn_rects["main_menu"] = menu_rect
        pygame.draw.rect(surface, (120, 50, 50), menu_rect, border_radius=10)
        menu_txt = font_large.render("MAIN MENU", True, (255, 255, 255))
        surface.blit(menu_txt, (menu_rect.x + (menu_rect.width - menu_txt.get_width()) // 2, menu_rect.y + 16))

    def handle_touch(self, pos):
        if self.state == "HOME":
            for key, rect in self.btn_rects.items():
                if rect.collidepoint(pos):
                    if key == "start_game":
                        self.start_new_game()
                    elif key == "continue_game":
                        self.continue_game()
                    elif key == "open_shop":
                        self.state = "SKILL_TREE"
                    elif key == "toggle_control":
                        self.control_mode = "JOYSTICK" if self.control_mode == "TOUCH" else "TOUCH"
                    elif key == "exit_game":
                        pygame.quit()
                        sys.exit()
        elif self.state == "SKILL_TREE":
            for key, rect in self.btn_rects.items():
                if rect.collidepoint(pos):
                    if key == "next_round":
                        self.reset_run()
                        self.state = "PLAYING"
                    elif key == "main_menu":
                        self.state = "HOME"
                    else:
                        self.buy_skill(key)
        elif self.state == "PLAYING":
            if self.control_mode == "JOYSTICK":
                self.joystick_center = pos
                self.joystick_current = pos
            else:
                cam_x = self.player_pos[0] - SCREEN_WIDTH / 2
                cam_y = self.player_pos[1] - SCREEN_HEIGHT / 2
                self.target_pos = [pos[0] + cam_x, pos[1] + cam_y]

    def handle_drag(self, pos):
        if self.state == "PLAYING":
            if self.control_mode == "JOYSTICK" and self.joystick_center:
                self.joystick_current = pos
            elif self.control_mode == "TOUCH":
                cam_x = self.player_pos[0] - SCREEN_WIDTH / 2
                cam_y = self.player_pos[1] - SCREEN_HEIGHT / 2
                self.target_pos = [pos[0] + cam_x, pos[1] + cam_y]

    def handle_release(self):
        if self.state == "PLAYING" and self.control_mode == "JOYSTICK":
            self.joystick_center = None
            self.joystick_current = None

# --- RUN LOOP ---

def main():
    game = Game()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_touch(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    game.handle_drag(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                game.handle_release()

        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()