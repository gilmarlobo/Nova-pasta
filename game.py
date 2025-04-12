import pgzrun
from pygame import Rect

WIDTH = 800
HEIGHT = 450
GRAVITY = 900
JUMP_FORCE = -450
GROUND_Y = 380

class Personagem:
    def __init__(self, x, y, vida, speed, animations, initial_animation):
        self.actor = Actor(animations[initial_animation][0], topleft=(x, y))
        self.rect = Rect(x, y, 12, 12)
        self.vida = vida
        self.speed = speed
        self.animations = animations
        self.current_animation = initial_animation
        self.frame = 0
        self.frame_time = 0
        self.frame_duration = 0.05

    def draw(self):
        self.actor.width = 12
        self.actor.height = 12
        self.actor.draw()

    def update_animation(self, dt):
        self.frame_time += dt
        if self.frame_time >= self.frame_duration:
            self.frame_time = 0
            self.frame = (self.frame + 1) % len(self.animations[self.current_animation])
            self.actor.image = self.animations[self.current_animation][self.frame]

    def take_damage(self, amount):
        self.vida -= amount
        return self.vida > 0

    def collides_with(self, other):
        return self.rect.colliderect(other.rect)

class Candidato(Personagem):
    def __init__(self, x, y):
        animations = {
            "parado": [f"heroiparado{i}" for i in range(1, 11)],
            "correndo": [f"heroicorre{i}" for i in range(1, 11)],
            "atacando": [f"heroiataque{i}" for i in range(1, 11)],
            "pulando": [f"heroipula{i}" for i in range(1, 11)],
            "morrendo": [f"heroimorto{i}" for i in range(1, 11)]
        }
        super().__init__(x, y, vida=100, speed=270, animations=animations, initial_animation="parado")
        self.is_jumping = False
        self.jump_velocity = 0
        self.is_attacking = False
        self.immune_timer = 0
        self.immune_duration = 0.3
        self.is_dying = False
        self.death_animation_finished = False
        self.death_frame_duration = 0.1
        self.actor.y = GROUND_Y
        self.rect.y = GROUND_Y
        self.regen_timer = 0
        self.regen_interval = 2.0

    def draw(self):
        if not self.is_dying or not self.death_animation_finished:
            self.actor.width = 12
            self.actor.height = 12
            self.actor.draw()

    def move(self, dt):
        if self.is_dying or self.vida <= 0:
            return
        new_x = self.actor.x
        is_moving = False
        if keyboard.K_LEFT:
            new_x -= self.speed * dt
            is_moving = True
        if keyboard.K_RIGHT:
            new_x += self.speed * dt
            is_moving = True
        if not self.is_jumping and keyboard.K_UP:
            self.is_jumping = True
            self.jump_velocity = JUMP_FORCE
            self.current_animation = "pulando"
        if keyboard.K_SPACE and not self.is_attacking:
            self.is_attacking = True
            self.current_animation = "atacando"
            self.frame = 0
            self.frame_time = 0
            self.immune_timer = self.immune_duration
        self.actor.x = max(0, min(new_x, WIDTH - 12))
        self.rect.x = self.actor.x
        if not self.is_attacking and not self.is_jumping:
            self.current_animation = "correndo" if is_moving else "parado"

    def update(self, dt):
        if self.is_dying:
            self.frame_time += dt
            if self.frame_time >= self.death_frame_duration:
                self.frame_time = 0
                self.frame = min(self.frame + 1, len(self.animations["morrendo"]) - 1)
                self.actor.image = self.animations["morrendo"][self.frame]
            if self.frame >= len(self.animations["morrendo"]) - 1:
                self.death_animation_finished = True
            return
        
        if self.vida <= 0:
            self.is_dying = True
            self.current_animation = "morrendo"
            self.frame = 0
            self.frame_time = 0
            self.is_jumping = False
            self.is_attacking = False
            return

        if self.is_jumping:
            self.jump_velocity += GRAVITY * dt
            self.actor.y += self.jump_velocity * dt
            if self.actor.y >= GROUND_Y:
                self.actor.y = GROUND_Y
                self.rect.y = GROUND_Y
                self.is_jumping = False
                self.jump_velocity = 0
                self.current_animation = "parado"
            else:
                self.current_animation = "pulando"
        
        self.rect.y = self.actor.y
        self.update_animation(dt)
        
        if self.is_attacking:
            if self.frame >= len(self.animations["atacando"]) - 1:
                self.is_attacking = False
                self.current_animation = "parado"
                self.frame = 0
                self.frame_time = 0
        
        if self.immune_timer > 0:
            self.immune_timer -= dt
        
        if self.vida < 100 and not self.is_dying:
            self.regen_timer += dt
            if self.regen_timer >= self.regen_interval:
                self.vida = min(self.vida + 1, 100)
                self.regen_timer = 0

