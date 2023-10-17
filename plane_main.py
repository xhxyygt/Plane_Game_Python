import sys
import pygame

pygame.init()
from plane_sprites import *

GAME_ACTIVE = False #写成全局变量的意义是方便在结束界面更改（结束界面按重新开始不要再次显示开始界面）

class PlaneGame(object):
    """飞机大战主游戏"""

    def __init__(self):
        print("游戏初始化")
        

        # 1. 创建游戏的窗口
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        # 创建开始和结束界面
        self.canvas_start = CanvasStart(self.screen)
        self.canvas_over = CanvasOver(self.screen)
        # 2. 创建游戏的时钟
        self.clock = pygame.time.Clock()
        # 3. 调用私有方法，精灵和精灵组的创建
        self.__create_sprites()
        # 分数对象
        self.score = GameScore()
        # 程序控制指针
        self.index = 0
        # 游戏是否开始
        # self.game_active = False 
        # 音乐bgm
        self.bg_music = pygame.mixer.Sound("./music/game_music.ogg")
        self.bg_music.set_volume(0.5)
        self.bg_music.play(-1)
        # 游戏结束了吗
        self.game_over = False
        # 4. 设置定时器事件 - 创建敌机　1s
        pygame.time.set_timer(CREATE_ENEMY_EVENT, random.randint(1000, 2000))
        pygame.time.set_timer(HERO_FIRE_EVENT, 400)
        pygame.time.set_timer(BUFF1_SHOW_UP, random.randint(3000, 5000))
        # pygame.time.set_timer(BUFF2_SHOW_UP, random.randint(20000, 40000))
        pygame.time.set_timer(BUFF2_SHOW_UP, random.randint(5000, 10000))
        pygame.time.set_timer(ENEMY_FIRE_EVENT, 2000)
        # 5. record用于记录用户最高得分
        self.recorded = False

    def __create_sprites(self):

        # 创建背景精灵和精灵组
        bg1 = Background()
        bg2 = Background(True)

        self.back_group = pygame.sprite.Group(bg1, bg2)

        # 创建敌机的精灵组

        self.enemy_group = pygame.sprite.Group()

        # 创建英雄的精灵和精灵组
        self.hero = Hero()
        self.hero_group = pygame.sprite.Group(self.hero)

        # 创建敌军子弹组
        self.enemy_bullet_group = pygame.sprite.Group()

        # 血条列表
        self.bars = []
        self.bars.append(self.hero.bar)

        # 创建buff组
        self.buff1_group = pygame.sprite.Group()

        # 创建假象boom组
        self.enemy_boom = pygame.sprite.Group()

        # bomb列表
        self.bombs = []

    def start_game(self):
        print("游戏开始...")

        while True:
            global GAME_ACTIVE
            if GAME_ACTIVE == True:
            # if self.game_active == True: #游戏开始时才进行事件和碰撞检测

                # 2. 事件监听
                self.__event_handler()
                # 3. 碰撞检测
                self.__check_collide()

            self._check_events()
            # 1. 设置刷新帧率
            self.clock.tick(FRAME_PER_SEC)
            # 4. 更新/绘制精灵组
            self.__update_sprites()

            # 5. 更新显示
            pygame.display.update()

    def _check_events(self): # 开始界面事件检测
        for event in pygame.event.get():
            global GAME_ACTIVE
            if GAME_ACTIVE == False:
            # if self.game_active == False:
                flag = self.canvas_start.event_handler(event)
                if flag == 1:
                    GAME_ACTIVE = True
                    # self.game_active = True
                elif flag == 2:
                    pygame.quit()
                    sys.exit()

    def __event_handler(self):  # 事件检测

        # 出现Boss的时机（200.700...）
        # if self.score.getvalue() > 200+500*self.index:
        if self.score.getvalue() > 50+350*self.index:
            self.boss = Boss()
            self.enemy_group.add(self.boss)
            self.bars.append(self.boss.bar)
            self.index += 1

        for event in pygame.event.get():
            # 判断是否退出游戏
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == CREATE_ENEMY_EVENT:
                # 创建敌机精灵将敌机精灵添加到敌机精灵组
                if self.score.getvalue() < 20:
                    enemy = Enemy()
                else:
                    if random.randint(0, 100) % 4:
                        enemy = Enemy()
                    else:
                        enemy = Enemy(2)

                self.enemy_group.add(enemy)
                self.bars.append(enemy.bar)

            elif event.type == HERO_FIRE_EVENT:
                for hero in self.hero_group:
                    hero.fire()
            elif event.type == BUFF1_SHOW_UP:
                buff1 = Buff1()
                self.buff1_group.add(buff1)
            elif event.type == BUFF2_SHOW_UP: #濒死下核弹改为血包
                if self.hero.bar.color == color_red:
                    buff = Buff3()
                else:
                    buff= Buff2()
                self.buff1_group.add(buff)
            elif event.type == ENEMY_FIRE_EVENT:
                for enemy in self.enemy_group:
                    if enemy.number >= 2:
                        enemy.fire()
                        for bullet in enemy.bullets:
                            self.enemy_bullet_group.add(bullet)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.bomb_throw()
            else:
                if self.game_over == True:
                    flag = self.canvas_over.event_handler(event)
                    if flag == 1:
                        self.__start__()                       
                    elif flag == 0:
                        pygame.quit()
                        sys.exit()

        # 使用键盘提供的方法获取键盘按键 - 按键元组
        keys_pressed = pygame.key.get_pressed()
        pygame.key.stop_text_input() #停止读文本输入，防止按字母键的时候卡死（作为读文本在等待）
        # 判断元组中对应的按键索引值 
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.heros_move(5)
        elif keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.heros_move(-5)
        elif keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            self.heros_move(0, -5)
        elif keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            self.heros_move(0, 5)
        else:
            self.heros_move(0, 0)

    def heros_move(self, x=0, y=0):
        self.hero.speedx = x
        self.hero.speedy = y

    def bomb_throw(self):
        music_use_bomb = pygame.mixer.Sound("./music/use_bomb.wav")
        if self.hero.bomb > 0:
            music_use_bomb.play()
            self.hero.bomb -= 1
            self.bombs.pop()
            for enemy in self.enemy_group:
                if enemy.number < 3:
                    enemy.bar.length = 0
                    enemy.isboom = True
                else:
                    enemy.injury = 20
                    enemy.isboom = True

    def __check_collide(self):

        # 1. 子弹摧毁敌机
        for enemy in self.enemy_group:
            for hero in self.hero_group:
                for bullet in hero.bullets:
                    if pygame.sprite.collide_mask(bullet, enemy):  # 这种碰撞检测可以精确到像素去掉alpha遮罩的那种哦
                        bullet.kill()
                        enemy.injury = bullet.hity
                        enemy.isboom = True
                        if enemy.bar.length <= 0:
                            self.enemy_group.remove(enemy)
                            self.enemy_boom.add(enemy)

        # 2. 敌机撞毁英雄
        for enemy in self.enemy_group:
            if pygame.sprite.collide_mask(self.hero, enemy):
                if enemy.number < 3:
                    enemy.bar.length = 0  # 敌机直接死
                    self.hero.injury = self.hero.bar.value / 3  # 英雄掉3分之一的血
                    if self.hero.buff1_num > 0:
                        if self.hero.buff1_num == 5:
                            self.mate1.kill()
                            self.mate2.kill()
                        self.hero.buff1_num -= 1
                        self.hero.music_degrade.play()
                    self.enemy_group.remove(enemy)
                    self.enemy_boom.add(enemy)
                    enemy.isboom = True
                else:
                    self.hero.bar.length = 0
                self.hero.isboom = True

        # 子弹摧毁英雄
        for bullet in self.enemy_bullet_group:
            if pygame.sprite.collide_mask(self.hero, bullet):
                bullet.kill()
                # self.hero.injury = 1
                self.hero.injury = self.hero.bar.value / 3  # 英雄掉3分之一的血
                if self.hero.buff1_num > 0:
                    self.hero.music_degrade.play()
                    if self.hero.buff1_num == 5:
                        self.mate1.kill()
                        self.mate2.kill()
                    self.hero.buff1_num -= 1

                self.hero.isboom = True

        # 英雄死亡，移出英雄和队友，停止播放音乐
        if not self.hero.alive():
            self.hero.rect.right = -10  # 把英雄移除屏幕
            self.hero.kill()
            if self.hero.buff1_num >= 4: #5级死的时候buff显示为4
                # mate移出屏幕
                self.mate1.rect.right = -10
                self.mate2.rect.right = -10
                self.mate1.kill()
                self.mate2.kill()
                # self.hero.buff1_num = 0
            self.game_over = True
            pygame.mixer.fadeout(2000)

        # 3.buff吸收
        if self.hero.bar.length: #需要判断英雄是否存活，否则会在英雄死后继续生成跟班
            for buff in self.buff1_group:
                if pygame.sprite.collide_mask(self.hero, buff):
                    buff.music_get.play()
                    if buff.tag == 1:  
                        if self.hero.buff1_num < 5 and self.hero.alive():
                            self.hero.buff1_num += 1
                            self.hero.music_upgrade.play()
                            if self.hero.buff1_num == 5:
                                self.team_show()

                    elif buff.tag==2:
                        self.hero.bomb += 1
                        image = pygame.image.load("./images/bomb.png")
                        self.bombs.append(image)
                    elif buff.tag==3:
                        if self.hero.bar.length < self.hero.bar.weight*self.hero.bar.value:
                            # self.hero.bar.length += self.hero.bar.weight*self.hero.bar.value
                            self.hero.bar.length += 160
                    buff.kill()

    def team_show(self):
        self.mate1 = Heromate(-1)
        self.mate2 = Heromate(1)
        self.mate1.image = pygame.image.load("./images/life.png")
        self.mate1.rect = self.mate1.image.get_rect()
        self.mate2.image = pygame.image.load("./images/life.png")
        self.mate2.rect = self.mate2.image.get_rect()
        self.hero_group.add(self.mate1)
        self.hero_group.add(self.mate2)

    # 各种更新
    def __update_sprites(self):

        self.back_group.update()
        self.back_group.draw(self.screen)

        self.enemy_group.update()
        self.enemy_group.draw(self.screen)

        self.enemy_boom.update()
        self.enemy_boom.draw(self.screen)

        self.heros_update()
        self.hero_group.draw(self.screen)

        for hero in self.hero_group:
            hero.bullets.update()
            hero.bullets.draw(self.screen)

        self.buff1_group.update()
        self.buff1_group.draw(self.screen)

        self.bars_update()
        self.bombs_update()

        self.enemy_bullet_group.update()
        self.enemy_bullet_group.draw(self.screen)

        # 得分和等级显示
        self.score_show()
        self.level_show()
        
        # 游戏开始和结束画面显示
        global GAME_ACTIVE
        if not GAME_ACTIVE:
        # if not self.game_active:
            self.canvas_start.update()
        if self.game_over:
            self.canvas_over.update()  
        pygame.display.flip()

    def heros_update(self):

        # 绘制剩余生命数量
        life_num = int(self.hero.bar.length / 160)
        life_image = pygame.image.load("images/life.png").convert_alpha()
        life_rect = life_image.get_rect()
        if life_num:
            for i in range(life_num):
                self.screen.blit(life_image, \
                    (SCREEN_RECT.width - 10 - (i + 1) * life_rect.width, \
                    SCREEN_RECT.height - 30 - life_rect.height))

        for hero in self.hero_group:
            if hero.number == 1:
                hero.rect.bottom = self.hero.rect.bottom
                hero.rect.left = self.hero.rect.right
            if hero.number == -1:
                hero.rect.bottom = self.hero.rect.bottom
                hero.rect.right = self.hero.rect.left
            hero.update()

    def bars_update(self):
        for bar in self.bars:
            if bar.length > 0:
                bar.update(self.screen)
            else:
                self.bars.remove(bar)

    def bullet_enemy_update(self):
        for enemy in self.enemy_group:
            enemy.bullets.update()
            enemy.bullets.draw(self.screen)

    def bombs_update(self):
        i = 1
        for bomb in self.bombs:
            self.screen.blit(bomb, (0, 700 - (bomb.get_rect().height) * i))
            i += 1

    def score_show(self):
        score_font = pygame.font.Font("./STCAIYUN.ttf", 33)
        image = score_font.render("SCORE:" + str(int(self.score.getvalue())), True, color_gray)
        rect = image.get_rect()
        rect.bottom, rect.right = 700, 480
        self.screen.blit(image, rect)

    def level_show(self):
        level_font = pygame.font.Font("./STCAIYUN.ttf", 33)
        level_image = level_font.render("LEVEL:" + str(int(self.hero.buff1_num)), True, color_gray)
        # if self.hero.buff1_num < 5:
        #     level_image = level_font.render("LEVEL:" + str(int(self.hero.buff1_num)), True, color_black)
        # else:
        #     level_image = level_font.render("LEVEL: MAX" , True, color_black)
        rect = level_image.get_rect()
        rect.right = SCREEN_RECT.right - 20
        rect.top = 50
        self.screen.blit(level_image, rect)
        
    @staticmethod
    def __start__():
        # 创建游戏对象
        game = PlaneGame()
        # 启动游戏
        game.start_game()


if __name__ == '__main__':
    PlaneGame.__start__()
