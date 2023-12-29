import pygame
import math
import random
import screeninfo
import json
class Data:
    def rotate_image(image, angle, position, screen):
        rotated_image = pygame.transform.rotate(image, angle)
        image_rect = image.get_rect()
        rrect = rotated_image.get_rect(center=(image_rect.width // 2, image_rect.height // 2))
        screen.blit(rotated_image, (position.x+rrect.x,position.y+rrect.y))
    def loadImage(path,width=35,height=35):
        img = pygame.image.load(path)
        img = pygame.transform.scale(img,(width,height))
        return img.convert_alpha()

    def resizeImage(surface,width,height):
        return pygame.transform.scale(surface,(width,height))
    def lsfsp(spritesheet,x,y,width,height,endWidth=32,endHeight=32):
        new_surf = pygame.Surface((width,height),pygame.SRCALPHA)
        source_rect = pygame.Rect(x, y, width, height)
        dest_rect = pygame.Rect(0, 0, width, height)
        new_surf.fill((0,0,0,0))
        new_surf.blit(spritesheet, dest_rect, source_rect)
        
        return pygame.transform.scale(new_surf,(endWidth,endHeight))
    def __init__(self):
        self.font = pygame.font.Font("vt323.ttf",25)
        self.spritesheet = pygame.Surface((128,128))
        self.sprites = {
            "halftransparent" : pygame.Surface((32,32),pygame.SRCALPHA),

        }
        self.has_collision = {}
        self.deadly = {}
        self.sprites["halftransparent"].fill((255,255,255,100))
        self.scales = {}
        self.type_list = []
        self.npc_types = []
        self.fetch_quest = {}
        self.fetch_quest_items = []
        self.dialogues = {}
        self.items = []
        self.loadDialogues()
        self.loadSprites()
    def loadSprites(self):
        f = open("settings/data.json","r")
        data = json.load(f)
        self.spritesheet = Data.loadImage(data["spritesheet"]["sprite"],data["spritesheet"]["width"],data["spritesheet"]["height"])
        self.sprites["npc1"] = Data.lsfsp(self.spritesheet,48,32,16,16)
        self.sprites["cloud"] =Data.lsfsp(self.spritesheet,data["cloud"]["x"],data["cloud"]["y"],data["cloud"]["width"],data["cloud"]["height"],data["cloud"]["endwidth"])
        self.sprites["playerright"] = Data.lsfsp(self.spritesheet,data["player"]["x"],data["player"]["y"],data["player"]["width"],data["player"]["height"],data["player"]["endwidth"])
        self.sprites["playerleft"] = pygame.transform.flip(self.sprites["playerright"],True,False)
        for i in data["blocks"]:
            self.sprites[i["name"]] = Data.lsfsp(self.spritesheet,i["x"],i["y"],i["width"],i["height"],i["endwidth"],i["endheight"])
            self.scales[i["name"]] = [i["endwidth"],i["endheight"]]
            self.deadly[i["name"]] = i["deadly"]
            self.type_list.append(i["name"])
            self.has_collision[i["name"]] = i["has_collision"]
    def loadDialogues(self):
        f = open("settings/dialogues.json","r")
        data = json.load(f)
        for i in data['npcs']:
            self.dialogues[i["name"]] = i["dialogues"]
            self.fetch_quest[i["name"]] = i["fetch quest"]
            self.npc_types.append(i["name"])
            if i["fetch quest"] != False:
                self.items.append([i["fetch quest"],i["item pos"][0],i["item pos"][1]])
                self.sprites[i["fetch quest"]] = Data.loadImage(i["sprite_path"],32,32)
class Chunk:
    def __init__(self,x,y,level):
        self.id = f"{int(x/300)*300} {int(y/300)*300}"
        self.level = level
        if not self.id in self.level.chunk_ids:
            self.level.chunk_ids.append(self.id)
            self.level.chunkDict[self.id] = self
            self.objects = [] 
            self.poses = []
    def update(self):
        for i in self.objects:
            i.update()
class Npc:
    def __init__(self,x,y,app,type,level):
        self.rect = pygame.Rect(x,y,32,32)
        self.app = app
        self.level = level
        self.level.npcs.append(self)
        choosen = random.randint(0,len(self.app.data.npc_types)-1)
        self.type = self.app.data.npc_types[choosen]
        self.released_space = False
        self.talking = -1
        self.done_quest = False
    def render_dialog(self,text,name):
        length = len(text)
        img = self.app.data.font.render(text,False,"white","black")
        position = pygame.Rect(self.rect.x-(length*10)/2-self.app.cam_pos[0],self.rect.y-25-self.app.cam_pos[1],length*10,25)
        self.app.screen.blit(img,position)
        img = self.app.data.font.render(name,False,"white","black")
        self.app.screen.blit(img,(position.x,position.y-25))
    def update(self):
        key = pygame.key.get_pressed()
        if not key[pygame.K_SPACE]:
            self.released_space = True
        for i in self.level.players:
            if pygame.Rect.colliderect(self.rect,pygame.Rect(i.rect.x,i.rect.y,16,16)):
                if key[pygame.K_SPACE] and self.released_space:
                    if self.app.data.fetch_quest[self.type] in i.items and not self.done_quest:
                        i.fetch_quests_done.append(self.app.data.fetch_quest[self.type])
                        self.done_quest = True
                        if self.app.data.fetch_quest[self.type] in i.fetch_quests_to_do:
                            i.fetch_quests_to_do.remove(self.app.data.fetch_quest[self.type])
                    else:      
                        if len(self.app.data.dialogues[self.type]) > self.talking:
                            i.locked = True
                            self.talking += 1
                            if (self.talking+1 > len(self.app.data.dialogues[self.type])):
                                i.locked = False
                                if self.app.data.fetch_quest[self.type] != False:
                                    i.fetch_quests_to_do.append(self.app.data.fetch_quest[self.type])
                    self.released_space = False
        
        if (self.talking < len(self.app.data.dialogues[self.type]) and self.talking!=-1):
            self.render_dialog(self.app.data.dialogues[self.type][self.talking],self.type)
        else:
            nm = self.app.data.font.render(self.type,False,"white","black")
            self.app.screen.blit(nm,(self.rect.x-self.app.cam_pos[0],self.rect.y-25-self.app.cam_pos[1]))
        
        self.app.screen.blit(self.app.data.sprites[f"npc1"],(self.rect.x-self.app.cam_pos[0],self.rect.y-self.app.cam_pos[1]))

class Player:
    def __init__(self,x,y,app,level):
        self.locked = False
        self.rect = pygame.Rect(x,y,32,32)
        self.app = app
        self.level = level
        self.y_velocity = 0
        self.level.players.append(self)
        self.angle_change = 1
        self.coll = {
            "left" : False,
            "down" : False,
            "up" : False,
            "right" : False,
        }
        self.fetch_quests_to_do = []
        self.fetch_quests_done = []
        self.items = []
        self.direction = "right"
        self.image_rect = self.app.data.sprites[f"player{self.direction}"].get_rect(center=(32 // 2, 32 // 2))
        self.angle = 35
        self.released_e = False
        self.open_menu = 1
    def movement(self):
        
        key = pygame.key.get_pressed()
        
        if not self.coll["down"]:
                self.y_velocity += 0.5
                self.angle += self.angle_change
                self.angle_change -= 10
                if self.angle_change < 25:
                    self.angle_change = 25
        else:
            self.y_velocity = -0.5
            if not key[pygame.K_d] and not key[pygame.K_a]: 
                self.angle = 0
                self.angle_change = 0
            
            if key[pygame.K_w] and not self.coll["up"]:
                self.angle_change = 100
                self.y_velocity = -15
        if not self.coll["left"]:
            if key[pygame.K_a]: 
                self.direction = "left"
                self.rect.x += -5
                self.angle += 25
        if not self.coll["right"]:
            if key[pygame.K_d]: 
                self.direction = "right"
                self.rect.x += 5
                self.angle += 25
        if self.y_velocity > 10:
            self.y_velocity = 10
        self.rect.y += self.y_velocity
    def update(self):
        if not self.locked:
            self.movement()
        self.app.cam_pos[0] = math.floor(self.rect.x) - self.app.screen_size[0]/2
        self.app.cam_pos[1] = math.floor(self.rect.y) - self.app.screen_size[1]/2
        #self.app.cam_pos[1] += key[pygame.K_s] * 5 + key[pygame.K_w] * -5
        self.coll = {
            "left" : False,
            "down" : False,
            "up" : False,
            "right" : False,
        }
        
        Data.rotate_image(self.app.data.sprites[f"player{self.direction}"],self.angle,pygame.Rect(self.rect.x-self.app.cam_pos[0],self.rect.y-self.app.cam_pos[1]-15,1,1),self.app.screen)
        key = pygame.key.get_pressed()
        if not key[pygame.K_e]:
            self.released_e = True
        elif(self.released_e):
            print("ea")
            self.open_menu *= -1
            self.released_e = False
        if self.open_menu==-1:
            r = 0
            for i in self.fetch_quests_to_do:
                img = self.app.data.font.render("get: "+i,False,"white")
                pygame.draw.rect(self.app.screen,"black",pygame.Rect(0,r*25,len("get: "+i)*10,25))
                self.app.screen.blit(img,pygame.Rect(0,r*25,len(i)*10,25))
                r+=1
            r = 0
            for i in self.fetch_quests_done:
                img = self.app.data.font.render(i,False,"white")
                pygame.draw.rect(self.app.screen,"black",pygame.Rect(150,r*25,len(i)*10,25))
                self.app.screen.blit(img,pygame.Rect(150,r*25,len(i)*10,25))
                r+=1
class Item:
    def __init__(self,x,y,type,level,app):
        self.rect = pygame.Rect(x,y,16,16)
        self.app = app
        self.level = level
        self.type = type
        self.level.npcs.append(self)
    def update(self):
        for i in self.level.players:
            if pygame.Rect.colliderect(i.rect,self.rect):
                self.level.npcs.remove(self)
                i.items.append(self.type)
        self.app.screen.blit(self.app.data.sprites[self.type],pygame.Rect(self.rect.x-self.app.cam_pos[0],self.rect.y-self.app.cam_pos[1],self.rect.width,self.rect.height))
        

class Block:
    def __init__(self,x,y,app,level,type):
        self.app = app
        self.level = level
        self.type = type
        self.rect = pygame.Rect(x,y,self.app.data.scales[type][0],self.app.data.scales[type][1])
        self.has_collision = self.app.data.has_collision[self.type]
        self.chunk_id = f"{int(x/300)*300} {int(y/300)*300}" 
        if not [x,y] in self.level.poses:
            if self.app.data.has_collision[self.type]:
                for dx in range(-1,1):
                    if not [x+dx*32,y] in self.level.poses and dx!=0:
                        self.has_collision = True
                    if not [x,y+dx*32] in self.level.poses and dx!=0:
                        self.has_collision = True

            self.level.poses.append([x,y])
            if not self.chunk_id in self.level.chunk_ids:
                Chunk(x,y,self.level)
            self.level.chunkDict[self.chunk_id].objects.append(self)
            self.level.chunkDict[self.chunk_id].poses.append([x,y])
    def destroy(self):
        self.level.poses.remove([self.rect.x,self.rect.y])
        self.level.chunkDict[self.chunk_id].objects.remove(self)
        print("destroyed")
    def update(self):
        if self.rect.x-self.app.cam_pos[0] > -50 and self.rect.x-self.app.cam_pos[0]<self.app.screen_size[0] and self.rect.y-self.app.cam_pos[1] > 0 and self.rect.y-self.app.cam_pos[1]<self.app.screen_size[1]:
            self.app.screen.blit(self.app.data.sprites[self.type],(self.rect.x-self.app.cam_pos[0],self.rect.y-self.app.cam_pos[1]))

            if self.has_collision:
                for i in self.level.players:
                    if pygame.Rect.colliderect(self.rect,pygame.Rect(i.rect.x+10,i.rect.y,16,16)):
                        i.coll["right"] = True
                    if pygame.Rect.colliderect(self.rect,pygame.Rect(i.rect.x-10,i.rect.y,16,16)):
                        i.coll["left"] = True
                    if pygame.Rect.colliderect(self.rect,pygame.Rect(i.rect.x,i.rect.y+10,16,16)):
                        i.coll["down"] = True
                    if pygame.Rect.colliderect(self.rect,pygame.Rect(i.rect.x,i.rect.y-5,16,16)):
                        i.coll["up"] = True
                        i.rect.y += 16
                        i.y_velocity = 0
            if self.app.mode == 1:
                if pygame.Rect.colliderect(self.rect,pygame.Rect(pygame.mouse.get_pos()[0]+self.app.cam_pos[0],pygame.mouse.get_pos()[1]+self.app.cam_pos[1],1,1)) and pygame.mouse.get_pressed()[2]:
                    self.destroy()
            if self.app.data.deadly[self.type]:
                for i in self.level.players:
                    if pygame.Rect.colliderect(self.rect,pygame.Rect(i.rect.x,i.rect.y,16,16)):
                        i.rect.x = self.level.player_spawnpoint[0]
                        i.rect.y = self.level.player_spawnpoint[0]
class Cloud:
    def __init__(self,x,y,app,level):
        self.app = app
        self.level = level
        self.level.clouds.append(self)
        self.pos = [x,y]
        self.speed = 1
        self.direction = random.randint(0,1)
    def update(self):
        if (self.direction==-1):
            self.pos[0] += self.speed
        else:
            self.pos[0] -= self.speed
        if (self.pos[0]>self.app.screen_size[0]+96):
            self.pos[0] = 0
            self.pos[1] = random.randint(1,int(self.app.screen_size[1]/32))*32+random.randint(-1,1) * 32
        if (self.pos[0]<-96):
            self.pos[0] = self.app.screen_size[0]
            self.pos[1] = random.randint(1,int(self.app.screen_size[1]/32))*32 +random.randint(-1,1) * 32
        self.app.screen.blit(self.app.data.sprites["cloud"],(self.pos[0],self.pos[1]))
class Level:
    def __init__(self,app):
        self.app = app
        self.objects = []
        self.clouds = []
        self.poses = []
        self.player_spawnpoint = [0,0]
        self.players = []
        self.npcs = []
        self.chunkDict = {}
        self.chunk_ids = []
        self.gen_clouds()
    def save_map(self):
        map = {
            "blocks" : [],
            "player_spawnpoint" : self.player_spawnpoint
        }
        for i in self.chunk_ids:
            for ii in self.chunkDict[i].objects:
                map["blocks"].append([ii.rect.x,ii.rect.y,ii.type])
        with open("settings/main_map.json", "w") as write_file:
            json.dump(map, write_file)
    def gen_clouds(self):
        cloud_count = (self.app.screen_size[0]/96*self.app.screen_size[1]/16)/2
        for i in range(16):
            Cloud(random.randint(1,int(self.app.screen_size[0]/32))*32,random.randint(1,int(self.app.screen_size[0]/32))*32+random.randint(-1,1) * 32,self.app,self)
    def load_map(self):
        f = open('settings/main_map.json')
        data = json.load(f)
        self.chunkDict = {}
        self.chunk_ids = []
        self.npcs = []
        self.poses = []
        self.players = []
        for i in data["blocks"]:
            if i[2] == "house":
                Npc(i[0],i[1]+32,self.app,1,self)
            Block(i[0],i[1],self.app,self,i[2])
        self.player_spawnpoint = data["player_spawnpoint"]
        for i in self.app.data.items:
            Item(i[1],i[2],i[0],self,self.app)
            print(i[0],i[1],i[2])
        Player(self.player_spawnpoint[0],self.player_spawnpoint[1],self.app,self)
class Editor:
    def __init__(self,app,level):
        self.app = app
        self.level = level
        self.hovered_over = False
        self.released_f5 = False
        self.choosen_type = "tree"
        self.released_f6 = False
    def update(self):
        key = pygame.key.get_pressed()
        self.app.updateObjects()
        if not key[pygame.K_F6]:
            self.released_f6 = True
        if self.released_f6 and key[pygame.K_F6]:
            self.released_f6 = False
            self.app.mode *= -1
        self.app.cam_pos[0] += key[pygame.K_a] * -5 + key[pygame.K_d] * 5
        self.app.cam_pos[1] += key[pygame.K_s] * 5 + key[pygame.K_w] * -5
        mx,my = pygame.mouse.get_pos()
        mx = math.floor((mx+self.app.cam_pos[0])/32)*32
        my = math.floor((my+self.app.cam_pos[1])/32)*32
        if key[pygame.K_r]:
            self.level.save_map()
        if key[pygame.K_t]:
            self.level.load_map()
        id = f"{int(self.app.cam_pos[0]/300)*300} {int(self.app.cam_pos[1]/300)*300}"
        if id in self.level.chunk_ids:
            self.level.chunkDict[id].update()
        
        self.app.screen.blit(self.app.data.sprites[self.choosen_type],(mx-self.app.cam_pos[0],my-self.app.cam_pos[1]))
        x = 0
        y = 0
        self.hovered_over = False
        for i in self.app.data.type_list:
            self.app.screen.blit(self.app.data.sprites[i],(x*35,y))
            if pygame.Rect.colliderect(pygame.Rect(x*35,y,32,32),pygame.Rect(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1],1,1)):
                self.hovered_over = True
                self.app.screen.blit(self.app.data.sprites["halftransparent"],(x*35,y))
                if pygame.mouse.get_pressed()[0]:
                    self.choosen_type = i
            
            x+=1      
        
        if pygame.mouse.get_pressed()[0] and not self.hovered_over:
            Block(mx,my,self.app,self.level,self.choosen_type)
        if pygame.mouse.get_pressed()[1]  and not [mx,my] in self.level.poses and not self.hovered_over and not key[pygame.K_q]:
            self.level.player_spawnpoint = [mx,my]
        if pygame.mouse.get_pressed()[1] and key[pygame.K_q]:
            print(mx,my)
class App:
    def __init__(self,width=600,height=600):
        self.screen = pygame.display.set_mode((width,height))
        pygame.font.init()
        self.background = Data.loadImage("sprites/background.png",width,height)
        self.crt = Data.loadImage("sprites/crt_effect.png",width,height)
        self.crt.set_alpha(50)
        self.screen_size = [width,height]
        self.running = True
        self.level = Level(self)
        self.data = Data()
        self.cam_pos = [0,0]
        self.clock = pygame.time.Clock()
        self.hovered_over = False
        self.released_f5 = False
        self.effects = {
            "crt" : False,
        }
        self.released_f6 = False
        self.mode = -1
        self.editor = Editor(self,self.level)
        self.level.load_map()
    def updateObjects(self):
        
        for x in range(0,int(self.screen_size[0]/300+2)):
            for y in range(0,int(self.screen_size[1]/300+2)):
                id = f"{int(self.cam_pos[0]/300)*300+x*300} {int(self.cam_pos[1]/300)*300+y*300}"
                if id in self.level.chunk_ids:
                    self.level.chunkDict[id].update()
        for i in self.level.npcs:
            i.update()
    def levelUpdate(self):
        key = pygame.key.get_pressed()
        if not key[pygame.K_F6]:
            self.released_f6 = True
        if self.released_f6 and key[pygame.K_F6]:
            self.released_f6 = False
            self.mode *= -1
        self.updateObjects()
        for i in self.level.players:
            i.update()
    def run(self):
        while self.running:
            self.screen.fill("cyan")
            self.screen.blit(self.background,(0,0))
            key = pygame.key.get_pressed()
            if not key[pygame.K_F5]:
                self.released_f5 = True
            elif(self.released_f5):
                for m in screeninfo.get_monitors():
                    pass
                self.screen = pygame.display.set_mode((m.width,m.height),pygame.FULLSCREEN)
                self.screen_size = [m.width,m.height]
                self.background = Data.loadImage("sprites/background.png",m.width,m.height)
                self.crt = Data.loadImage("sprites/crt_effect.png",m.width,m.height)
                self.level.gen_clouds()
                
                self.released_f5 = False
            for i in self.level.clouds:
                i.update()
            self.clock.tick(60)
            pygame.display.set_caption("fps:"+str(self.clock.get_fps())+" block count: " + str(len(self.level.objects)))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            if self.effects["crt"]:
                self.screen.blit(self.crt,(0,0))
            
            if self.mode == 1:
                self.editor.update()
            else:
                self.levelUpdate()
                
            pygame.display.flip()
_app = App(1000,800)

_app.run()