class Zumbi(Personagem):
    def __init__(self, x, y):
        animations = {
            "andando": [f"fzandando{i}" for i in range(1, 11)],
            "morrendo": [f"fzmorto{i}" for i in range(1, 13)],
            "atacando": [f"fzataque{i}" for i in range(1, 9)]
        }
        super().__init__(x, y, vida=100, speed=50, animations=animations, initial_animation="andando")
        self.is_dying = False
        self.respawn_timer = 0
        self.respawn_duration = 1.0
        self.current_animation = "andando"
        self.actor.y = GROUND_Y
        self.rect.y = GROUND_Y
        self.respawn_count = 0
        self.is_attacking = False
        self.is_permanently_dead = False

    def move(self, dt, target):
        if not self.is_dying and self.vida > 0 and not self.is_attacking:
            if self.actor.x > target.actor.x:
                self.actor.x -= self.speed * dt
            elif self.actor.x < target.actor.x:
                self.actor.x += self.speed * dt
            self.actor.x = max(0, min(self.actor.x, WIDTH - 12))
            self.rect.x = self.actor.x
            self.actor.y = GROUND_Y
            self.rect.y = GROUND_Y

    def update(self, dt, target):
        if self.is_permanently_dead:
            return

        if self.is_dying:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0 and self.frame >= len(self.animations["morrendo"]) - 1:
                if self.respawn_count < 3:
                    self.is_dying = False
                    self.respawn_count += 1
                    self.vida = 100 + (self.respawn_count * 10)
                    self.actor.x = WIDTH - 50
                    self.actor.y = GROUND_Y
                    self.rect.x = self.actor.x
                    self.rect.y = GROUND_Y
                    self.current_animation = "andando"
                    self.frame = 0
                    self.is_attacking = False
                else:
                    self.is_permanently_dead = True
            self.update_animation(dt)
            return
        
        if not self.is_attacking:
            self.move(dt, target)
        
        if self.is_attacking:
            if self.frame >= len(self.animations["atacando"]) - 1:
                self.is_attacking = False
                self.current_animation = "andando"
                self.frame = 0
                self.frame_time = 0
        
        self.update_animation(dt)

class Zombie_Boss(Personagem):
    def __init__(self, x, y):
        animations = {
            "andando": [f"mzandando{i}" for i in range(1, 11)],
            "atacando": [f"mzataque{i}" for i in range(1, 9)],
            "morrendo": [f"mzmorto{i}" for i in range(1, 13)]
        }
        super().__init__(x, y, vida=150, speed=50, animations=animations, initial_animation="andando")
        self.is_dying = False
        self.is_attacking = False
        self.actor.y = GROUND_Y
        self.rect.y = GROUND_Y

    def move(self, dt, target):
        if not self.is_dying and self.vida > 0 and not self.is_attacking:
            if self.actor.x > target.actor.x:
                self.actor.x -= self.speed * dt
            elif self.actor.x < target.actor.x:
                self.actor.x += self.speed * dt
            self.actor.x = max(0, min(self.actor.x, WIDTH - 12))
            self.rect.x = self.actor.x
            self.actor.y = GROUND_Y
            self.rect.y = GROUND_Y

    def update(self, dt, target):
        if self.is_dying:
            self.update_animation(dt)
            return
        
        if not self.is_attacking:
            self.move(dt, target)
        
        if self.is_attacking:
            if self.frame >= len(self.animations["atacando"]) - 1:
                self.is_attacking = False
                self.current_animation = "andando"
                self.frame = 0
                self.frame_time = 0
        
        self.update_animation(dt)

