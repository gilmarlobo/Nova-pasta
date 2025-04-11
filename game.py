import pgzrun
from pygame import Rect  

WIDTH = 800
HEIGHT = 450

background = "bg"

music.set_volume(0.5) 
music.play("fundo")   

#sprite do heroi
player_rect = Rect(40, 300, 12, 12)  # Alinhado com o Actor
player = Actor("heroiparado1", topleft=(40, 300))  # Posição inicial
player.width = 12  # Largura do sprite
player.height = 12  # Altura do sprite

# Animações
idle_frames = [f"heroiparado{i}" for i in range(1, 11)]  # heroiparado1 a heroiparado10
run_frames = [f"heroicorre{i}" for i in range(1, 11)]  # heroic are1 a heroicorre10
attack_frames = [f"heroiataque{i}" for i in range(1, 11)]  # heroiataque1 a heroiataque10
current_frame = 0  # Frame atual pra parado/corrida
frame_time = 0  # Contador de tempo pra troca de frame
frame_duration = 0.1  # Duração de cada frame em segundos (100ms)
is_attacking = False  # Estado de ataque
attack_frame = 0  # Frame atual do ataque

# Movimento
player_speed = 200  # Velocidade em pixels por segundo

def draw():
    screen.clear()
    screen.blit(background, (0, 0))
    player.draw()

def update(dt):
    global current_frame, frame_time, is_attacking, attack_frame
    
    is_moving = False # Movimento
    if keyboard.K_LEFT:
        player.x -= player_speed * dt
        player_rect.x -= player_speed * dt
        is_moving = True
    if keyboard.K_RIGHT:
        player.x += player_speed * dt
        player_rect.x += player_speed * dt
        is_moving = True
    
    # Limita o jogador à tela
    player.x = max(0, min(player.x, WIDTH - player.width))
    player_rect.x = player.x
    
    # Iniciar ataque com K_SPACE
    if keyboard.K_SPACE and not is_attacking:
        is_attacking = True
        attack_frame = 0  # Começa do primeiro frame do ataque
        frame_time = 0  # Reseta o temporizador pra começar imediatamente
    
    frame_time += dt   # Animação
    if frame_time >= frame_duration:
        frame_time = 0  # Reseta o temporizador
        
        if is_attacking:
            attack_frame += 1
            if attack_frame < len(attack_frames):
                player.image = attack_frames[attack_frame]  # Próximo frame do ataque
            else:
                # Fim da animação de ataque
                is_attacking = False
                current_frame = 0  # Reseta pra animação normal
                # Define a animação com base no movimento
                animation_frames = run_frames if is_moving else idle_frames
                player.image = animation_frames[current_frame]
        else: # Animação normal (parado ou corrida)
            animation_frames = run_frames if is_moving else idle_frames
            current_frame = (current_frame + 1) % len(animation_frames)  # Próximo frame, cicla
            player.image = animation_frames[current_frame]

pgzrun.go()