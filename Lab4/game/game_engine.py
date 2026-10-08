import math
import random
import pygame


# --- Player / stamina ------------------------------------------------------------------------
PLAYER_PUSH = 4.2            # arm_position change per accepted keystroke (negative = toward player)
PUSH_STAMINA_COST = 2.0      # stamina spent per accepted keystroke
STAMINA_MIN_TO_PUSH = 10.0   # at or below this the player is exhausted and keystrokes are ignored
STAMINA_REGEN = 0.05         # stamina regained per frame (was 0.8, which could never be drained)

# --- Task 2: AI cycle  NORMAL -> SURGE -> COOLDOWN -> NORMAL (durations in ms, Pygame ticks) ---
AI_NORMAL, AI_SURGE, AI_COOLDOWN = "NORMAL", "SURGE", "COOLDOWN"
AI_PHASE_MS = {AI_NORMAL: 3000, AI_SURGE: 3000, AI_COOLDOWN: 2500}
AI_NEXT_PHASE = {AI_NORMAL: AI_SURGE, AI_SURGE: AI_COOLDOWN, AI_COOLDOWN: AI_NORMAL}
AI_STRENGTH_MULT = {AI_NORMAL: 1.0, AI_SURGE: 3.5, AI_COOLDOWN: 0.3}
AI_PHASE_COLORS = {AI_NORMAL: (190, 190, 190), AI_SURGE: (255, 90, 70), AI_COOLDOWN: (90, 200, 255)}

# --- Task 4: counter-surge bonus -------------------------------------------------------------
COUNTER_EARLY_MS = 250       # a push this long before the surge ends already counts
COUNTER_LATE_MS = 600        # ...and a push this long after cooldown starts still counts
COUNTER_BONUS_MS = 2000      # how long the bonus lasts
COUNTER_PUSH_MULT = 2.0      # player push strength multiplier while active
COUNTER_REGEN_MULT = 4.0     # stamina regeneration multiplier while active


