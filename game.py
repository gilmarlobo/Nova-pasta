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

class Heroi(Personagem):
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
        self.regen_timer = 0  # Novo: temporizador para regeneração
        self.regen_interval = 2.0  # Novo: intervalo de 2 segundos (2000 ms)

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
        
        # Novo: lógica de regeneração de vida
        if self.vida < 100 and not self.is_dying:
            self.regen_timer += dt
            if self.regen_timer >= self.regen_interval:
                self.vida = min(self.vida + 1, 100)  # Adiciona 1, sem ultrapassar 100
                self.regen_timer = 0  # Reseta o temporizador
            
class Zumbi(Personagem):
    def __init__(self, x, y):
        animations = {
            "andando": [f"fzandando{i}" for i in range(1, 11)],
            "morrendo": [f"fzmorto{i}" for i in range(1, 13)],
            "atacando": [f"fzataque{i}" for i in range(1, 9)]  # Novo: animação de ataque
        }
        super().__init__(x, y, vida=100, speed=50, animations=animations, initial_animation="andando")
        self.is_dying = False
        self.respawn_timer = 0
        self.respawn_duration = 1.0
        self.current_animation = "andando"
        self.actor.y = GROUND_Y
        self.rect.y = GROUND_Y
        self.respawn_count = 0
        self.is_attacking = False  # Novo: estado de ataque

    def move(self, dt, target):
        if not self.is_dying and self.vida > 0 and not self.is_attacking:  # Só move se não está atacando
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
                    self.is_attacking = False  # Reseta ataque no respawn
                else:
                    self.vida = 0
        else:
            self.move(dt, target)
        
        # Controle da animação de ataque
        if self.is_attacking:
            if self.frame >= len(self.animations["atacando"]) - 1:
                self.is_attacking = False
                self.current_animation = "andando"
                self.frame = 0
                self.frame_time = 0
        
        self.update_animation(dt)
class Jogo:
    def __init__(self):
        self.heroi = Heroi(40, GROUND_Y)
        self.zumbi = Zumbi(640, GROUND_Y)
        self.background = "bckg"
        self.game_over = False
        self.win = False
        music.set_volume(0.5)
        music.play("fundo")

    def draw(self):
        screen.clear()
        screen.blit(self.background, (0, 0))
        self.heroi.draw()
        if self.zumbi.vida > 0 or self.zumbi.is_dying:
            self.zumbi.draw()
        screen.draw.text(f"Player XP: {int(self.heroi.vida)}", topleft=(10, 10), fontsize=20, color="white")
        if self.zumbi.vida > 0:
            screen.draw.text(f"Zombie XP: {int(self.zumbi.vida)}", topleft=(10, 30), fontsize=20, color="white")
        if self.game_over:
            screen.draw.text("Game Over", center=(WIDTH/2, HEIGHT/2), fontsize=70, color="white")
        elif self.win:  # Alterado: adiciona elif para evitar sobreposição
            screen.draw.text("You Win!", center=(WIDTH/2, HEIGHT/2), fontsize=70, color="white")

    def update(self, dt):
        if self.game_over or self.win:  # Alterado: para o jogo se win for True
            return
        
        self.heroi.move(dt)
        self.heroi.update(dt)
        self.zumbi.update(dt, self.heroi)
        
        if self.heroi.collides_with(self.zumbi) and not self.zumbi.is_dying:
            if self.heroi.is_attacking:
                self.zumbi.take_damage(20 * dt)
                if self.zumbi.vida <= 0:
                    self.zumbi.is_dying = True
                    self.zumbi.respawn_timer = self.zumbi.respawn_duration
                    self.zumbi.current_animation = "morrendo"
                    self.zumbi.frame = 0
                    self.zumbi.is_attacking = False
            elif self.heroi.immune_timer <= 0 and not self.heroi.is_dying:
                if not self.zumbi.is_attacking:
                    self.zumbi.is_attacking = True
                    self.zumbi.current_animation = "atacando"
                    self.zumbi.frame = 0
                    self.zumbi.frame_time = 0
                self.heroi.take_damage(2)
        
        if self.heroi.is_dying and self.heroi.death_animation_finished:
            self.game_over = True
        
        # Novo: verifica condição de vitória
        if self.zumbi.vida <= 0 and self.zumbi.respawn_count == 3 and not self.zumbi.is_dying:
            self.win = True
        
        if self.zumbi.vida <= 0:
            self.heroi.vida += 25 * dt

jogo = Jogo()

def draw():
    jogo.draw()

def update(dt):
    jogo.update(dt)

pgzrun.go()