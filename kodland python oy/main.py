import pgzrun
import random
import math

WIDTH = 800
HEIGHT = 500
TITLE = "Ski Escape"

game_state = 'menu'
game_score = 0
player_lives = 3
game_level = 1
total_flags = 0
sound_enabled = True
music_started = False

snowflakes = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'speed': random.uniform(1, 2)} for _ in range(30)]

class Player(Actor):
    def __init__(self):
        super().__init__('hero_ski1', (WIDTH / 2, 100)) 
        self.move_speed = 4
        self.tick = 0
        self.moving = False

    def handle_movement(self):
        self.moving = False
        if keyboard.left and self.left > 0:
            self.x -= self.move_speed
            self.moving = True
        if keyboard.right and self.right < WIDTH:
            self.x += self.move_speed
            self.moving = True

        self.tick += 1
        if self.moving:
            if (self.tick // 15) % 2 == 0:
                self.image = 'hero_ski1'
            else:
                self.image = 'hero_ski2'
        else:
            if (self.tick // 40) % 2 == 0:
                self.image = 'hero_ski1'
            else:
                self.image = 'hero_ski2'

class Hazard(Actor):
    def __init__(self, type_name):
        self.kind = type_name
        self.sprite_timer = random.randint(0, 100)
        
        if self.kind == 'tree':
            super().__init__('tree', (random.randint(50, WIDTH - 50), random.randint(HEIGHT + 50, HEIGHT + 200)))
            self.start_speed = 1.5
        elif self.kind == 'snowman':
            self.frame_id = random.randint(1, 3)
            super().__init__(f'snowman{self.frame_id}', (random.randint(50, WIDTH - 50), random.randint(HEIGHT + 100, HEIGHT + 300)))
            self.start_speed = 2.0
            self.side_dir = 1
        elif self.kind == 'coin':
            super().__init__('coin', (random.randint(50, WIDTH - 50), random.randint(HEIGHT + 50, HEIGHT + 150)))
            self.start_speed = 1.8
            
        self.current_speed = self.start_speed

    def run_logic(self, lvl):
        diff_scale = 1.0 + (lvl - 1) * 0.15
        self.y -= self.current_speed * diff_scale
        
        self.sprite_timer += 1
        if self.kind == 'snowman':
            if self.sprite_timer % 25 == 0:
                self.frame_id = (self.frame_id % 3) + 1
                self.image = f'snowman{self.frame_id}'
                
            self.x += self.side_dir * 1.0 * diff_scale
            if self.x < 50 or self.x > WIDTH - 50:
                self.side_dir *= -1
                
        if self.y < -50:
            self.y = random.randint(HEIGHT + 50, HEIGHT + 250)
            self.x = random.randint(50, WIDTH - 50)

hero = Player()
entities = [Hazard('tree'), Hazard('snowman'), Hazard('snowman'), Hazard('coin')]

def on_mouse_down(pos):
    global game_state, sound_enabled, music_started
    if game_state == 'menu':
        if Rect((300, 200), (200, 50)).collidepoint(pos):
            game_state = 'game'
            if sound_enabled and not music_started:
                sounds.wind_ambience.set_volume(0.3)
                sounds.wind_ambience.play(loops=-1)
                music_started = True
        if Rect((300, 280), (200, 50)).collidepoint(pos):
            sound_enabled = not sound_enabled
            if not sound_enabled:
                sounds.wind_ambience.stop()
        if Rect((300, 360), (200, 50)).collidepoint(pos):
            exit()

def on_key_down(key):
    global game_state, game_score, player_lives, music_started, total_flags, game_level
    if key == keys.SPACE and game_state == 'gameover':
        if sound_enabled:
            sounds.gameover_sound.stop()
        game_score = 0
        player_lives = 3
        game_level = 1
        total_flags = 0
        music_started = False
        game_state = 'menu'

def update():
    global game_state, game_score, player_lives, music_started, total_flags, game_level
    
    if game_state == 'game':
        for f in snowflakes:
            f['y'] -= f['speed']
            if f['y'] < 0:
                f['y'] = HEIGHT
                f['x'] = random.randint(0, WIDTH)
                
        hero.handle_movement()
        game_score += 1
        
        for item in entities:
            item.run_logic(game_level)
            
            if hero.colliderect(item):
                if item.kind == 'coin':
                    if sound_enabled:
                        sounds.coin.set_volume(0.6)
                        sounds.coin.play()
                    game_score += 200
                    total_flags += 1
                    if total_flags % 3 == 0:
                        game_level += 1
                else:
                    if sound_enabled:
                        sounds.hit.set_volume(0.8)
                        sounds.hit.play()
                    player_lives -= 1
                
                item.y = random.randint(HEIGHT + 50, HEIGHT + 250)
                item.x = random.randint(50, WIDTH - 50)
                
                if player_lives <= 0:
                    game_state = 'gameover'
                    if sound_enabled:
                        sounds.wind_ambience.stop()
                        sounds.gameover_sound.set_volume(0.7)
                        sounds.gameover_sound.play()

def draw():
    screen.clear()
    
    if game_state == 'menu':
        screen.fill((20, 40, 80))
        screen.draw.text("SKI ESCAPE", center=(WIDTH/2, 100), fontsize=50, color="white")
        screen.draw.filled_rect(Rect((300, 200), (200, 50)), (50, 200, 50))
        screen.draw.text("PLAY", center=(WIDTH/2, 225), fontsize=30, color="white")
        screen.draw.filled_rect(Rect((300, 280), (200, 50)), (200, 150, 50))
        btn_text = "SOUND: ON" if sound_enabled else "SOUND: OFF"
        screen.draw.text(btn_text, center=(WIDTH/2, 305), fontsize=30, color="white")
        screen.draw.filled_rect(Rect((300, 360), (200, 50)), (200, 50, 50))
        screen.draw.text("EXIT", center=(WIDTH/2, 385), fontsize=30, color="white")

        screen.draw.text("Developed by Miyase Elif", (WIDTH - 250, HEIGHT - 40), fontsize=20, color="gray")
        
    elif game_state == 'game':
        screen.fill((240, 248, 255)) 
        for f in snowflakes:
            screen.draw.filled_circle((f['x'], f['y']), 2, (255, 255, 255))
        
        screen.draw.line((0, 60), (WIDTH, 60), (200, 200, 200))
        screen.draw.line((0, HEIGHT - 40), (WIDTH, HEIGHT - 40), (200, 200, 200))
        screen.draw.text(f"Score: {game_score}", (20, 20), fontsize=26, color="black")
        screen.draw.text(f"Level: {game_level}", (350, 20), fontsize=26, color="blue")
        screen.draw.text(f"Lives: {player_lives}", (650, 20), fontsize=26, color="red")
        
        hero.draw()
        for item in entities:
            item.draw()

    elif game_state == 'gameover':
        screen.fill((50, 10, 10))
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2 - 50), fontsize=60, color="red")
        screen.draw.text(f"Final Score: {game_score}", center=(WIDTH/2, HEIGHT/2 + 10), fontsize=30, color="white")
        screen.draw.text(f"Max Level: {game_level}", center=(WIDTH/2, HEIGHT/2 + 50), fontsize=25, color="gold")
        screen.draw.text("Press SPACE to return Menu", center=(WIDTH/2, HEIGHT/2 + 100), fontsize=20, color="gray")

pgzrun.go()