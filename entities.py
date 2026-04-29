import pygame

class Jogador:
    SPRITE_FILES = {
        "idle": "assets/folhadesprites.png",
        "run": "assets/folhadesprites.png",
        "jump": "assets/folhadesprites.png",
        "shoot": "assets/folhadesprites.png"
    }
    FRAME_SIZE = (80, 80)
    def __init__(self, CHAO_Y):
        self.rect = pygame.Rect(100, CHAO_Y - 80 + 10, 40, 80)
        self.pos_x, self.pos_y = float(self.rect.x), float(self.rect.y)
        self.velX = self.velY = self.jumpBuffer = 0
        self.velocidadeMax, self.aceleracao, self.desaceleracao = 400, 1000, 1400
        self.forcaPulo, self.gravidade, self.gravidadeQueda = -820, 1600, 2000
        self.noChao, self.direcao, self.estado = True, "direita", "idle"
        self.frame_index = 0
        self.frame_timer = 0
        self.anim_speed = 0.15  
        self.animations = {}
        self.current_animation = []
        self.load_all_animations()
        self._anim_nome = ""
        self.set_animation("idle")

    def load_all_animations(self):
        for estado, filename in self.SPRITE_FILES.items():
            try:
                folha = pygame.image.load(filename).convert_alpha()
            except Exception:
                folha = None
            frames = []
            if folha:
                frame_w, frame_h = self.FRAME_SIZE
                num_frames = folha.get_width() // frame_w
                for i in range(num_frames):
                    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                    frame.blit(folha, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                    frames.append(frame)
            self.animations[estado] = frames

    def set_animation(self, estado):
        self._anim_nome = estado
        self.current_animation = self.animations.get(estado, [])
        if self.current_animation:
            self.frame_index = self.frame_index % len(self.current_animation)
            self.rect.height = self.current_animation[0].get_height()

    def update(self, dt, teclas, mov, CHAO_Y, LARGURA_MAPA, plataformas=None, chao_ativo=True):
        self.jumpBuffer = max(0, self.jumpBuffer - dt)
        if mov:
            self.direcao = "direita" if mov > 0 else "esquerda"
            acel = self.desaceleracao if mov * self.velX < 0 else self.aceleracao
            self.velX = max(-self.velocidadeMax, min(self.velocidadeMax, self.velX + mov * acel * dt))
        else:
            self.velX = max(0, abs(self.velX) - self.desaceleracao * dt) * (1 if self.velX > 0 else -1)
        
        # Movimento X e Colisão Lateral
        self.pos_x += self.velX * dt
        self.rect.x = int(self.pos_x)
        if plataformas:
            for p in plataformas:
                if self.rect.colliderect(p):
                    if self.rect.bottom > p.top + 10:
                        if self.velX > 0: self.rect.right = p.left
                        elif self.velX < 0: self.rect.left = p.right
                        self.pos_x = float(self.rect.x)
                        self.velX = 0

        # Limites do mapa
        if self.pos_x < 0:
            self.pos_x = 0; self.rect.x = 0; self.velX = 0
        elif self.pos_x > LARGURA_MAPA - self.rect.width:
            self.pos_x = LARGURA_MAPA - self.rect.width; self.rect.x = int(self.pos_x); self.velX = 0

        # Movimento Y e Gravidade
        self.velY += (self.gravidade if self.velY < 0 else self.gravidadeQueda) * dt
        self.pos_y += self.velY * dt
        self.rect.y = int(self.pos_y)
        self.noChao = False

        if chao_ativo and self.rect.bottom >= CHAO_Y + 10:
            self.rect.bottom, self.velY, self.noChao = CHAO_Y + 10, 0, True
            self.pos_y = float(self.rect.y)

        # Colisões com Plataformas (Pouso e Cabeçada)
        if plataformas:
            for p in plataformas:
                if self.rect.colliderect(p):
                    if self.velY >= 0 and self.rect.bottom - self.velY * dt <= p.top + 10:
                        self.rect.bottom, self.velY, self.noChao = p.top, 0, True
                        self.pos_y = float(self.rect.y)
                        break
                    elif self.velY < 0 and self.rect.top - self.velY * dt >= p.bottom - 10:
                        self.rect.top, self.velY = p.bottom, 0
                        self.pos_y = float(self.rect.y)
                        break

        if self.jumpBuffer > 0 and self.noChao:
            self.velY, self.noChao, self.jumpBuffer = self.forcaPulo, False, 0
        elif not (teclas[pygame.K_w] or teclas[pygame.K_UP]) and self.velY < 0:
            self.velY *= 0.7

        self.estado = "jump" if self.velY < 0 else "fall" if not self.noChao else "run" if self.velX else "idle"
        if self.estado not in self.animations:
            if self._anim_nome != "idle":
                self.set_animation("idle")
        elif self._anim_nome != self.estado:
            self.set_animation(self.estado)

        if self.current_animation:
            self.frame_timer += dt
            if self.frame_timer >= self.anim_speed:
                self.frame_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.current_animation)

class Camera:
    def __init__(self, largura_tela, largura_mapa):
        self.x = 0.0
        self.offset_x = 0
        self.largura_tela, self.largura_mapa = largura_tela, largura_mapa
        self.pos_tela = largura_tela / 2

    def update(self, dt, jogador, mov):
        # Se o mapa for menor que a tela (ex: casas de 800px em tela de 1280px)
        if self.largura_mapa < self.largura_tela:
            self.offset_x = (self.largura_tela - self.largura_mapa) // 2
            self.x = 0
            return
        
        self.offset_x = 0
        alvo_pos = self.largura_tela * (0.4 if mov > 0 else 0.6 if mov < 0 else 0.45 if jogador.direcao == "direita" else 0.55)
        self.pos_tela += (alvo_pos - self.pos_tela) * 2.0 * dt
        alvoCamera = jogador.rect.centerx - self.pos_tela
        vel = min(0.5 + abs(alvoCamera - self.x) / 80.0 * 4.5, 8.0)
        self.x = max(0, min(self.x + (alvoCamera - self.x) * vel * dt, self.largura_mapa - self.largura_tela))

class SistemaVisual:
    def __init__(self, largura, altura, zoom_max=3.0):
        self.nivel = 1.0
        self.max = zoom_max
        self.largura, self.altura = largura, altura
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.nivel = max(1.0, min(self.max, self.nivel + (0.1 if event.y > 0 else -0.1)))

    def render(self, surface_jogo, tela_display, mouse_pos):
        if self.nivel == 1.0:
            tela_display.blit(surface_jogo, (0, 0))
            return
            
        nw, nh = int(self.largura * self.nivel), int(self.altura * self.nivel)
        scaled = pygame.transform.smoothscale(surface_jogo, (nw, nh))
        
        px, py = mouse_pos[0] / self.largura, mouse_pos[1] / self.altura
        ox = max(-nw + self.largura, min(0, int(mouse_pos[0] - nw * px)))
        oy = max(-nh + self.altura, min(0, int(mouse_pos[1] - nh * py)))
        
        tela_display.fill((0, 0, 0))
        tela_display.blit(scaled, (ox, oy))
