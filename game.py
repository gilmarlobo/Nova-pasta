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
        self.death_animation_finished = False  # Novo: indica fim da animação de morte
        self.death_frame_duration = 0.1  # Novo: duração mais lenta para morte
        self.actor.y = GROUND_Y
        self.rect.y = GROUND_Y

    def draw(self):
        if not self.is_dying or not self.death_animation_finished:  # Desenha até o fim da animação
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
            # Usa frame_duration mais lento para animação de morte
            self.frame_time += dt
            if self.frame_time >= self.death_frame_duration:
                self.frame_time = 0
                self.frame = min(self.frame + 1, len(self.animations["morrendo"]) - 1)
                self.actor.image = self.animations["morrendo"][self.frame]
            if self.frame >= len(self.animations["morrendo"]) - 1:
                self.death_animation_finished = True  # Marca animação como concluída
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
            
class Zumbi(Personagem):
    def __init__(self, x, y):
        animations = {
            "andando": [f"fzandando{i}" for i in range(1, 11)],
            "morrendo": [f"fzmorto{i}" for i in range(1, 13)]
        }
        super().__init__(x, y, vida=100, speed=50, animations=animations, initial_animation="andando")
        self.is_dying = False
        self.respawn_timer = 0
        self.respawn_duration = 1.0
        self.current_animation = "andando"
        # Garante que y inicial está correto
        self.actor.y = GROUND_Y
        self.rect.y = GROUND_Y

    def move(self, dt, target):
        if not self.is_dying and self.vida > 0:
            if self.actor.x > target.actor.x:
                self.actor.x -= self.speed * dt
            elif self.actor.x < target.actor.x:
                self.actor.x += self.speed * dt
            self.actor.x = max(0, min(self.actor.x, WIDTH - 12))
            self.rect.x = self.actor.x
            # Mantém y fixo no chão
            self.actor.y = GROUND_Y
            self.rect.y = GROUND_Y

    def update(self, dt, target):
        if self.is_dying:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0 and self.frame >= len(self.animations["morrendo"]) - 1:
                self.is_dying = False
                self.vida = 100
                self.actor.x = WIDTH - 50
                self.actor.y = GROUND_Y
                self.rect.x = self.actor.x
                self.rect.y = GROUND_Y
                self.current_animation = "andando"
                self.frame = 0
        else:
            self.move(dt, target)
        self.update_animation(dt)

class Jogo:
    def __init__(self):
        self.heroi = Heroi(40, GROUND_Y)
        self.zumbi = Zumbi(640, GROUND_Y)
        self.background = "bckg"
        self.game_over = False
        music.set_volume(0.5)
        music.play("fundo")

    def draw(self):
        screen.clear()
        screen.blit(self.background, (0, 0))
        self.heroi.draw()
        if self.zumbi.vida > 0 or self.zumbi.is_dying:
            self.zumbi.draw()
        screen.draw.text(f"Player XP: {self.heroi.vida}", topleft=(10, 10), fontsize=20, color="white")
        if self.zumbi.vida > 0:
            screen.draw.text(f"Zombie XP: {self.zumbi.vida}", topleft=(10, 30), fontsize=20, color="white")
        if self.game_over:
            screen.draw.text("Game Over", center=(WIDTH/2, HEIGHT/2), fontsize=40, color="red")

    def update(self, dt):
        if self.game_over:
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
            elif self.heroi.immune_timer <= 0 and not self.heroi.is_dying:
                self.heroi.take_damage(2)
        
        # Ativa game over apenas após a animação de morte
        if self.heroi.is_dying and self.heroi.death_animation_finished:
            self.game_over = True

jogo = Jogo()

def draw():
    jogo.draw()

def update(dt):
    jogo.update(dt)

pgzrun.go()