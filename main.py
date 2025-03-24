import pygame
import numpy as np
import random
from classes.Dashboard import Dashboard
from classes.Level import Level
from classes.Menu import Menu
from classes.Sound import Sound
from entities.Mario import Mario

# Kích thước cửa sổ
windowSize = 640, 480

class MarioAI:
    """AI điều khiển Mario bằng thuật toán di truyền"""
    def __init__(self, gene_length=100):
        self.gene_length = gene_length
        self.genes = np.random.randint(0, 3, self.gene_length)  # 0: Không làm gì, 1: Nhảy, 2: Tiến lên
        self.fitness = 0  # Điểm số dựa trên khoảng cách đi được

    def mutate(self, mutation_rate=0.1):
        """Đột biến để tránh bị kẹt ở local optimum"""
        for i in range(len(self.genes)):
            if random.random() < mutation_rate:
                self.genes[i] = random.randint(0, 2)

    def crossover(self, other):
        """Lai ghép hai cá thể để tạo thế hệ mới"""
        crossover_point = random.randint(0, self.gene_length - 1)
        child = MarioAI(self.gene_length)
        child.genes[:crossover_point] = self.genes[:crossover_point]
        child.genes[crossover_point:] = other.genes[crossover_point:]
        return child

class GeneticAlgorithm:
    """Thuật toán di truyền để tối ưu hóa hành vi của Mario"""
    def __init__(self, population_size=20, gene_length=100):
        self.population_size = population_size
        self.gene_length = gene_length
        self.population = [MarioAI(self.gene_length) for _ in range(self.population_size)]

    def create_chromosome(self):
        """Tạo quần thể mới bằng elitism + crossover"""
        self.population.sort(key=lambda mario: mario.fitness, reverse=True)

        # Giữ lại 10% cá thể mạnh nhất (elitism)
        top_elite = self.population[:max(1, self.population_size // 100)]

        # Tạo thế hệ mới bằng lai ghép
        new_population = top_elite[:]
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(top_elite, 2)
            child = parent1.crossover(parent2)
            child.mutate()
            new_population.append(child)

        self.population = new_population

def main():
    """Hàm chính để chạy game với AI Mario sử dụng thuật toán di truyền"""
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    screen = pygame.display.set_mode(windowSize)
    max_frame_rate = 60

    # Tạo các đối tượng cần thiết
    dashboard = Dashboard("./img/font.png", 8, screen)
    sound = Sound()
    level = Level(screen, sound, dashboard)
    menu = Menu(screen, dashboard, level, sound)

    # Hiển thị menu
    while not menu.start:
        menu.update()

    # Khởi tạo thuật toán di truyền
    ga = GeneticAlgorithm(population_size=10, gene_length=500)

    for generation in range(10):  # Chạy qua 10 thế hệ
        print(f"🔄 Đang chạy thế hệ {generation + 1}...")

        for ai in ga.population:
            mario = Mario(0, 0, level, screen, dashboard, sound)
            mario.gravity = 1  # Thêm trọng lực để tránh bay lên trời
            mario.on_ground = False  # Ban đầu Mario chưa chạm đất
            clock = pygame.time.Clock()
            step = 0  # Vị trí trong chuỗi gene

            while not mario.restart:
                pygame.display.set_caption(f"Super Mario AI - Gen {generation+1}")

                if mario.pause:
                    mario.pauseObj.update()
                else:
                    level.drawLevel(mario.camera)
                    dashboard.update()

                    # Mario AI tự động điều khiển
                    if step < len(ai.genes):
                        action = ai.genes[step]

                        # Chỉ cho phép nhảy nếu đang chạm đất
                        if action == 1 and mario.on_ground:
                            mario.is_jumping = True
                            mario.on_ground = False
                        elif action == 2:
                            mario.rect.x += 5  # Di chuyển sang phải

                        step += 1

                    # Áp dụng trọng lực
                    mario.rect.y += mario.gravity
                    if mario.rect.y >= 400:  # Giả lập chạm đất (tọa độ 400)
                        mario.rect.y = 400
                        mario.on_ground = True

                    mario.update()

                pygame.display.update()
                clock.tick(max_frame_rate)

            # Cập nhật điểm số (fitness) dựa trên khoảng cách Mario di chuyển
            ai.fitness = mario.rect.x

        # Tiến hóa thế hệ mới
        ga.create_chromosome()

    print("✅ AI đã hoàn thành 10 thế hệ huấn luyện!")
    pygame.quit()

if __name__ == "__main__":
    main()