class GameEngine:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None
        
        self.stamina = 100.0
        self.max_stamina = 100.0
        
        self.winner = None
        self.game_state = "PLAYING"
        self.ai_strength = 0.35  
        
        self._reset_cycle()
        
        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            now = pygame.time.get_ticks()
            self._sync_ai_phase(now)

            if self.player_exhausted():
                return
                
            if event.key == pygame.K_LEFT:
                if self.last_key != pygame.K_LEFT: 
                    self._player_push(now)
                    self.last_key = pygame.K_LEFT
            elif event.key == pygame.K_RIGHT:
                if self.last_key != pygame.K_RIGHT: 
                    self._player_push(now)
                    self.last_key = pygame.K_RIGHT

    def update(self):
        if self.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()
        self._sync_ai_phase(now)

        ai_variance = random.uniform(0.3, 1.0)
        self.arm_position += self.ai_strength * AI_STRENGTH_MULT[self.ai_phase] * ai_variance

        if self.stamina < self.max_stamina:
            regen = STAMINA_REGEN * (COUNTER_REGEN_MULT if self.counter_active(now) else 1.0)
            self.stamina = min(self.max_stamina, self.stamina + regen)

        if self.arm_position <= -self.target_limit:
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"
        elif self.arm_position >= self.target_limit:
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    def reset(self):
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self._reset_cycle()

    def _reset_cycle(self):
        """Start-of-match state for the AI cycle (Task 2) and the counter-surge bonus (Task 4)."""
        self.ai_phase = AI_NORMAL
        self.phase_start = pygame.time.get_ticks()
        self.counter_until = 0
        self.counter_used = False

    def _sync_ai_phase(self, now):
        """Advance NORMAL -> SURGE -> COOLDOWN -> NORMAL from elapsed time (no frame counting)."""
        while now - self.phase_start >= AI_PHASE_MS[self.ai_phase]:
            self.phase_start += AI_PHASE_MS[self.ai_phase]
            self.ai_phase = AI_NEXT_PHASE[self.ai_phase]
            if self.ai_phase == AI_SURGE:
                self.counter_used = False  # every new surge offers one new counter opportunity

    def player_exhausted(self):
        return self.stamina <= STAMINA_MIN_TO_PUSH

    def counter_active(self, now):
        return now < self.counter_until

    def _in_counter_window(self, now):
        """True only shortly before the SURGE ends or shortly after COOLDOWN starts."""
        if self.ai_phase == AI_SURGE:
            return self.phase_start + AI_PHASE_MS[AI_SURGE] - now <= COUNTER_EARLY_MS
        if self.ai_phase == AI_COOLDOWN:
            return now - self.phase_start <= COUNTER_LATE_MS
        return False

    def _player_push(self, now):
        if not self.counter_used and self._in_counter_window(now):
            self.counter_used = True
            self.counter_until = now + COUNTER_BONUS_MS
        strength = PLAYER_PUSH * (COUNTER_PUSH_MULT if self.counter_active(now) else 1.0)
        self.arm_position -= strength  # negative = toward the player's side (Task 1 fix)
        self.stamina = max(0.0, self.stamina - PUSH_STAMINA_COST)

    def _draw_banner(self, screen, y, text, color):
        rect = pygame.Rect(40, y, self.width - 80, 34)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        label = self.font_med.render(text, True, (255, 255, 255))
        screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    def render(self, screen):
        screen.fill((25, 28, 35))

        title_surf = self.font_big.render("ARM WRESTLE SHOWDOWN", True, (240, 240, 240))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 12))

        player_header = self.font_med.render("PLAYER", True, (80, 160, 255))
        computer_header = self.font_med.render("COMPUTER", True, (255, 100, 80))
        screen.blit(player_header, (60, 55))
        screen.blit(computer_header, (self.width - 150, 55))
        if self.game_state == "PLAYING":
            phase_label = self.font_med.render(f"AI: {self.ai_phase}", True, AI_PHASE_COLORS[self.ai_phase])
            screen.blit(phase_label, (self.width - 150, 78))

        table_rect = pygame.Rect(40, 100, self.width - 80, 310)
        pygame.draw.rect(screen, (110, 50, 15), table_rect, border_radius=14)
        pygame.draw.rect(screen, (70, 30, 8), table_rect, width=5, border_radius=14)

        pygame.draw.line(screen, (45, 18, 4), (self.width // 2, 100), (self.width // 2, 410), 4)

        offset_x = (self.arm_position / self.target_limit) * 95
        hand_x = (self.width // 2) + int(offset_x)
        hand_y = 235

        p_shoulder = (70, 330)
        p_elbow = (140, 215)
        c_shoulder = (self.width - 70, 330)
        c_elbow = (self.width - 140, 215)

        pygame.draw.line(screen, (200, 145, 110), p_shoulder, p_elbow, 32)
        pygame.draw.line(screen, (215, 160, 125), p_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (185, 130, 95), p_elbow, 18)

        pygame.draw.line(screen, (170, 110, 85), c_shoulder, c_elbow, 32)
        pygame.draw.line(screen, (185, 125, 95), c_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (150, 95, 70), c_elbow, 18)

        pygame.draw.circle(screen, (225, 175, 140), (hand_x, hand_y), 24)
        pygame.draw.circle(screen, (160, 115, 85), (hand_x, hand_y), 24, width=3)

        stamina_label = self.font_med.render("STAMINA", True, (220, 220, 220))
        screen.blit(stamina_label, (40, 445))

        stamina_bg = pygame.Rect(140, 448, 240, 22)
        stamina_fill = pygame.Rect(140, 448, int(240 * (self.stamina / self.max_stamina)), 22)
        pygame.draw.rect(screen, (45, 50, 60), stamina_bg, border_radius=6)
        bar_color = (60, 210, 100) if self.stamina > 25 else (220, 60, 60)
        pygame.draw.rect(screen, bar_color, stamina_fill, border_radius=6)

        if self.game_state == "PLAYING":
            now = pygame.time.get_ticks()
            if self.ai_phase == AI_SURGE:
                self._draw_banner(screen, 490, "WARNING: AI SURGE!", (200, 40, 30))
            if self.player_exhausted():
                self._draw_banner(screen, 530, "PLAYER EXHAUSTED", (200, 120, 20))
            if self.counter_active(now):
                secs = (self.counter_until - now) / 1000
                self._draw_banner(
                    screen, 570,
                    f"COUNTER-SURGE! {COUNTER_PUSH_MULT:g}x PUSH + FAST RECOVERY  {secs:.1f}s",
                    (30, 150, 70))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            win_text = "PLAYER WINS THE MATCH!" if self.winner == "PLAYER" else "COMPUTER WINS!"
            color = (80, 240, 100) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 45)
            )

            restart_surf = self.font_med.render(
                "Press [R] to Rematch", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )
