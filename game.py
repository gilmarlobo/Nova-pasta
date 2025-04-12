import pgzrun
from pygame import Rect  

WIDTH = 800
HEIGHT = 450

background = "bckg"
music.set_volume(0.5) 
music.play("fundo")   

# Sprite do heroi
player_rect = Rect(40, 300, 12, 12)
player = Actor("heroiparado1", topleft=(40, 300))
player.width = 12
player.height = 12

player_xp = 100
vida_fzombie = 100
fzombi_alive = True

# Sprite zumbi fêmea
fzombi_rect = Rect(640, 310, 12, 12)
fzombi = Actor("fzandando1", topleft=(640, 310))
fzombi.width = 12
fzombi.height = 12

# Pulo
is_jumping = False
jump_velocity = 0
gravity = 900
jump_force = -500
ground_y = 374

# Animações
player_parado = [f"heroiparado{i}" for i in range(1, 11)]
fzombi_andando = [f"fzandando{i}" for i in range(1, 11)]
fzombi_morto = [f"fzmorto{i}" for i in range(1, 13)]
run_frames = [f"heroicorre{i}" for i in range(1, 11)]
attack_frames = [f"heroiataque{i}" for i in range(1, 11)]
jump_frames = [f"heroipula{i}" for i in range(1, 11)]
current_frame = 0
frame_time = 0
frame_duration = 0.05
is_attacking = False
attack_frame = 0

fzombi_dying = False
fzombi_respawn_timer = 0
fzombi_death_frame = 0
fzombi_death_duration = 1.0

fzombi_frame = 0
fzombi_frame_time = 0
fzombi_frame_duration = 0.05

player_speed = 270
fzombi_speed = 50

# Imunidade e dano
is_immune = False
immune_timer = 0
immune_duration = 0.5
damage_cooldown = 0.5
damage_timer = 0

def draw():
    screen.clear()
    screen.blit(background, (0, 0))
    # Força tamanho antes de desenhar
    player.width = 12
    player.height = 12
    player.draw()
    if fzombi_alive or fzombi_dying:
        fzombi.width = 12
        fzombi.height = 12
        fzombi.draw()
    screen.draw.text(f"Player XP: {player_xp}", topleft=(10, 10), fontsize=20, color="white")
    if fzombi_alive:
        screen.draw.text(f"Zombie XP: {vida_fzombie}", topleft=(10, 30), fontsize=20, color="white")

def update_animation(actor, frames, frame_counter, frame_time, frame_duration, dt):
    frame_time[0] += dt
    if frame_time[0] >= frame_duration:
        frame_time[0] = 0
        frame_counter[0] = (frame_counter[0] + 1) % len(frames)
        actor.image = frames[frame_counter[0]]
        actor.width = 12
        actor.height = 12
    return frame_counter[0], frame_time[0]