class Jogo:
    def __init__(self):
        self.state = "menu"
        self.heroi = None
        self.zumbi = None
        self.boss = None
        self.background = "bckg"
        self.game_over = False
        self.win = False
        self.menu_background = "tela_inicial"
        self.play_button = Actor("play", center=(WIDTH/2, HEIGHT/2))
        self.restart_button = Actor("restart", center=(WIDTH/2, HEIGHT/2 + 100))
        self.music_button = Actor("music_on", topright=(WIDTH - 12, 12))
        self.music_enabled = True
        music.set_volume(0.5)
        music.play("fundo")

    def draw(self):
        screen.clear()
        if self.state == "menu":
            screen.blit(self.menu_background, (0, 0))
            self.play_button.draw()
            self.music_button.draw()
        elif self.state == "playing":
            screen.blit(self.background, (0, 0))
            self.heroi.draw()
            if self.zumbi and not self.zumbi.is_permanently_dead:
                self.zumbi.draw()
            if self.boss and (self.boss.vida > 0 or self.boss.is_dying):
                self.boss.draw()
            screen.draw.text(f"Candidato XP: {int(self.heroi.vida)}", topleft=(10, 10), fontsize=20, color="white")
            if self.zumbi and self.zumbi.vida > 0:
                screen.draw.text(f"Zombie XP: {int(self.zumbi.vida)}", topleft=(10, 30), fontsize=20, color="white")
            if self.boss and self.boss.vida > 0:
                screen.draw.text(f"Boss XP: {int(self.boss.vida)}", topleft=(10, 30), fontsize=20, color="white")
            if self.game_over:
                screen.draw.text("Seu projeto foi reprovado.kkkkk", center=(WIDTH/2, HEIGHT/2 - 50), fontsize=70, color="red")
                self.restart_button.draw()
            elif self.win:
                screen.draw.text("Seu projeto foi aprovado, Parabéns!!", center=(WIDTH/2, HEIGHT/2 - 50), fontsize=70, color="green")
                self.restart_button.draw()
            self.music_button.draw()  # Desenha o botão de áudio no jogo

    def update(self, dt):
        if self.state == "menu":
            return
        
        if self.game_over or self.win:
            return
        
        self.heroi.move(dt)
        self.heroi.update(dt)
        
        if self.zumbi and not self.zumbi.is_permanently_dead:
            self.zumbi.update(dt, self.heroi)
        
        if self.boss:
            self.boss.update(dt, self.heroi)
        
        if self.zumbi and self.zumbi.is_permanently_dead and not self.boss:
            self.boss = Zombie_Boss(640, GROUND_Y)
            self.zumbi = None
            if self.music_enabled:
                music.stop()
                music.set_volume(0.5)
                music.play("boss_zombie")
        
        if self.zumbi and not self.zumbi.is_permanently_dead and self.heroi.collides_with(self.zumbi) and not self.zumbi.is_dying:
            if self.heroi.is_attacking:
                self.zumbi.take_damage(20 * dt)
                if self.zumbi.vida <= 0:
                    self.zumbi.is_dying = True
                    self.zumbi.respawn_timer = self.zumbi.respawn_duration
                    self.zumbi.current_animation = "morrendo"
                    self.zumbi.frame = 0
                    self.zumbi.is_attacking = False
                    self.heroi.vida = min(self.heroi.vida + 25, 100)
            elif self.heroi.immune_timer <= 0 and not self.heroi.is_dying:
                if not self.zumbi.is_attacking:
                    self.zumbi.is_attacking = True
                    self.zumbi.current_animation = "atacando"
                    self.zumbi.frame = 0
                    self.zumbi.frame_time = 0
                self.heroi.take_damage(2)
        
        if self.boss and self.heroi.collides_with(self.boss) and not self.boss.is_dying:
            if self.heroi.is_attacking:
                self.boss.take_damage(20 * dt)
                if self.boss.vida <= 0:
                    self.boss.is_dying = True
                    self.boss.current_animation = "morrendo"
                    self.boss.frame = 0
                    self.boss.is_attacking = False
                    self.heroi.vida = min(self.heroi.vida + 50, 100)
            elif self.heroi.immune_timer <= 0 and not self.heroi.is_dying:
                if not self.boss.is_attacking:
                    self.boss.is_attacking = True
                    self.boss.current_animation = "atacando"
                    self.boss.frame = 0
                    self.boss.frame_time = 0
                self.heroi.take_damage(2)
        
        if self.heroi.is_dying and self.heroi.death_animation_finished:
            self.game_over = True
        
        if self.boss and self.boss.vida <= 0 and self.boss.is_dying and self.boss.frame >= len(self.boss.animations["morrendo"]) - 1:
            self.win = True

jogo = Jogo()

def draw():
    jogo.draw()

def update(dt):
    jogo.update(dt)

def on_mouse_down(pos):
    if jogo.music_button.collidepoint(pos):  # Botão de áudio clicado em qualquer estado
        jogo.music_enabled = not jogo.music_enabled
        if jogo.music_enabled:
            jogo.music_button.image = "music_on"
            music.set_volume(0.5)
            if jogo.state == "menu" or not (jogo.game_over or jogo.win):
                music.stop()
                music.play("fundo" if not jogo.boss else "boss_zombie")
        else:
            jogo.music_button.image = "music_off"
            music.stop()
            music.set_volume(0.0)
    elif jogo.state == "menu" and jogo.play_button.collidepoint(pos):
        jogo.state = "playing"
        jogo.heroi = Candidato(40, GROUND_Y)
        jogo.zumbi = Zumbi(640, GROUND_Y)
        jogo.boss = None
        jogo.game_over = False
        jogo.win = False
        if not jogo.music_enabled:
            music.stop()
            music.set_volume(0.0)
        else:
            music.stop()
            music.set_volume(0.5)
            music.play("fundo")
    elif (jogo.game_over or jogo.win) and jogo.restart_button.collidepoint(pos):
        jogo.state = "menu"
        jogo.heroi = None
        jogo.zumbi = None
        jogo.boss = None
        jogo.game_over = False
        jogo.win = False
        if not jogo.music_enabled:
            music.stop()
            music.set_volume(0.0)
        else:
            music.stop()
            music.set_volume(0.5)
            music.play("fundo")

pgzrun.go()