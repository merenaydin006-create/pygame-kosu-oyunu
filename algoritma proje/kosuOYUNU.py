"""
Koşan Adam Oyunu - Karakter Seçimi
4 şeritli yolda engellerden kaçın, özel güçlerinizi kullanın!
"""

import pygame
import random
import sys
import math

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
ORANGE = (255, 165, 0)
PURPLE = (200, 0, 255)
BROWN = (139, 69, 19)
SKIN = (255, 220, 177)
LIGHT_BLUE = (100, 200, 255)
CYAN = (0, 255, 255)

# Oyun ayarları
WIDTH = 800
HEIGHT = 600
FPS = 60

# Karakter ayarları
RUNNER_WIDTH = 40
RUNNER_HEIGHT = 60
RUNNER_SPEED = 5
ROAD_WIDTH = 500
LANE_COUNT = 4
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT

# Engeller ve güçler
OBSTACLE_SPEED = 4
POWERUP_SPAWN_RATE = 0.0067  # Her frame'de ~%0.67 şans (2/3 oranında azaltıldı)
OBSTACLE_SPAWN_RATE = 0.03  # Her frame'de %3 şans

# Zaman sabitleri (frame cinsinden, 60 FPS)
SHIELD_DURATION = 300  # 5 saniye
SHIELD_COOLDOWN = 1200  # 20 saniye
FLY_DURATION = 300  # 5 saniye
FLY_COOLDOWN = 1500  # 25 saniye
LIGHTNING_BOOST_DURATION = 300  # 5 saniye
SPEED_INCREASE_INTERVAL = 300  # 5 saniye
SPEED_INCREASE_MULTIPLIER = 1.2  # %20 artış

# Fizik sabitleri
JUMP_CLEAR_HEIGHT = -30  # Zıplama ile engelin üstünden geçme yüksekliği

# Karakter tipleri
CHAR_BLUE = "blue"  # Robot - Kalkan
CHAR_RED = "red"    # Kırmızı tişörtlü - Zıplama
CHAR_BIRD = "bird"  # Kuş - Uçma

# Parkur tipleri
TRACK_FOREST = "forest"  # Orman yolu (mevcut)
TRACK_SPACE = "space"    # Uzay

# Parkur renkleri
SPACE_BG = (10, 10, 30)  # Koyu mavi uzay arka planı
SPACE_STARS = (255, 255, 255)  # Yıldızlar
SPACE_PLANET = (150, 100, 200)  # Gezegen rengi
SPACE_ROAD = (40, 40, 60)  # Uzay yolu
SPACE_LANE = (100, 100, 150)  # Uzay şerit çizgileri