def update(dt):
    global current_frame, frame_time, is_attacking, attack_frame
    global fzombi_frame, fzombi_frame_time, player_xp, vida_fzombie, fzombi_alive
    global is_immune, immune_timer, damage_timer
    global is_jumping, jump_velocity
    global fzombi_dying, fzombi_respawn_timer, fzombi_death_frame

    # Movimento do heroi
    is_moving = False
    new_player_x = player.x
    if keyboard.K_LEFT:
        new_player_x -= player_speed * dt
        is_moving = True
    if keyboard.K_RIGHT:
        new_player_x += player_speed * dt
        is_moving = True

    # Controle de pulo
    if not is_jumping and keyboard.K_UP:
        is_jumping = True
        jump_velocity = jump_force

    if is_jumping:
        jump_velocity += gravity * dt
        player.y += jump_velocity * dt
        if player.y >= ground_y:
            player.y = ground_y
            is_jumping = False
            jump_velocity = 0
            player.image = player_parado[0]  # Volta pro parado ao aterrissar
            player.width = 12
            player.height = 12

    # Movimento do zumbi
    if fzombi_alive:
        if fzombi.x > player.x:
            fzombi.x -= fzombi_speed * dt
        elif fzombi.x < player.x:
            fzombi.x += fzombi_speed * dt
        fzombi_rect.x = fzombi.x

    # Atualiza hitbox
    player_rect.x = new_player_x
    player_rect.y = player.y
    if fzombi_alive:
        fzombi_rect.x = fzombi.x
        fzombi_rect.y = fzombi.y

    # Checa colisão
    if fzombi_alive and player_rect.colliderect(fzombi_rect):
        # Impede avanço
        if keyboard.K_LEFT and player.x > fzombi.x:
            player.x = fzombi.x + fzombi.width
            player_rect.x = player.x
        elif keyboard.K_RIGHT and player.x < fzombi.x:
            player.x = fzombi.x - player.width
            player_rect.x = player.x

        # Dano ao zumbi só no ataque
        if is_attacking and vida_fzombie > 0:
            vida_fzombie -= 20 * dt
            if vida_fzombie <= 0:
                fzombi_alive = False
                fzombi_dying = True
                fzombi_respawn_timer = fzombi_death_duration
                fzombi_death_frame = 0
        # Dano ao jogador fora do ataque
        elif not is_immune:
            damage_timer -= dt
            if damage_timer <= 0 and player_xp > 0:
                player_xp -= 2
                damage_timer = damage_cooldown
                player.image = player_parado[0]  # Feedback visual
    else:
        player.x = new_player_x

    # Limita à tela
    player.x = max(0, min(player.x, WIDTH - player.width))
    player_rect.x = player.x
    if fzombi_alive:
        fzombi.x = max(0, min(fzombi.x, WIDTH - fzombi.width))
        fzombi_rect.x = fzombi.x

    # Controle da imunidade
    if is_immune:
        immune_timer -= dt
        if immune_timer <= 0:
            is_immune = False

    # Iniciar ataque
    if keyboard.K_SPACE and not is_attacking:
        is_attacking = True
        is_immune = True
        immune_timer = immune_duration
        attack_frame = 0
        frame_time = 0

    # Animações
    frame_time += dt
    if frame_time >= frame_duration:
        frame_time = 0

        # Animação do zumbi
        if fzombi_alive:
            fzombi_frame, fzombi_frame_time = update_animation(
                fzombi, fzombi_andando, [fzombi_frame], [fzombi_frame_time], fzombi_frame_duration, dt
            )
        elif fzombi_dying:
            fzombi_death_frame, fzombi_frame_time = update_animation(
                fzombi, fzombi_morto, [fzombi_death_frame], [fzombi_frame_time], fzombi_frame_duration, dt
            )
            if fzombi_death_frame >= len(fzombi_morto) - 1:
                fzombi_dying = False
                fzombi_respawn_timer = fzombi_death_duration

        # Animação do jogador
        if is_attacking:
            attack_frame += 1
            if attack_frame < len(attack_frames):
                player.image = attack_frames[attack_frame]
                player.width = 12
                player.height = 12
            else:
                is_attacking = False
                current_frame = 0
                animation_frames = run_frames if is_moving else player_parado
                player.image = animation_frames[current_frame]
                player.width = 12
                player.height = 12
        elif is_jumping:
            player.image = jump_frames[current_frame % len(jump_frames)]
            player.width = 12
            player.height = 12
            current_frame = (current_frame + 1) % len(jump_frames)
        else:
            animation_frames = run_frames if is_moving else player_parado
            current_frame = (current_frame + 1) % len(animation_frames)
            player.image = animation_frames[current_frame]
            player.width = 12
            player.height = 12

    # Respawn do zumbi
    if fzombi_dying:
        fzombi_respawn_timer -= dt
        if fzombi_respawn_timer <= 0 and fzombi_death_frame >= len(fzombi_morto) - 1:
            fzombi_alive = True
            fzombi_dying = False
            fzombi.x = WIDTH - 50
            fzombi.y = ground_y
            fzombi_rect.x = fzombi.x
            fzombi_rect.y = fzombi.y
            vida_fzombie = max(vida_fzombie + 20, 100)
            fzombi_frame = 0
            fzombi_death_frame = 0
            fzombi.image = fzombi_andando[0]
            fzombi.width = 12
            fzombi.height = 12

pgzrun.go()