class Runner(pygame.sprite.Sprite):
    """Oyuncunun koşan karakteri"""
    def __init__(self, x, y, char_type=CHAR_BLUE):
        super().__init__()
        self.char_type = char_type
        self.image = pygame.Surface((RUNNER_WIDTH, RUNNER_HEIGHT), pygame.SRCALPHA)
        self.draw_character()
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.base_y = y  # Normal y pozisyonu
        self.speed = RUNNER_SPEED
        self.current_lane = 1  # 0-3 arası şerit
        self.target_lane = 1
        self.is_moving = False  # Şerit değiştirme sırasında
        
        # Özel güçler
        self.shield = False
        self.shield_time = 0
        self.shield_cooldown = 0  # Mavi karakter için
        
        self.jumping = False
        self.jump_height = 0
        self.jump_speed = 0
        
        self.flying = False
        self.fly_time = 0
        self.fly_cooldown = 0  # Kuş karakter için
        
        self.lightning_boost = False
        self.lightning_boost_time = 0
        self.base_speed_multiplier = 1.0  # Pasif hızlanma çarpanı
        self.speed_increase_timer = 0  # Her 5 saniyede bir artış için timer

    def draw_character(self):
        """Karakter tipine göre çiz"""
        if self.char_type == CHAR_BLUE:
            # Robot karakteri
            # Baş (metalik gri)
            pygame.draw.rect(self.image, (192, 192, 192), (8, 5, 24, 20))
            pygame.draw.rect(self.image, (128, 128, 128), (10, 7, 20, 16))
            # Gözler (LED - mavi)
            pygame.draw.circle(self.image, BLUE, (14, 15), 3)
            pygame.draw.circle(self.image, BLUE, (26, 15), 3)
            pygame.draw.circle(self.image, CYAN, (14, 15), 1)
            pygame.draw.circle(self.image, CYAN, (26, 15), 1)
            # Gövde (metalik)
            pygame.draw.rect(self.image, (160, 160, 160), (10, 25, 20, 25))
            pygame.draw.rect(self.image, (128, 128, 128), (12, 27, 16, 21))
            # Gövde detayları
            pygame.draw.line(self.image, (100, 100, 100), (15, 30), (25, 30), 2)
            pygame.draw.line(self.image, (100, 100, 100), (15, 40), (25, 40), 2)
            # Kollar (metalik)
            pygame.draw.rect(self.image, (192, 192, 192), (5, 28, 8, 15))
            pygame.draw.rect(self.image, (192, 192, 192), (27, 28, 8, 15))
            # Eklemler
            pygame.draw.circle(self.image, (100, 100, 100), (9, 28), 3)
            pygame.draw.circle(self.image, (100, 100, 100), (31, 28), 3)
            # Bacaklar (metalik)
            pygame.draw.rect(self.image, (160, 160, 160), (12, 50, 6, 10))
            pygame.draw.rect(self.image, (160, 160, 160), (22, 50, 6, 10))
            # Ayaklar (metalik)
            pygame.draw.rect(self.image, (128, 128, 128), (10, 58, 10, 4))
            pygame.draw.rect(self.image, (128, 128, 128), (20, 58, 10, 4))
        elif self.char_type == CHAR_RED:
            # Kırmızı tişörtlü
            pygame.draw.circle(self.image, SKIN, (RUNNER_WIDTH // 2, 15), 12)
            pygame.draw.rect(self.image, RED, (10, 25, 20, 25))
            pygame.draw.line(self.image, SKIN, (8, 28), (5, 40), 4)
            pygame.draw.line(self.image, SKIN, (32, 28), (35, 40), 4)
            pygame.draw.line(self.image, BROWN, (15, 50), (12, 60), 5)
            pygame.draw.line(self.image, BROWN, (25, 50), (28, 60), 5)
            pygame.draw.ellipse(self.image, BLACK, (8, 58, 8, 4))
            pygame.draw.ellipse(self.image, BLACK, (24, 58, 8, 4))
        elif self.char_type == CHAR_BIRD:
            # Kuş karakteri (daha detaylı)
            # Gövde (daha büyük ve oval)
            pygame.draw.ellipse(self.image, (255, 215, 0), (8, 22, 24, 28))
            # Gövde gölgesi
            pygame.draw.ellipse(self.image, (255, 200, 0), (10, 24, 20, 24))
            
            # Baş (daha büyük)
            pygame.draw.circle(self.image, (255, 215, 0), (RUNNER_WIDTH // 2, 18), 12)
            # Baş gölgesi
            pygame.draw.circle(self.image, (255, 200, 0), (RUNNER_WIDTH // 2 - 2, 18), 10)
            
            # Gaga (daha belirgin)
            pygame.draw.polygon(self.image, ORANGE, [
                (RUNNER_WIDTH // 2 + 10, 18), 
                (RUNNER_WIDTH // 2 + 18, 16), 
                (RUNNER_WIDTH // 2 + 18, 20)
            ])
            pygame.draw.polygon(self.image, (255, 140, 0), [
                (RUNNER_WIDTH // 2 + 10, 18), 
                (RUNNER_WIDTH // 2 + 16, 17), 
                (RUNNER_WIDTH // 2 + 16, 19)
            ])
            
            # Kanatlar (daha büyük ve detaylı)
            # Sol kanat
            pygame.draw.ellipse(self.image, (255, 165, 0), (3, 28, 18, 14))
            pygame.draw.ellipse(self.image, (255, 140, 0), (5, 30, 14, 10))
            # Sağ kanat
            pygame.draw.ellipse(self.image, (255, 165, 0), (19, 28, 18, 14))
            pygame.draw.ellipse(self.image, (255, 140, 0), (21, 30, 14, 10))
            
            # Kuyruk
            pygame.draw.polygon(self.image, (255, 200, 0), [
                (RUNNER_WIDTH // 2, 45),
                (RUNNER_WIDTH // 2 - 5, 55),
                (RUNNER_WIDTH // 2 + 5, 55)
            ])
            
            # Göz (daha büyük)
            pygame.draw.circle(self.image, WHITE, (RUNNER_WIDTH // 2 + 4, 16), 4)
            pygame.draw.circle(self.image, BLACK, (RUNNER_WIDTH // 2 + 5, 16), 2)
            pygame.draw.circle(self.image, WHITE, (RUNNER_WIDTH // 2 + 6, 15), 1)
            
            # Ayaklar
            pygame.draw.line(self.image, ORANGE, (RUNNER_WIDTH // 2 - 3, 50), (RUNNER_WIDTH // 2 - 3, 55), 2)
            pygame.draw.line(self.image, ORANGE, (RUNNER_WIDTH // 2 + 3, 50), (RUNNER_WIDTH // 2 + 3, 55), 2)

    def handle_e_press(self):
        """E tuşuna basıldığında özel gücü kullan"""
        if self.char_type == CHAR_BLUE:
            # Mavi: Kalkan (20 saniyede bir)
            if self.shield_cooldown <= 0 and not self.shield:
                self.activate_shield()
        elif self.char_type == CHAR_RED:
            # Kırmızı: Zıplama
            if not self.jumping:
                self.jump()
        elif self.char_type == CHAR_BIRD:
            # Kuş: Uçma (25 saniyede bir)
            if self.fly_cooldown <= 0 and not self.flying:
                self.activate_fly()

    def change_lane_left(self):
        """Sol şeride geç (event-based)"""
        if not self.is_moving and self.target_lane > 0:
            self.target_lane -= 1
            self.is_moving = True

    def change_lane_right(self):
        """Sağ şeride geç (event-based)"""
        if not self.is_moving and self.target_lane < LANE_COUNT - 1:
            self.target_lane += 1
            self.is_moving = True

    def jump(self):
        """Zıplama gücü (kırmızı karakter)"""
        if not self.jumping:
            INITIAL_JUMP_SPEED = -12
            self.jumping = True
            self.jump_speed = INITIAL_JUMP_SPEED
            self.jump_height = 0

    def activate_shield(self):
        """Kalkanı aktif et (mavi karakter - 20 saniyede bir)"""
        self.shield = True
        self.shield_time = SHIELD_DURATION
        self.shield_cooldown = SHIELD_COOLDOWN

    def activate_fly(self):
        """Uçma gücü (kuş karakter - 25 saniyede bir)"""
        self.flying = True
        self.fly_time = FLY_DURATION
        self.fly_cooldown = FLY_COOLDOWN

    def update(self):
        """Karakter hareketi - şeritler arası (sadece yolda)"""
        road_left = WIDTH // 2 - ROAD_WIDTH // 2
        target_x = road_left + (self.target_lane * LANE_WIDTH) + (LANE_WIDTH // 2) - (RUNNER_WIDTH // 2)
        
        # Şerit merkezine yumuşak geçiş
        LANE_SWITCH_THRESHOLD = 2
        if abs(self.rect.x - target_x) > LANE_SWITCH_THRESHOLD:
            self.is_moving = True
            if self.rect.x < target_x:
                self.rect.x += min(self.speed, target_x - self.rect.x)
            else:
                self.rect.x -= min(self.speed, self.rect.x - target_x)
        else:
            self.rect.x = target_x
            self.current_lane = self.target_lane
            self.is_moving = False
        
        # Zıplama mekaniği (kırmızı karakter)
        if self.jumping:
            GRAVITY = 0.6
            self.jump_height += self.jump_speed
            self.jump_speed += GRAVITY
            self.rect.y = self.base_y + self.jump_height
            
            if self.jump_height >= 0:  # Yere döndü
                self.jumping = False
                self.jump_height = 0
                self.rect.y = self.base_y
        
        # Uçma mekaniği (kuş karakter)
        FLY_HEIGHT_OFFSET = 50
        if self.flying:
            self.rect.y = self.base_y - FLY_HEIGHT_OFFSET
        elif not self.flying and self.char_type == CHAR_BIRD:
            # Uçma bittiğinde yere dön
            LANDING_SPEED = 2
            if self.rect.y < self.base_y:
                self.rect.y = min(self.base_y, self.rect.y + LANDING_SPEED)
        
        # Cooldown'ları güncelle
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        if self.fly_cooldown > 0:
            self.fly_cooldown -= 1
        
        # Pasif hızlanma - her 5 saniyede %20 artış
        self.speed_increase_timer += 1
        if self.speed_increase_timer >= SPEED_INCREASE_INTERVAL:
            self.base_speed_multiplier *= SPEED_INCREASE_MULTIPLIER
            self.speed_increase_timer = 0

    def draw_shield(self, screen):
        """Kalkan efekti çiz"""
        if self.shield:
            SHIELD_OUTER_RADIUS = RUNNER_WIDTH // 2 + 15
            SHIELD_INNER_RADIUS = RUNNER_WIDTH // 2 + 10
            SHIELD_OUTER_COLOR = BLUE
            SHIELD_INNER_COLOR = (100, 150, 255)
            pygame.draw.circle(screen, SHIELD_OUTER_COLOR, self.rect.center, SHIELD_OUTER_RADIUS, 4)
            pygame.draw.circle(screen, SHIELD_INNER_COLOR, self.rect.center, SHIELD_INNER_RADIUS, 2)
    
    def draw_fly_effect(self, screen):
        """Uçma efekti çiz (kuş)"""
        if self.flying:
            # Kanat çırpma efekti
            WING_LINE_COUNT = 3
            WING_OFFSET_STEP = 3
            WING_BASE_OFFSET = 10
            WING_EXTEND_OFFSET = 20
            WING_VERTICAL_OFFSET = 10
            WING_LINE_WIDTH = 2
            
            for i in range(WING_LINE_COUNT):
                offset = (i - 1) * WING_OFFSET_STEP
                pygame.draw.line(screen, CYAN, 
                               (self.rect.centerx - WING_BASE_OFFSET, self.rect.centery + offset),
                               (self.rect.centerx - WING_EXTEND_OFFSET, self.rect.centery - WING_VERTICAL_OFFSET + offset), 
                               WING_LINE_WIDTH)
                pygame.draw.line(screen, CYAN,
                               (self.rect.centerx + WING_BASE_OFFSET, self.rect.centery + offset),
                               (self.rect.centerx + WING_EXTEND_OFFSET, self.rect.centery - WING_VERTICAL_OFFSET + offset), 
                               WING_LINE_WIDTH)


class Obstacle(pygame.sprite.Sprite):
    """Yoldaki engel - Çalılık, Kaya veya Obruk"""
    def __init__(self, x, obstacle_type=None, track_type=TRACK_FOREST):
        super().__init__()
        # Parkur tipine göre engel tipi belirle
        if obstacle_type:
            self.obstacle_type = obstacle_type
        elif track_type == TRACK_SPACE:
            # Uzay parkurunda obruk veya kaya
            self.obstacle_type = random.choice(['pit', 'rock'])
        else:
            # Diğer parkurlarda çalılık veya kaya
            self.obstacle_type = random.choice(['bush', 'rock'])
        
        self.size = random.randint(45, 65)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if self.obstacle_type == 'bush':
            # Çalılık çizimi
            # Ana gövde (yeşil)
            pygame.draw.ellipse(self.image, (34, 139, 34), (5, self.size - 30, self.size - 10, 25))
            # Yapraklar (farklı tonlarda yeşil)
            for i in range(5):
                leaf_x = random.randint(5, self.size - 15)
                leaf_y = random.randint(5, self.size - 20)
                leaf_size = random.randint(8, 15)
                leaf_color = random.choice([(34, 139, 34), (0, 128, 0), (50, 205, 50)])
                pygame.draw.circle(self.image, leaf_color, (leaf_x, leaf_y), leaf_size)
            # Küçük dallar
            for i in range(3):
                branch_x = random.randint(10, self.size - 10)
                branch_y = random.randint(self.size - 25, self.size - 10)
                pygame.draw.line(self.image, (101, 67, 33), (branch_x, branch_y), 
                               (branch_x + random.randint(-5, 5), branch_y + random.randint(5, 10)), 2)
        elif self.obstacle_type == 'rock':
            # Kaya çizimi
            # Ana kaya gövdesi (gri tonları)
            rock_color = random.choice([(105, 105, 105), (128, 128, 128), (169, 169, 169)])
            pygame.draw.ellipse(self.image, rock_color, (2, 2, self.size - 4, self.size - 4))
            # Kaya detayları (gölgeler)
            pygame.draw.ellipse(self.image, (64, 64, 64), (5, 5, self.size - 15, self.size - 15))
            pygame.draw.ellipse(self.image, (192, 192, 192), (self.size - 15, self.size - 15, 10, 10))
            # Çatlaklar
            for i in range(2):
                crack_x = random.randint(5, self.size - 5)
                pygame.draw.line(self.image, (64, 64, 64), (crack_x, 5), (crack_x + random.randint(-3, 3), self.size - 5), 1)
        elif self.obstacle_type == 'pit':
            # Obruk çizimi (uzay parkuru için)
            # Obruk genişliği (daha geniş)
            pit_width = self.size
            pit_height = self.size // 2
            
            # Dış kenar (koyu siyah - uzay boşluğu)
            pygame.draw.ellipse(self.image, (0, 0, 0), (0, self.size - pit_height, pit_width, pit_height))
            # İç kısım (daha koyu)
            pygame.draw.ellipse(self.image, (10, 10, 20), (5, self.size - pit_height + 5, pit_width - 10, pit_height - 10))
            # Derinlik efekti (iç çember)
            pygame.draw.ellipse(self.image, (5, 5, 15), (10, self.size - pit_height + 10, pit_width - 20, pit_height - 20))
            # Yıldızlar (obruk içinde) - güvenli aralık kontrolü
            star_x_min = max(10, 0)
            star_x_max = max(pit_width - 10, star_x_min + 1)
            # Obruk içindeki y yarımı için pozisyonlar
            pit_top = self.size - pit_height
            star_y_min = max(pit_top + 5, 5)
            star_y_max = max(self.size - 5, star_y_min + 1)
            
            # Sadece geçerli aralık varsa yıldız çiz
            if star_x_max > star_x_min and star_y_max > star_y_min:
                num_stars = min(3, pit_width // 10)  # Boyuta göre yıldız sayısı
                for i in range(num_stars):
                    star_x = random.randint(star_x_min, star_x_max)
                    star_y = random.randint(star_y_min, star_y_max)
                    pygame.draw.circle(self.image, (255, 255, 255), (star_x, star_y), 1)
            # Kenar vurgusu (parlaklık)
            pygame.draw.ellipse(self.image, (50, 50, 70), (0, self.size - pit_height, pit_width, pit_height), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -self.size
        self.speed = OBSTACLE_SPEED

    def update(self):
        """Engel aşağı hareket eder"""
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    """Güç toplama objesi"""
    def __init__(self, x, power_type):
        super().__init__()
        self.power_type = power_type  # 'lightning' veya 'shield'
        if power_type == 'lightning':
            self.size = 60  # Yıldırım 2 katı büyük
        else:
            self.size = 30
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if power_type == 'lightning':
            # Yıldırım - elektrik efekti (2 katı büyük)
            # Ana yıldırım şekli
            points = [
                (self.size//2, 10),
                (self.size//2 + 10, 24),
                (self.size//2 - 6, 24),
                (self.size//2 + 6, 40),
                (self.size//2 - 10, 40),
                (self.size//2, 50)
            ]
            pygame.draw.polygon(self.image, YELLOW, points)
            # Parlama efekti
            pygame.draw.polygon(self.image, WHITE, [
                (self.size//2, 16),
                (self.size//2 + 6, 26),
                (self.size//2 - 4, 26),
                (self.size//2 + 4, 38),
                (self.size//2 - 6, 38),
                (self.size//2, 46)
            ])
        else:  # shield
            # Kalkan - mavi kalkan
            pygame.draw.circle(self.image, BLUE, (self.size//2, self.size//2), self.size//2)
            pygame.draw.circle(self.image, WHITE, (self.size//2, self.size//2), self.size//2 - 3)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -self.size
        self.speed = OBSTACLE_SPEED

    def update(self):
        """Güç aşağı hareket eder"""
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Koşan Adam - 4 Şeritli Yol!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        self.selected_char = None
        self.selected_track = TRACK_FOREST  # Varsayılan parkur
        # Önce isim girişi, sonra karakter seçimi, sonra parkur seçimi gösterilecek
        self.show_name_input = True
        self.show_char_select = False
        self.show_track_select = False
        # Oyuncu takma adı ve skor dosyası yolu
        self.nickname = ""
        self.score_file = "scores.txt"
        # En yüksek skor bilgisi
        self.high_score = 0
        self.high_score_name = ""
        self.new_record = False
        # İsim girişi için geçici metin
        self.name_input_text = ""
        # Kayıtlı en yüksek skoru dosyadan yükle
        self.load_high_score()

    def load_high_score(self):
        """Dosyadan en yüksek skoru yükle"""
        try:
            with open(self.score_file, "r", encoding="utf-8") as f:
                best = 0
                best_name = ""
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Beklenen format: isim: skor
                    parts = line.rsplit(":", 1)
                    if len(parts) != 2:
                        continue
                    try:
                        score_val = int(parts[1].strip())
                        if score_val > best:
                            best = score_val
                            best_name = parts[0].strip()
                    except ValueError:
                        continue
                self.high_score = best
                self.high_score_name = best_name
        except FileNotFoundError:
            # Dosya yoksa sorun değil, 0'dan başla
            self.high_score = 0
            self.high_score_name = ""

    def save_score(self):
        """Skoru dosyaya kaydet"""
        try:
            with open(self.score_file, "a", encoding="utf-8") as f:
                f.write(f"{self.nickname}: {self.score}\n")
            # Kayıttan sonra da high score'u güncelle
            if self.score > self.high_score:
                self.high_score = self.score
                self.high_score_name = self.nickname
        except Exception as e:
            # Dosyaya yazılamazsa en azından konsola bilgi ver
            print("Skor dosyaya yazılırken hata oluştu:", e)

    def get_score_speed_multiplier(self):
        """Skor tabanlı hız çarpanı hesapla - her 1000 skor için %10 artış"""
        SCORE_MULTIPLIER_BASE = 1000
        SCORE_MULTIPLIER_RATE = 0.1
        return 1.0 + (self.score / SCORE_MULTIPLIER_BASE) * SCORE_MULTIPLIER_RATE
    
    def reset_game(self, char_type=CHAR_BLUE, track_type=TRACK_FOREST):
        """Oyunu sıfırla"""
        self.score = 0
        self.game_over = False
        self.new_record = False
        self.road_offset = 0
        self.selected_track = track_type
        # Gezegen sistemi için yenilenme kontrolü (20 saniyede bir)
        self.solar_system_reset_timer = 0
        self.solar_system_reset_interval = 1200  # 20 saniye @ 60 FPS = 1200 frame
        self.solar_system_last_reset_frame = 0
        self.solar_system_reset_start_offset = 0
        
        # Sprite grupları
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Koşan karakter
        road_left = WIDTH // 2 - ROAD_WIDTH // 2
        start_x = road_left + (LANE_COUNT // 2 * LANE_WIDTH) + (LANE_WIDTH // 2) - (RUNNER_WIDTH // 2)
        base_y = HEIGHT - RUNNER_HEIGHT - 20
        self.runner = Runner(start_x, base_y, char_type)
        self.runner.base_y = base_y
        # Pasif hızlanma değişkenlerini sıfırla
        self.runner.base_speed_multiplier = 1.0
        self.runner.speed_increase_timer = 0
        self.all_sprites.add(self.runner)

    def spawn_obstacle(self):
        """Rastgele şeritte engel oluştur (parkur tipine göre)"""
        road_left = WIDTH // 2 - ROAD_WIDTH // 2
        lane = random.randint(0, LANE_COUNT - 1)
        x = road_left + (lane * LANE_WIDTH) + (LANE_WIDTH // 2) - 20
        obstacle = Obstacle(x, track_type=self.selected_track)
        self.obstacles.add(obstacle)
        self.all_sprites.add(obstacle)

    def spawn_powerup(self):
        """Rastgele şeritte güç oluştur"""
        road_left = WIDTH // 2 - ROAD_WIDTH // 2
        lane = random.randint(0, LANE_COUNT - 1)
        # Yıldırım 60x60 olduğu için merkezleme farklı
        x = road_left + (lane * LANE_WIDTH) + (LANE_WIDTH // 2) - 30
        power_type = 'lightning'  # Sadece yıldırım (hızlanma) gücü
        powerup = PowerUp(x, power_type)
        self.powerups.add(powerup)
        self.all_sprites.add(powerup)

    def draw_road(self):
        """Parkur tipine göre 4 şeritli yolu çiz"""
        if self.selected_track == TRACK_FOREST:
            self.draw_forest_road()
        elif self.selected_track == TRACK_SPACE:
            self.draw_space_road()
    
    def draw_forest_road(self):
        """Orman yolu - kenarlarda ağaçlar"""
        road_x = WIDTH // 2 - ROAD_WIDTH // 2
        
        # Çimen arka planı
        pygame.draw.rect(self.screen, GREEN, (0, 0, WIDTH, HEIGHT))
        
        # Yol arka planı
        pygame.draw.rect(self.screen, DARK_GRAY, (road_x, 0, ROAD_WIDTH, HEIGHT))
        
        # Sol taraftaki ağaçlar (daha sola)
        tree_x_left = road_x - 60
        self.draw_trees(tree_x_left, True)
        
        # Sağ taraftaki ağaçlar (daha sağa)
        tree_x_right = road_x + ROAD_WIDTH + 60
        self.draw_trees(tree_x_right, False)
        
        # Şerit çizgileri (dikey)
        for i in range(1, LANE_COUNT):
            x = road_x + (i * LANE_WIDTH)
            pygame.draw.line(self.screen, YELLOW, (x, 0), (x, HEIGHT), 3)
        
        # Yol çizgileri (yatay - hareket eden)
        line_width = 4
        line_height = 40
        line_spacing = 60
        start_y = int((self.road_offset % line_spacing) - line_height)
        
        for y in range(start_y, HEIGHT, line_spacing):
            for lane in range(LANE_COUNT):
                lane_center_x = road_x + (lane * LANE_WIDTH) + (LANE_WIDTH // 2)
                pygame.draw.rect(self.screen, YELLOW, 
                               (lane_center_x - line_width // 2, y, line_width, line_height))
    
    def draw_space_road(self):
        """Uzay parkuru - yıldızlar ve gezegenler"""
        road_x = WIDTH // 2 - ROAD_WIDTH // 2
        
        # Uzay arka planı
        pygame.draw.rect(self.screen, SPACE_BG, (0, 0, WIDTH, HEIGHT))
        
        # Yıldızlar (dikey akan - yukarıdan aşağıya)
        star_speed = 0.6  # Daha yavaş (2'den 0.6'ya düşürüldü)
        star_spacing = 30
        star_y_offset = int(self.road_offset * star_speed) % star_spacing
        
        # Sabit yıldız pozisyonları (bir kez oluştur, sonra kullan)
        if not hasattr(self, '_space_star_positions'):
            self._space_star_positions = []
            for x in range(0, WIDTH, 25):
                for base_y in range(-star_spacing, HEIGHT + star_spacing * 2, star_spacing):
                    if random.random() < 0.4:  # %40 şansla yıldız
                        brightness = random.randint(150, 255)
                        self._space_star_positions.append((x, base_y, brightness))
        
        # Yıldızları çiz (dikey hareket)
        for star_x, base_y, brightness in self._space_star_positions:
            star_y = (base_y + star_y_offset) % (HEIGHT + star_spacing * 2) - star_spacing
            if 0 <= star_y <= HEIGHT:
                # Yıldız parıltısı efekti
                pygame.draw.circle(self.screen, (brightness, brightness, brightness), 
                                 (star_x, star_y), 1)
                # Bazı yıldızlar daha parlak
                if brightness > 200:
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                     (star_x, star_y), 0)
        
        # Sağ tarafta akan güneş sistemi objeleri
        solar_system_speed = 0.4  # Daha yavaş (1.5'ten 0.4'e düşürüldü)
        solar_system_spacing = 350  # Objeler arası mesafe
        
        # Güneş sistemi objelerini oluştur (bir kez)
        if not hasattr(self, '_solar_system_objects'):
            self._solar_system_objects = []
            # Sağ tarafta (yolun sağında) akan objeler - daha sağa
            system_x = road_x + ROAD_WIDTH + 80  # 30'dan 80'e çıkarıldı
            base_y = -200
            
            # Gerçek güneş sistemi objeleri (sırayla)
            planets = [
                {'name': 'sun', 'size': 32, 'color': YELLOW, 'glow_color': ORANGE, 'has_ring': False},
                {'name': 'mercury', 'size': 8, 'color': (150, 150, 150), 'glow_color': None, 'has_ring': False},
                {'name': 'venus', 'size': 12, 'color': (255, 240, 200), 'glow_color': None, 'has_ring': False},
                {'name': 'earth', 'size': 14, 'color': (100, 150, 255), 'glow_color': None, 'has_ring': False},
                {'name': 'moon', 'size': 6, 'color': (180, 180, 180), 'glow_color': None, 'has_ring': False},
                {'name': 'mars', 'size': 11, 'color': (200, 80, 80), 'glow_color': None, 'has_ring': False},
                {'name': 'jupiter', 'size': 24, 'color': (220, 180, 120), 'glow_color': None, 'has_ring': False, 'stripes': True},
                {'name': 'saturn', 'size': 20, 'color': (255, 230, 180), 'glow_color': None, 'has_ring': True},
                {'name': 'uranus', 'size': 16, 'color': (150, 220, 220), 'glow_color': None, 'has_ring': False},
                {'name': 'neptune', 'size': 15, 'color': (80, 120, 255), 'glow_color': None, 'has_ring': False},
            ]
            
            # Her gezegeni ekle
            for i, planet in enumerate(planets):
                obj_y = base_y - (i * solar_system_spacing)
                
                self._solar_system_objects.append({
                    'x': system_x + random.randint(-5, 5),
                    'base_y': obj_y,
                    'name': planet['name'],
                    'size': planet['size'],
                    'color': planet['color'],
                    'glow_color': planet.get('glow_color'),
                    'has_ring': planet.get('has_ring', False),
                    'stripes': planet.get('stripes', False)
                })
        
        # Güneş sistemi objelerini çiz (dikey akan)
        # Gezegenler bir kere akar, 20 saniye sonra yenilenir (döngüsel değil)
        current_solar_y_offset = int(self.road_offset * solar_system_speed)
        
        # Reset başlangıcını kontrol et (eğer yoksa oyun başlangıcı)
        if not hasattr(self, 'solar_system_reset_start_offset'):
            self.solar_system_reset_start_offset = current_solar_y_offset
        
        # 20 saniyede bir gezegenleri yenile
        frames_since_last_reset = self.score - self.solar_system_last_reset_frame
        if frames_since_last_reset >= self.solar_system_reset_interval:
            # Yenilenme zamanı - objeleri baştan başlat
            self.solar_system_last_reset_frame = self.score
            # Reset başlangıç offset'ini güncelle
            self.solar_system_reset_start_offset = current_solar_y_offset
            # Objeleri yeniden oluştur (yukarıdan başlasın)
            self._solar_system_objects = None
            delattr(self, '_solar_system_objects')
        
        # Reset başlangıcından bu yana geçen offset (döngüsel değil)
        solar_y_offset = current_solar_y_offset - self.solar_system_reset_start_offset
        
        # Objeleri çiz (eğer varsa)
        if hasattr(self, '_solar_system_objects') and self._solar_system_objects:
            for obj in self._solar_system_objects:
                # Modulo yok, sadece direkt offset ekle
                obj_y = obj['base_y'] + solar_y_offset
                
                if -100 <= obj_y <= HEIGHT + 100:  # Ekranın görünür alanında veya yakınında
                    planet_name = obj['name']
                    
                    if planet_name == 'sun':
                        # Güneş - parlayan
                        # Dış parıltı
                        for glow_size in range(obj['size'] + 15, obj['size'] + 5, -3):
                            alpha = max(0, 255 - (glow_size - obj['size']) * 20)
                            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                            pygame.draw.circle(glow_surface, (*obj['glow_color'], alpha // 3), 
                                             (glow_size, glow_size), glow_size)
                            self.screen.blit(glow_surface, 
                                           (obj['x'] - glow_size, obj_y - glow_size))
                        
                        # Ana güneş
                        pygame.draw.circle(self.screen, obj['color'], (obj['x'], obj_y), obj['size'])
                        # Güneş yüzeyi detayları
                        pygame.draw.circle(self.screen, ORANGE, (obj['x'] - 3, obj_y - 3), obj['size'] - 3)
                        pygame.draw.circle(self.screen, (255, 200, 0), (obj['x'] + 2, obj_y + 2), obj['size'] - 5)
                    
                    elif planet_name == 'jupiter':
                        # Jüpiter - çizgili
                        pygame.draw.circle(self.screen, obj['color'], (obj['x'], obj_y), obj['size'])
                        # Yatay çizgiler (Jüpiter'in karakteristik çizgileri)
                        for stripe_y in range(obj_y - obj['size'] + 3, obj_y + obj['size'] - 3, 4):
                            pygame.draw.line(self.screen, (200, 150, 100), 
                                           (obj['x'] - obj['size'] + 2, stripe_y),
                                           (obj['x'] + obj['size'] - 2, stripe_y), 1)
                        # Gölge
                        pygame.draw.circle(self.screen, 
                                         tuple(max(0, c - 30) for c in obj['color']), 
                                         (obj['x'] - 2, obj_y - 2), obj['size'] - 2)
                    
                    elif planet_name == 'saturn':
                        # Satürn - halkalı
                        pygame.draw.circle(self.screen, obj['color'], (obj['x'], obj_y), obj['size'])
                        # Gölge
                        pygame.draw.circle(self.screen, 
                                         tuple(max(0, c - 30) for c in obj['color']), 
                                         (obj['x'] - 2, obj_y - 2), obj['size'] - 2)
                        # Halkalar (Satürn'ün ünlü halkaları)
                        ring_width = obj['size'] + 8
                        pygame.draw.ellipse(self.screen, (200, 200, 200), 
                                          (obj['x'] - ring_width, obj_y - 4, 
                                           ring_width * 2, 8), 2)
                        pygame.draw.ellipse(self.screen, (180, 180, 180), 
                                          (obj['x'] - ring_width + 2, obj_y - 3, 
                                           (ring_width - 2) * 2, 6), 1)
                    
                    elif planet_name == 'earth':
                        # Dünya - mavi-yeşil
                        pygame.draw.circle(self.screen, obj['color'], (obj['x'], obj_y), obj['size'])
                        # Kıtalar (yeşil lekeler)
                        pygame.draw.circle(self.screen, (50, 150, 50), 
                                         (obj['x'] - 3, obj_y - 2), obj['size'] - 5)
                        pygame.draw.circle(self.screen, (50, 150, 50), 
                                         (obj['x'] + 2, obj_y + 1), obj['size'] - 6)
                        # Gölge
                        pygame.draw.circle(self.screen, (70, 120, 200), 
                                         (obj['x'] - 2, obj_y - 2), obj['size'] - 2)
                    
                    elif planet_name == 'moon':
                        # Ay - gri, kraterli
                        pygame.draw.circle(self.screen, obj['color'], (obj['x'], obj_y), obj['size'])
                        # Ay yüzeyi (kraterler)
                        pygame.draw.circle(self.screen, (150, 150, 150), 
                                         (obj['x'] - 2, obj_y - 1), obj['size'] - 2)
                        # Küçük kraterler
                        pygame.draw.circle(self.screen, (120, 120, 120), 
                                         (obj['x'] - 1, obj_y), 2)
                        pygame.draw.circle(self.screen, (120, 120, 120), 
                                         (obj['x'] + 2, obj_y + 1), 1)
                    
                    elif planet_name == 'mars':
                        # Mars - kırmızı
                        pygame.draw.circle(self.screen, obj['color'], (obj['x'], obj_y), obj['size'])
                        # Mars yüzeyi detayları
                        pygame.draw.circle(self.screen, (180, 60, 60), 
                                         (obj['x'] - 1, obj_y - 1), obj['size'] - 2)
                        # Gölge
                        pygame.draw.circle(self.screen, (150, 50, 50), 
                                         (obj['x'] - 2, obj_y - 2), obj['size'] - 2)
                    
                    else:
                        # Diğer gezegenler (Merkür, Venüs, Uranüs, Neptün)
                        pygame.draw.circle(self.screen, obj['color'], (obj['x'], obj_y), obj['size'])
                        # Gölge
                        pygame.draw.circle(self.screen, 
                                         tuple(max(0, c - 30) for c in obj['color']), 
                                         (obj['x'] - 2, obj_y - 2), obj['size'] - 2)
        
        # Koşulan alan - gezegen yüzeyi (yolun üzerine gezegen deseni)
        # Gezegen yüzeyi için gradient efekti
        planet_surface_colors = [
            (80, 60, 100),   # Koyu mor
            (100, 80, 120),  # Orta mor
            (120, 100, 140), # Açık mor
            (100, 80, 120),  # Orta mor
            (80, 60, 100)    # Koyu mor
        ]
        
        # Gezegen yüzeyi deseni (dikey çizgiler)
        for i, color in enumerate(planet_surface_colors):
            x_start = road_x + (i * ROAD_WIDTH // len(planet_surface_colors))
            x_end = road_x + ((i + 1) * ROAD_WIDTH // len(planet_surface_colors))
            pygame.draw.rect(self.screen, color, (x_start, 0, x_end - x_start, HEIGHT))
        
        # Uzay yolu kenarları (neon çerçeve)
        pygame.draw.rect(self.screen, CYAN, (road_x - 3, 0, 3, HEIGHT))
        pygame.draw.rect(self.screen, CYAN, (road_x + ROAD_WIDTH, 0, 3, HEIGHT))
        
        # Şerit çizgileri (dikey - neon mavi, parlayan)
        for i in range(1, LANE_COUNT):
            x = road_x + (i * LANE_WIDTH)
            # Ana çizgi
            pygame.draw.line(self.screen, SPACE_LANE, (x, 0), (x, HEIGHT), 3)
            # Parlama efekti (yan taraflar)
            pygame.draw.line(self.screen, CYAN, (x - 1, 0), (x - 1, HEIGHT), 1)
            pygame.draw.line(self.screen, CYAN, (x + 1, 0), (x + 1, HEIGHT), 1)
            # İç parıltı
            for glow_y in range(0, HEIGHT, 20):
                glow_intensity = int(255 * (0.3 + 0.2 * (glow_y % 40) / 40))
                pygame.draw.line(self.screen, (glow_intensity, glow_intensity, 255), 
                               (x, glow_y), (x, min(glow_y + 10, HEIGHT)), 1)
        
        # Yol çizgileri (yatay - hareket eden, neon)
        line_width = 4
        line_height = 40
        line_spacing = 60
        start_y = int((self.road_offset % line_spacing) - line_height)
        
        for y in range(start_y, HEIGHT, line_spacing):
            for lane in range(LANE_COUNT):
                lane_center_x = road_x + (lane * LANE_WIDTH) + (LANE_WIDTH // 2)
                # Ana çizgi
                pygame.draw.rect(self.screen, CYAN, 
                               (lane_center_x - line_width // 2, y, line_width, line_height))
                # Parlama efekti
                pygame.draw.rect(self.screen, WHITE, 
                               (lane_center_x - line_width // 2 + 1, y + 1, 
                                line_width - 2, line_height - 2))
                # Yan parıltı
                pygame.draw.rect(self.screen, (100, 200, 255), 
                               (lane_center_x - line_width // 2 - 1, y, 
                                1, line_height))
                pygame.draw.rect(self.screen, (100, 200, 255), 
                               (lane_center_x + line_width // 2, y, 
                                1, line_height))
    def draw_trees(self, x_pos, is_left):
        """Yolun kenarlarına ağaçlar çiz (büyük)"""
        tree_spacing = 100
        start_y = int((self.road_offset % tree_spacing) - 120)
        
        for y in range(start_y, HEIGHT + 120, tree_spacing):
            # Gövde (daha büyük)
            trunk_width = 18
            trunk_height = 60
            trunk_x = x_pos + (15 if is_left else -33)
            pygame.draw.rect(self.screen, BROWN, (trunk_x, y + 50, trunk_width, trunk_height))
            
            # Yapraklar (yeşil daireler - daha büyük)
            leaf_colors = [(34, 139, 34), (0, 100, 0), (50, 205, 50)]
            leaf_color = random.choice(leaf_colors)
            
            # Ana yaprak kümesi (büyük)
            pygame.draw.circle(self.screen, leaf_color, (trunk_x + trunk_width // 2, y + 40), 40)
            # Ek yapraklar (daha doğal görünüm - büyük)
            pygame.draw.circle(self.screen, (0, 128, 0), (trunk_x - 8, y + 35), 25)
            pygame.draw.circle(self.screen, (50, 205, 50), (trunk_x + trunk_width + 8, y + 35), 25)
            pygame.draw.circle(self.screen, leaf_color, (trunk_x + trunk_width // 2, y + 15), 30)
            # Üst yaprak kümesi
            pygame.draw.circle(self.screen, (34, 139, 34), (trunk_x + trunk_width // 2, y + 5), 20)

    def handle_collisions(self):
        """Çarpışmaları kontrol et"""
        # Engellerle çarpışma
        hits = pygame.sprite.spritecollide(self.runner, self.obstacles, False)
        if hits:
            # Kalkan varsa korunur, engel silinir
            if self.runner.shield:
                for hit in hits:
                    hit.kill()
            # Zıplama veya uçma sırasında engellerin üstünden geçer, engel silinir
            elif self.runner.jumping and self.runner.jump_height < JUMP_CLEAR_HEIGHT:
                for hit in hits:
                    hit.kill()
            elif self.runner.flying:
                for hit in hits:
                    hit.kill()
            else:
                # Oyun bitti, engelleri sil
                for hit in hits:
                    hit.kill()
                # Oyun bitti durumu ilk kez gerçekleşiyorsa skoru kaydet
                if not self.game_over:
                    self.game_over = True
                    # Yeni rekor mu?
                    if self.score > self.high_score:
                        self.new_record = True
                    self.save_score()
        
        # Güç toplama
        power_hits = pygame.sprite.spritecollide(self.runner, self.powerups, True)
        for power in power_hits:
            if power.power_type == 'lightning':
                # Yıldırım gücü - hızı 2x artırır
                self.runner.lightning_boost = True
                self.runner.lightning_boost_time = LIGHTNING_BOOST_DURATION

    def update_power_effects(self):
        """Güç efektlerini güncelle"""
        if self.runner.shield:
            self.runner.shield_time -= 1
            if self.runner.shield_time <= 0:
                self.runner.shield = False
        
        if self.runner.flying:
            self.runner.fly_time -= 1
            if self.runner.fly_time <= 0:
                self.runner.flying = False
                self.runner.rect.y = self.runner.base_y
        
        if self.runner.lightning_boost:
            self.runner.lightning_boost_time -= 1
            if self.runner.lightning_boost_time <= 0:
                self.runner.lightning_boost = False

    def draw_ui(self):
        """Arayüzü çiz"""
        # Skor
        score_text = self.font.render(f"Skor: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        # Takma ad (sağ üst)
        if self.nickname:
            name_text = self.small_font.render(f"İsim: {self.nickname}", True, WHITE)
            self.screen.blit(name_text, (WIDTH - 200, 10))
        
        # Özel güç durumları
        y_offset = 50
        
        if self.runner.char_type == CHAR_BLUE:
            # Mavi karakter - Kalkan
            if self.runner.shield:
                shield_text = self.small_font.render(f"🛡 Kalkan: {self.runner.shield_time // 60 + 1}s", True, BLUE)
                self.screen.blit(shield_text, (10, y_offset))
            elif self.runner.shield_cooldown > 0:
                cooldown = self.runner.shield_cooldown // 60 + 1
                shield_text = self.small_font.render(f"🛡 Kalkan: {cooldown}s bekle (E)", True, GRAY)
                self.screen.blit(shield_text, (10, y_offset))
            else:
                shield_text = self.small_font.render("🛡 Kalkan Hazır (E tuşu)", True, WHITE)
                self.screen.blit(shield_text, (10, y_offset))
            y_offset += 25
        
        elif self.runner.char_type == CHAR_RED:
            # Kırmızı karakter - Zıplama
            if self.runner.jumping:
                jump_text = self.small_font.render("⬆ Zıplıyor!", True, RED)
                self.screen.blit(jump_text, (10, y_offset))
            else:
                jump_text = self.small_font.render("⬆ Zıpla (E tuşu)", True, WHITE)
                self.screen.blit(jump_text, (10, y_offset))
            y_offset += 25
        
        elif self.runner.char_type == CHAR_BIRD:
            # Kuş karakter - Uçma
            if self.runner.flying:
                fly_text = self.small_font.render(f"🦅 Uçuyor: {self.runner.fly_time // 60 + 1}s", True, YELLOW)
                self.screen.blit(fly_text, (10, y_offset))
            elif self.runner.fly_cooldown > 0:
                cooldown = self.runner.fly_cooldown // 60 + 1
                fly_text = self.small_font.render(f"🦅 Uçma: {cooldown}s bekle (E)", True, GRAY)
                self.screen.blit(fly_text, (10, y_offset))
            else:
                fly_text = self.small_font.render("🦅 Uçma Hazır (E tuşu)", True, WHITE)
                self.screen.blit(fly_text, (10, y_offset))
            y_offset += 25
        
        if self.runner.lightning_boost:
            lightning_text = self.small_font.render(f"⚡ Hızlanma: {self.runner.lightning_boost_time // 60 + 1}s", True, YELLOW)
            self.screen.blit(lightning_text, (10, y_offset))

    def draw_character_select(self):
        """Karakter seçim ekranı"""
        self.screen.fill(DARK_GRAY)
        
        # Başlık
        title = self.title_font.render("KARAKTER SEÇİNİZ", True, WHITE)
        self.screen.blit(title, (WIDTH // 2 - 150, 50))
        
        # Karakter seçenekleri
        char_width = 150
        char_height = 200
        spacing = 50
        start_x = (WIDTH - (3 * char_width + 2 * spacing)) // 2
        
        chars = [
            (CHAR_BLUE, "Robot", "Kalkan Gücü", "20s cooldown"),
            (CHAR_RED, "Kırmızı Tişört", "Zıplama Gücü", "Engellerin üstünden atla"),
            (CHAR_BIRD, "Kuş", "Uçma Gücü", "5s uç, 25s cooldown")
        ]
        
        # Karakter görsellerini önceden oluştur (performans için)
        if not hasattr(self, '_char_previews'):
            self._char_previews = {}
            for char_type, _, _, _ in chars:
                temp_runner = Runner(0, 0, char_type)
                self._char_previews[char_type] = pygame.transform.scale(
                    temp_runner.image, (RUNNER_WIDTH * 2, RUNNER_HEIGHT * 2)
                )
        
        for i, (char_type, name, power, desc) in enumerate(chars):
            x = start_x + i * (char_width + spacing)
            y = 150
            
            # Karakter kutusu
            color = BLUE if char_type == CHAR_BLUE else (RED if char_type == CHAR_RED else YELLOW)
            pygame.draw.rect(self.screen, color, (x, y, char_width, char_height), 3)
            
            # Karakter çizimi (önceden oluşturulmuş)
            char_surface = self._char_previews[char_type]
            self.screen.blit(char_surface, (x + char_width // 2 - RUNNER_WIDTH, y + 20))
            
            # İsim
            name_text = self.small_font.render(name, True, WHITE)
            self.screen.blit(name_text, (x + 10, y + char_height - 60))
            
            # Güç açıklaması
            power_text = self.small_font.render(power, True, YELLOW)
            self.screen.blit(power_text, (x + 10, y + char_height - 40))
            
            desc_text = self.small_font.render(desc, True, GRAY)
            self.screen.blit(desc_text, (x + 10, y + char_height - 20))
            
            # Seçim tuşu
            key_text = self.font.render(f"{i+1}", True, WHITE)
            pygame.draw.circle(self.screen, color, (x + char_width // 2, y + char_height + 20), 20)
            self.screen.blit(key_text, (x + char_width // 2 - 8, y + char_height + 12))
        
        # Talimat
        instruction = self.small_font.render("1, 2 veya 3 tuşuna basarak karakter seçin", True, WHITE)
        self.screen.blit(instruction, (WIDTH // 2 - 150, HEIGHT - 50))

    def draw_track_select(self):
        """Parkur seçim ekranı"""
        self.screen.fill(DARK_GRAY)
        
        # Başlık
        title = self.title_font.render("PARKUR SEÇİNİZ", True, WHITE)
        self.screen.blit(title, (WIDTH // 2 - 140, 50))
        
        # Parkur seçenekleri
        track_width = 200
        track_height = 250
        spacing = 40
        start_x = (WIDTH - (2 * track_width + spacing)) // 2
        
        tracks = [
            (TRACK_FOREST, "Orman Yolu", "Doğal ortam", "Ağaçlar ve çimen"),
            (TRACK_SPACE, "Uzay", "Yıldızlar arası", "Gezegenler ve yıldızlar")
        ]
        
        for i, (track_type, name, desc1, desc2) in enumerate(tracks):
            x = start_x + i * (track_width + spacing)
            y = 120
            
            # Parkur kutusu
            if track_type == TRACK_FOREST:
                color = GREEN
            elif track_type == TRACK_SPACE:
                color = PURPLE
            else:
                color = RED
            
            pygame.draw.rect(self.screen, color, (x, y, track_width, track_height), 3)
            
            # Parkur önizlemesi (küçük görsel)
            preview_surface = pygame.Surface((track_width - 20, track_height - 80))
            if track_type == TRACK_FOREST:
                preview_surface.fill(GREEN)
                # Ağaç önizlemesi
                pygame.draw.rect(preview_surface, BROWN, (20, 60, 15, 40))
                pygame.draw.circle(preview_surface, (34, 139, 34), (27, 50), 25)
                # Yol
                pygame.draw.rect(preview_surface, DARK_GRAY, (60, 0, 100, track_height - 80))
                pygame.draw.line(preview_surface, YELLOW, (110, 0), (110, track_height - 80), 2)
            elif track_type == TRACK_SPACE:
                preview_surface.fill(SPACE_BG)
                # Yıldızlar (sabit desen)
                star_positions = [(15, 15), (45, 25), (75, 20), (105, 30), (135, 15), 
                                 (25, 50), (55, 55), (85, 60), (115, 50), (145, 55)]
                for star_x, star_y in star_positions:
                    pygame.draw.circle(preview_surface, WHITE, (star_x, star_y), 1)
                # Gezegen
                pygame.draw.circle(preview_surface, SPACE_PLANET, (track_width - 50, 30), 20)
                # Yol
                pygame.draw.rect(preview_surface, SPACE_ROAD, (60, 0, 100, track_height - 80))
                pygame.draw.line(preview_surface, CYAN, (110, 0), (110, track_height - 80), 2)
            
            self.screen.blit(preview_surface, (x + 10, y + 10))
            
            # İsim
            name_text = self.font.render(name, True, WHITE)
            self.screen.blit(name_text, (x + 10, y + track_height - 60))
            
            # Açıklama
            desc1_text = self.small_font.render(desc1, True, YELLOW)
            self.screen.blit(desc1_text, (x + 10, y + track_height - 40))
            
            desc2_text = self.small_font.render(desc2, True, GRAY)
            self.screen.blit(desc2_text, (x + 10, y + track_height - 20))
            
            # Seçim tuşu
            key_text = self.font.render(f"{i+1}", True, WHITE)
            pygame.draw.circle(self.screen, color, (x + track_width // 2, y + track_height + 20), 20)
            self.screen.blit(key_text, (x + track_width // 2 - 8, y + track_height + 12))
        
        # Talimat
        instruction = self.small_font.render("1 veya 2 tuşuna basarak parkur seçin", True, WHITE)
        self.screen.blit(instruction, (WIDTH // 2 - 140, HEIGHT - 50))

    def draw_name_input(self):
        """Takma ad giriş ekranı"""
        # Gökyüzü
        self.screen.fill(LIGHT_BLUE)

        # Güneş
        pygame.draw.circle(self.screen, YELLOW, (WIDTH - 100, 80), 40)
        for i in range(8):
            angle = i * (3.14159 / 4)
            x1 = WIDTH - 100 + int(55 * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            y1 = 80 + int(55 * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
            x2 = WIDTH - 100 + int(70 * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            y2 = 80 + int(70 * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
            pygame.draw.line(self.screen, YELLOW, (x1, y1), (x2, y2), 2)

        # Bulutlar (gökyüzünü boğmadan birkaç yumuşak bulut)
        def draw_cloud(center_x, center_y, scale=1.0):
            base_width = int(80 * scale)
            base_height = int(30 * scale)
            # Ana gövde
            pygame.draw.ellipse(self.screen, WHITE, (center_x - base_width // 2, center_y - base_height // 2, base_width, base_height))
            # Ek kabarcıklar
            pygame.draw.circle(self.screen, WHITE, (center_x - int(25 * scale), center_y - int(10 * scale)), int(18 * scale))
            pygame.draw.circle(self.screen, WHITE, (center_x, center_y - int(15 * scale)), int(20 * scale))
            pygame.draw.circle(self.screen, WHITE, (center_x + int(25 * scale), center_y - int(8 * scale)), int(17 * scale))

        draw_cloud(160, 120, 0.9)
        # Ortadaki bulutu biraz yukarı al ki takma ad yazısının üstüne gelmesin
        draw_cloud(360, 60, 1.1)
        draw_cloud(580, 130, 0.8)

        # Uzak dağlar (katmanlı ve gölgeli)
        mountain_base_color = (110, 170, 195)
        mountain_shadow_color = (90, 145, 170)

        # Sol dağ
        left_mountain = [(40, 360), (200, 140), (360, 360)]
        pygame.draw.polygon(self.screen, mountain_shadow_color, left_mountain)
        pygame.draw.polygon(self.screen, mountain_base_color, [(60, 360), (200, 155), (340, 360)])

        # Orta dağ
        mid_mountain = [(230, 390), (450, 150), (670, 390)]
        pygame.draw.polygon(self.screen, mountain_shadow_color, mid_mountain)
        pygame.draw.polygon(self.screen, mountain_base_color, [(250, 390), (450, 170), (650, 390)])

        # Sağ dağ
        right_mountain = [(480, 370), (700, 155), (920, 370)]
        pygame.draw.polygon(self.screen, mountain_shadow_color, right_mountain)
        pygame.draw.polygon(self.screen, mountain_base_color, [(500, 370), (700, 175), (900, 370)])

        # Dağ kar kaplı tepeler (daha detaylı, katmanlı)
        snow_color = (245, 252, 255)
        snow_shadow = (220, 235, 245)

        def draw_snow_cap(peak_x, peak_y, width, height):
            top = (peak_x, peak_y)
            left = (peak_x - width // 2, peak_y + height)
            right = (peak_x + width // 2, peak_y + height)
            mid_left = (peak_x - width // 4, peak_y + height // 2)
            mid_right = (peak_x + width // 4, peak_y + height // 2)
            # Ana kar üçgeni
            pygame.draw.polygon(self.screen, snow_color, [top, left, right])
            # Gölgeli kısmı
            pygame.draw.polygon(self.screen, snow_shadow, [top, mid_left, left])
            pygame.draw.polygon(self.screen, snow_shadow, [top, mid_right, right])
            # Küçük kar çıkıntıları
            pygame.draw.polygon(self.screen, snow_color, [mid_left, (mid_left[0] - 8, mid_left[1] + 8), (mid_left[0] + 4, mid_left[1] + 10)])
            pygame.draw.polygon(self.screen, snow_color, [mid_right, (mid_right[0] + 8, mid_right[1] + 8), (mid_right[0] - 4, mid_right[1] + 10)])

        draw_snow_cap(200, 145, 80, 45)
        draw_snow_cap(450, 160, 90, 50)
        draw_snow_cap(700, 165, 80, 45)

        # Çimen zemin
        grass_top = HEIGHT // 2 + 50
        pygame.draw.rect(self.screen, GREEN, (0, grass_top, WIDTH, HEIGHT - grass_top))

        # Çimenlerden geçen nehir
        river_color = (0, 140, 220)
        river_edge_color = (200, 230, 255)
        river_points = [
            (0, grass_top + 40),
            (150, grass_top + 60),
            (300, grass_top + 55),
            (450, grass_top + 75),
            (600, grass_top + 70),
            (800, grass_top + 90),
            (800, grass_top + 140),
            (600, grass_top + 120),
            (450, grass_top + 130),
            (300, grass_top + 110),
            (150, grass_top + 115),
            (0, grass_top + 95),
        ]
        pygame.draw.polygon(self.screen, river_color, river_points)
        # Nehir kenarlarına hafif parlama
        pygame.draw.lines(self.screen, river_edge_color, False, river_points[:6], 3)
        pygame.draw.lines(self.screen, river_edge_color, False, river_points[6:], 3)

        # Bazı ağaçlar
        def draw_tree(base_x):
            trunk_width = 18
            trunk_height = 50
            # Ağaç gövdesini nehirin hemen kıyısına, çimenlerin üzerine yerleştir
            trunk_y = grass_top + 5
            pygame.draw.rect(self.screen, BROWN, (base_x, trunk_y, trunk_width, trunk_height))
            pygame.draw.circle(self.screen, (34, 139, 34), (base_x + trunk_width // 2, trunk_y - 5), 30)
            pygame.draw.circle(self.screen, (0, 128, 0), (base_x + trunk_width // 2 - 20, trunk_y + 5), 25)
            pygame.draw.circle(self.screen, (50, 205, 50), (base_x + trunk_width // 2 + 20, trunk_y + 5), 25)

        for tx in [120, 260, 520, 660]:
            draw_tree(tx)

        # Başlık
        title = self.title_font.render("TAKMA AD GİRİN", True, WHITE)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 70))

        # Giriş kutusu
        box_width = 420
        box_height = 70
        box_x = WIDTH // 2 - box_width // 2
        box_y = HEIGHT // 2 - box_height // 2

        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height), 2)

        display_text = self.name_input_text if self.name_input_text else "İsminizi yazın..."
        color = WHITE if self.name_input_text else GRAY
        text_surface = self.font.render(display_text, True, color)
        self.screen.blit(text_surface, (box_x + 15, box_y + 18))

        tip = self.small_font.render("Boş bırakırsanız isim: Oyuncu", True, WHITE)
        tip_x = WIDTH // 2 - tip.get_width() // 2
        tip_y = box_y + box_height + 20
        self.screen.blit(tip, (tip_x, tip_y))

    def draw_game_over(self):
        """Oyun bitti ekranı"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("OYUN BİTTİ!", True, RED)
        score_text = self.font.render(f"Skorunuz: {self.score}", True, WHITE)
        if self.high_score > 0 and self.high_score_name:
            hs_label = f"En Yüksek Skor: {self.high_score} ({self.high_score_name})"
        elif self.high_score > 0:
            hs_label = f"En Yüksek Skor: {self.high_score}"
        else:
            hs_label = "En Yüksek Skor: -"
        high_score_text = self.small_font.render(hs_label, True, YELLOW)
        restart_text = self.small_font.render("Yeniden başlamak için R tuşuna basın", True, WHITE)
        quit_text = self.small_font.render("Çıkmak için ESC tuşuna basın", True, WHITE)

        # Temel yazılar
        self.screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 100))
        self.screen.blit(score_text, (WIDTH // 2 - 120, HEIGHT // 2 - 60))
        self.screen.blit(high_score_text, (WIDTH // 2 - 120, HEIGHT // 2 - 30))

        # Yeni rekor efekti
        if self.new_record:
            new_record_text = self.title_font.render("YENİ REKOR!", True, YELLOW)
            new_record_x = WIDTH // 2 - new_record_text.get_width() // 2
            self.screen.blit(new_record_text, (new_record_x, HEIGHT // 2 - 160))
        
        self.screen.blit(restart_text, (WIDTH // 2 - 180, HEIGHT // 2 + 20))
        self.screen.blit(quit_text, (WIDTH // 2 - 140, HEIGHT // 2 + 50))

    def run(self):
        """Ana oyun döngüsü"""
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    # Önce isim giriş ekranı
                    if self.show_name_input:
                        if event.key == pygame.K_RETURN:
                            # ENTER: ismi onayla
                            self.nickname = self.name_input_text.strip() or "Oyuncu"
                            self.show_name_input = False
                            self.show_char_select = True
                        elif event.key == pygame.K_BACKSPACE:
                            # BACKSPACE: son karakteri sil
                            self.name_input_text = self.name_input_text[:-1]
                        else:
                            # Yazılabilir karakterler
                            MAX_NAME_LENGTH = 16
                            if event.unicode.isprintable() and len(self.name_input_text) < MAX_NAME_LENGTH:
                                self.name_input_text += event.unicode

                    # İsim girildiyse karakter seçimi
                    elif self.show_char_select:
                        if event.key == pygame.K_1:
                            self.selected_char = CHAR_BLUE
                            self.show_char_select = False
                            self.show_track_select = True
                        elif event.key == pygame.K_2:
                            self.selected_char = CHAR_RED
                            self.show_char_select = False
                            self.show_track_select = True
                        elif event.key == pygame.K_3:
                            self.selected_char = CHAR_BIRD
                            self.show_char_select = False
                            self.show_track_select = True
                    
                    # Karakter seçildiyse parkur seçimi
                    elif self.show_track_select:
                        if event.key == pygame.K_1:
                            self.show_track_select = False
                            self.reset_game(self.selected_char, TRACK_FOREST)
                        elif event.key == pygame.K_2:
                            self.show_track_select = False
                            self.reset_game(self.selected_char, TRACK_SPACE)

                    # Oyun sırasında kontroller
                    else:
                        if event.key == pygame.K_r and self.game_over:
                            # Yeniden başlat: karakter seçimine dön
                            self.game_over = False
                            self.show_char_select = True
                            self.show_track_select = False
                        # E tuşu kontrolü (özel güç)
                        if event.key == pygame.K_e and not self.game_over:
                            self.runner.handle_e_press()
                        # Şerit değiştirme (sol/sağ)
                        if not self.game_over:
                            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                                self.runner.change_lane_left()
                            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                                self.runner.change_lane_right()
            
            # Çizim
            if self.show_name_input:
                # İsim girişi ekranı
                self.draw_name_input()
            elif self.show_char_select:
                # Karakter seçim ekranı
                self.draw_character_select()
            elif self.show_track_select:
                # Parkur seçim ekranı
                self.draw_track_select()
            else:
                if not self.game_over:
                    # Skor artır
                    self.score += 1
                    
                    # Skor tabanlı hız çarpanı
                    score_speed_mult = self.get_score_speed_multiplier()
                    
                    # Karakterin hızını güncelle (skor + yıldırım boost)
                    LIGHTNING_MULTIPLIER = 2.0
                    lightning_mult = LIGHTNING_MULTIPLIER if self.runner.lightning_boost else 1.0
                    self.runner.speed = RUNNER_SPEED * self.runner.base_speed_multiplier * lightning_mult * score_speed_mult
                    
                    # Yol animasyonu - yıldırım boost + skor çarpanı
                    game_speed_mult = lightning_mult * score_speed_mult
                    # Uzay parkurunda ve pause modundayken güneş sistemi offset'i dondurulur
                    # ama yıldızlar ve yol çizgileri hala hareket etmeli
                    # Bu yüzden road_offset her zaman artar, sadece draw_space_road'da
                    # pause kontrolü yapılır
                    self.road_offset += OBSTACLE_SPEED * game_speed_mult
                    
                    # Rastgele engel oluştur - yıldırım boost aktifken daha fazla engel (hız çarpanı kadar)
                    obstacle_spawn_rate = OBSTACLE_SPAWN_RATE * lightning_mult
                    if random.random() < obstacle_spawn_rate:
                        self.spawn_obstacle()
                    
                    # Rastgele güç oluştur
                    if random.random() < POWERUP_SPAWN_RATE:
                        self.spawn_powerup()
                    
                    # Engellerin ve güçlerin hızlarını güncelle (yıldırım boost + skor)
                    for obstacle in self.obstacles:
                        obstacle.speed = OBSTACLE_SPEED * game_speed_mult
                    for powerup in self.powerups:
                        powerup.speed = OBSTACLE_SPEED * game_speed_mult
                    
                    # Güncellemeler
                    self.runner.update()
                    self.obstacles.update()
                    self.powerups.update()
                    self.update_power_effects()
                    self.handle_collisions()
                
                # Çizim
                self.screen.fill(GREEN)  # Çimen
                self.draw_road()
                self.all_sprites.draw(self.screen)
                self.runner.draw_shield(self.screen)
                if self.runner.char_type == CHAR_BIRD:
                    self.runner.draw_fly_effect(self.screen)
                self.draw_ui()
                
                if self.game_over:
                    self.draw_game_over()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
