import pygame
import math
import random
from src.scenes.base_scene import BaseScene
from src.world.world import World
from src.world.camera import Camera
from src.entities.player import Player
from src.entities.npc import NPC
from src.entities.interactive_object import InteractiveObject
from src.entities.vighna import Vighna
from src.entities.stranger import Stranger
from src.entities.divine_attacks import DivineShockwave, TridentStrikeArea
from src.systems.dialogue_manager import DialogueManager
from src.utils.helpers import load_font
from src.settings import COLORS, LOGICAL_WIDTH, LOGICAL_HEIGHT

class TempleEntrance(InteractiveObject):
    def __init__(self, x: float, y: float, scene):
        super().__init__(x, y, "Temple Entrance", interaction_range=150.0)
        self.scene = scene
        self.surf = pygame.Surface((200, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.surf, (40, 30, 20), (0, 0, 200, 100))
        pygame.draw.rect(self.surf, COLORS["saffron"], (0, 0, 200, 100), 4)
        
        self.prompt_surf = self.font.render("[E] APPROACH ENTRANCE", True, COLORS["ivory"])
        self.prompt_surf_hold = self.font.render("[E] STAND YOUR GROUND", True, COLORS["saffron"])
        self.time = 0.0

    def draw(self, surface: pygame.Surface, camera):
        self.time += 0.016
        if self.scene.objective == "HOLD THE GATE":
            self.prompt_surf = self.prompt_surf_hold
        surface.blit(self.surf, (self.x - camera.x - 100, self.y - camera.y - 50))
        
        if self.scene.objective == "EXAMINE THE TEMPLE ENTRANCE":
            pulse = abs(math.sin(self.time * 3))
            pygame.draw.circle(surface, (200, 150, 50, int(100 * pulse)), (int(self.x - camera.x), int(self.y - camera.y)), 60, 2)
            
        if self.scene.state in ["SHIVA_BATTLE_INTRO", "SHIVA_BATTLE_DIALOGUE", "SHIVA_BATTLE", "SHIVA_POWER_MOMENT"]:
            pulse = abs(math.sin(self.time * 4))
            pygame.draw.circle(surface, (*COLORS["gold"], int(50 * pulse)), (int(self.x - camera.x), int(self.y - camera.y)), 120, 5)
            # Integrity visual damage
            if hasattr(self.scene, 'gate_integrity') and self.scene.gate_integrity < 50:
                pygame.draw.circle(surface, (*COLORS["crimson"], int(80 * pulse)), (int(self.x - camera.x), int(self.y - camera.y)), 120, 2)

    def interact(self, game):
        if self.scene.objective == "GO TO THE TEMPLE ENTRANCE" and self.scene.state == "EXPLORE":
            dialogue = [
                ("GANESHA", "This is the entrance Mother entrusted to me."),
                ("GANESHA", "I will not let anyone pass.")
            ]
            def on_complete():
                self.scene.set_objective("GUARD THE ENTRANCE")
                # Trigger encounter
                self.scene.trigger_vighna_intro()
                
            self.scene.dialogue_manager.start_dialogue(dialogue, on_complete)
        elif self.scene.objective == "EXAMINE THE TEMPLE ENTRANCE" and self.scene.state == "EXPLORE":
            dialogue = [
                ("GANESHA", "This is not the work of the Vighnas."),
                ("GANESHA", "Someone... or something... tried to break the seal."),
                ("GANESHA", "Mother entrusted this place to me."),
                ("GANESHA", "I must protect it until she returns.")
            ]
            def on_complete():
                self.scene.trigger_mountain_disturbance()
            self.scene.dialogue_manager.start_dialogue(dialogue, on_complete)
        elif self.scene.objective == "RETURN TO THE TEMPLE ENTRANCE" and self.scene.state == "EXPLORE":
            dialogue = [
                ("STRANGER", "Move aside, child."),
                ("GANESHA", "I cannot."),
                ("STRANGER", "Do you know whom you stand before?"),
                ("GANESHA", "I know only what my mother commanded me."),
                ("GANESHA", "No one enters.")
            ]
            def on_complete():
                self.scene.set_objective("HOLD THE GATE")
                self.scene.game.save_manager.data["checkpoint"] = "stranger_arrived"
                self.scene.game.save_manager.save()
            self.scene.dialogue_manager.start_dialogue(dialogue, on_complete)
        elif self.scene.objective == "HOLD THE GATE" and self.scene.state == "EXPLORE":
            dialogue = [
                ("STRANGER", "Then you leave me no choice."),
                ("GANESHA", "I will not fail Mother.")
            ]
            def on_complete():
                self.scene.trigger_final_standoff()
            self.scene.dialogue_manager.start_dialogue(dialogue, on_complete)

class MountainPath(InteractiveObject):
    def __init__(self, x: float, y: float, scene):
        super().__init__(x, y, "Mountain Path", interaction_range=200.0)
        self.scene = scene
        
    def draw(self, surface: pygame.Surface, camera):
        pass
        
    def interact(self, game):
        if self.scene.objective == "INVESTIGATE THE MOUNTAIN" and self.scene.state == "EXPLORE":
            self.scene.trigger_stranger_arrival()

class KailashWorldScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        
        self.world = World(2000, 1500)
        self.camera = Camera(2000, 1500)
        
        self.player = Player(1000, 1200)
        self.world.add_entity(self.player)
        
        parvati_dialogue = [
            ("PARVATI", "My child, I must leave for a while."),
            ("PARVATI", "Guard the temple entrance. Do not allow anyone to pass."),
            ("PARVATI", "This gate is under your protection."),
            ("GANESHA", "I will not fail you, Mother.")
        ]
        
        self.parvati = NPC(1000, 800, "Parvati", parvati_dialogue)
        self.world.add_entity(self.parvati)
        
        self.entrance = TempleEntrance(1000, 400, self)
        self.world.add_entity(self.entrance)
        
        self.mountain_path = MountainPath(1500, 800, self)
        self.world.add_entity(self.mountain_path)
        
        self.dialogue_manager = DialogueManager()
        
        self.font_ui_title = load_font(None, 24)
        self.font_ui_obj = load_font(None, 28)
        self.font_cinematic = load_font(None, 60)
        self.font_tutorial_title = load_font(None, 32)
        self.font_tutorial_text = load_font(None, 24)
        
        self.current_chapter = 1
        self.set_chapter(1)
        self.ui_obj_title = self.font_ui_title.render("OBJECTIVE", True, COLORS["gold"])
        
        self.objective = "SPEAK TO MOTHER"
        self.parvati_spoken_to = False
        
        # State Machine: EXPLORE -> VIGHNA_INTRO -> COMBAT -> VICTORY -> EXPLORE
        self.state = "EXPLORE"
        self.state_timer = 0.0
        self.cinematic_text = ""
        self.vighnas = []
        
        self.battle_timer = 60.0
        self.gate_integrity = 100.0
        self.save_cooldown = 0.0
        self.power_moment_triggered = False
        self.spoken_to_parvati_reborn = False
        self.spoken_to_parvati_reborn = False
        self.rebirth_particles = []
        self.rebirth_particles = []
        
        # Pre-render heart
        self.heart_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.heart_surf, COLORS["crimson"], [(15, 30), (5, 15), (10, 5), (15, 10), (20, 5), (25, 15)])
        
        # Load from checkpoint
        checkpoint = self.game.save_manager.data.get("checkpoint", "")
        if checkpoint in ["gate_standoff_complete", "shiva_revealed", "broken_gate_complete", "father_son_confrontation_started", "father_son_confrontation_complete", "ganesha_fallen", "parvati_arrived"]:
            self.set_chapter(2)
        elif checkpoint in ["chapter_2_complete", "ganesha_reborn"]:
            self.set_chapter(3)
            
        if checkpoint in ["gate_standoff_complete", "shiva_revealed"]:
            self.state = "CHAPTER_2_INTRO"
            self.state_timer = 0.0
            self.set_objective("")
            self.stranger = Stranger(self.entrance.x + 100, self.entrance.y)
            self.world.add_entity(self.stranger)
            self.parvati_spoken_to = True
            if checkpoint == "shiva_revealed":
                # Quick skip if loading post-reveal (optional, but requested to handle gracefully)
                # Actually, let's just replay the sequence from intro for simplicity, 
                # or start at post reveal if shiva_revealed.
                self.state = "POST_REVEAL"
                self.set_objective("PROTECT THE GATE")
                self.stranger.is_shiva_revealed = True
        elif checkpoint in ["broken_gate_complete", "father_son_confrontation_started"]:
            self.state = "SHIVA_BATTLE_INTRO"
            self.state_timer = 0.0
            self.set_objective("")
            self.stranger = Stranger(self.entrance.x + 100, self.entrance.y)
            self.stranger.is_shiva_revealed = True
            self.world.add_entity(self.stranger)
            self.parvati_spoken_to = True
            if checkpoint == "broken_gate_complete":
                self.game.save_manager.data["checkpoint"] = "father_son_confrontation_started"
                self.game.save_manager.save()
        elif checkpoint == "father_son_confrontation_complete":
            self.state = "FINAL_STAND_RETURN"
            self.state_timer = 0.0
            self.set_objective("RETURN TO THE GATE")
            self.stranger = Stranger(self.entrance.x + 100, self.entrance.y)
            self.stranger.is_shiva_revealed = True
            self.world.add_entity(self.stranger)
            self.parvati_spoken_to = True
        elif checkpoint == "ganesha_fallen":
            self.state = "GANESHA_FALLEN"
            self.state_timer = 0.0
            self.set_objective("")
            self.stranger = Stranger(self.entrance.x + 100, self.entrance.y)
            self.stranger.is_shiva_revealed = True
            self.world.add_entity(self.stranger)
            self.parvati_spoken_to = True
            self.player.x = self.entrance.x
            self.player.y = self.entrance.y
            self.player.health = 0
        elif checkpoint == "chapter_2_complete":
            self.state = "CHAPTER_3_INTRO"
            self.state_timer = 0.0
            self.set_objective("")
            self.stranger = Stranger(self.entrance.x + 100, self.entrance.y)
            self.stranger.is_shiva_revealed = True
            self.world.add_entity(self.stranger)
            self.parvati_spoken_to = True
            self.player.x = self.entrance.x
            self.player.y = self.entrance.y
            self.player.health = 0
            self.parvati.x = self.player.x - 50
            self.parvati.y = self.player.y
        elif checkpoint == "ganesha_reborn":
            self.state = "REBORN_EXPLORE"
            self.state_timer = 0.0
            self.set_objective("STAND WITH YOUR FAMILY")
            self.stranger = Stranger(self.entrance.x + 100, self.entrance.y)
            self.stranger.is_shiva_revealed = True
            self.world.add_entity(self.stranger)
            self.parvati_spoken_to = True
            self.player.is_reborn = True
            self.player.x = self.entrance.x
            self.player.y = self.entrance.y
            self.parvati.x = self.player.x - 100
            self.parvati.y = self.player.y
            
        elif checkpoint == "parvati_arrived":
            self.state = "PARVATI_ARRIVES"
            self.state_timer = 0.0
            self.set_objective("")
            self.stranger = Stranger(self.entrance.x + 100, self.entrance.y)
            self.stranger.is_shiva_revealed = True
            self.world.add_entity(self.stranger)
            self.parvati_spoken_to = True
            self.player.x = self.entrance.x
            self.player.y = self.entrance.y
            self.player.health = 0
            self.parvati.x = self.player.x - 150
            self.parvati.y = self.player.y

        
    def set_objective(self, text: str):
        self.objective = text
        
    def set_chapter(self, chapter: int):
        self.current_chapter = chapter
        if chapter == 1:
            self.ui_title_surf = self.font_ui_title.render("CHAPTER I - THE CHILD OF PARVATI", True, COLORS["saffron"])
        elif chapter == 2:
            self.ui_title_surf = self.font_ui_title.render("CHAPTER II - THE FATHER AND THE SON", True, COLORS["gold"])
        elif chapter == 3:
            self.ui_title_surf = self.font_ui_title.render("CHAPTER III - GANESHA REBORN", True, COLORS["gold"])


    def trigger_vighna_intro(self):
        self.state = "VIGHNA_INTRO"
        self.state_timer = 0.0
        self.set_objective("DEFEAT THE VIGHNAS")
        
    def trigger_mountain_disturbance(self):
        self.state = "DISTURBANCE"
        self.state_timer = 0.0
        self.cinematic_text = ""
        
    def trigger_stranger_arrival(self):
        self.state = "STRANGER_ARRIVAL"
        self.state_timer = 0.0
        self.cinematic_text = ""
        self.stranger = Stranger(2000, 800)
        self.world.add_entity(self.stranger)
        
    def trigger_final_standoff(self):
        self.state = "FINAL_STANDOFF"
        self.state_timer = 0.0
        self.cinematic_text = ""
        self.set_objective("")
        self.camera.add_shake(6.0, 0.5)
        
    def trigger_shiva_reveal(self):
        self.state = "SHIVA_REVEAL"
        self.state_timer = 0.0
        self.cinematic_text = ""
        self.camera.add_shake(3.0, 3.0)
        
    def trigger_shiva_power_demo(self):
        self.state = "SHIVA_POWER_DEMO"
        self.state_timer = 0.0
        self.camera.add_shake(8.0, 0.5)
        
        # Push Ganesha back
        dx = self.player.x - self.stranger.x
        dy = self.player.y - self.stranger.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.player.x += (dx/dist) * 50
            self.player.y += (dy/dist) * 50

    def handle_event(self, event: pygame.event.Event):
        if self.dialogue_manager.handle_event(event):
            if not self.dialogue_manager.active and not self.parvati_spoken_to:
                self.parvati_spoken_to = True
                self.set_objective("GO TO THE TEMPLE ENTRANCE")
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            from src.scenes.main_menu import MainMenuScene
            self.game.scene_manager.change_scene(MainMenuScene(self.game))
            return

        # Player handles movement & action only in gameplay states
        if not self.dialogue_manager.active and self.state in ["EXPLORE", "COMBAT", "POST_REVEAL", "SHIVA_BATTLE", "FINAL_STAND_RETURN", "FINAL_STAND_BATTLE", "REBORN_EXPLORE"]:
            self.player.handle_event(event)
            
            # Interact
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                for entity in self.world.entities:
                    if isinstance(entity, InteractiveObject) and entity.is_near_player:
                        entity.interact(self.game)
                        break

    def _spawn_vighnas(self):
        for _ in range(3):
            vx = self.entrance.x + random.uniform(-100, 100)
            vy = self.entrance.y + random.uniform(50, 150)
            v = Vighna(vx, vy)
            self.vighnas.append(v)
            self.world.add_entity(v)

    def _update_combat(self, dt: float):
        # Check Player strike hitting Vighnas
        if self.player.strike_hitbox:
            hx, hy, hr = self.player.strike_hitbox
            for v in self.vighnas:
                if v.state != "DEFEATED":
                    dist = math.hypot(hx - v.x, hy - v.y)
                    if dist < hr + 25: # 25 is approx vighna radius
                        # Determine knockback dir
                        dx = (v.x - self.player.x)
                        dy = (v.y - self.player.y)
                        length = math.hypot(dx, dy)
                        if length > 0: dx, dy = dx/length, dy/length
                        
                        v.hit(dx, dy)
                        self.camera.add_shake(5.0, 0.2)
                        
            # Consume hitbox so it doesn't hit multiple times per strike
            self.player.strike_hitbox = None
            
        # Check Vighnas hitting player
        active_vighnas = 0
        for v in self.vighnas:
            if v.state != "DEFEATED":
                active_vighnas += 1
                dist = math.hypot(v.x - self.player.x, v.y - self.player.y)
                if dist < 40: # collision threshold
                    dx = (self.player.x - v.x)
                    dy = (self.player.y - v.y)
                    length = math.hypot(dx, dy)
                    if length > 0: dx, dy = dx/length, dy/length
                    
                    if self.player.hurt(dx, dy):
                        self.camera.add_shake(8.0, 0.3)
                        
        if active_vighnas == 0:
            self.state = "VICTORY"
            self.state_timer = 0.0

    def update(self, dt: float):
        self.dialogue_manager.update(dt)
        
        if not self.dialogue_manager.active:
            self.world.update(dt)
            # Update world AI targets
            for e in self.world.entities:
                if isinstance(e, Vighna):
                    e.update(dt, self.player)
                elif isinstance(e, Stranger):
                    e.update(dt)
            
            # Check proximities
            if self.state in ["EXPLORE", "COMBAT", "POST_REVEAL", "SHIVA_BATTLE", "FINAL_STAND_RETURN", "FINAL_STAND_BATTLE"]:
                for entity in self.world.entities:
                    if isinstance(entity, InteractiveObject):
                        entity.check_proximity(self.player.x, self.player.y)
                        
            # Prevent leaving gate in POST_REVEAL and SHIVA_BATTLE
            if self.state in ["POST_REVEAL", "SHIVA_BATTLE", "FINAL_STAND_RETURN", "FINAL_STAND_BATTLE"]:
                dist_to_gate = math.hypot(self.player.x - self.entrance.x, self.player.y - self.entrance.y)
                if dist_to_gate > 350:
                    dx = self.entrance.x - self.player.x
                    dy = self.entrance.y - self.player.y
                    if dist_to_gate > 0:
                        self.player.x += (dx/dist_to_gate) * 5
                        self.player.y += (dy/dist_to_gate) * 5
                
                # Check player striking Shiva
                if self.player.strike_hitbox:
                    hx, hy, hr = self.player.strike_hitbox
                    dist = math.hypot(hx - self.stranger.x, hy - self.stranger.y)
                    if dist < hr + 50:
                        self.player.strike_hitbox = None
                        if self.state == "POST_REVEAL":
                            self.trigger_shiva_power_demo()
                        # In combat, striking Shiva does no direct health damage to him as he is invincible

                        
            # State logic
            if self.state == "VIGHNA_INTRO":
                self.state_timer += dt
                if self.state_timer < 2.0:
                    self.cinematic_text = "THE MOUNTAIN FALLS SILENT."
                elif self.state_timer < 4.0:
                    self.cinematic_text = "The shadows have come."
                elif self.state_timer < 5.0:
                    if len(self.vighnas) == 0:
                        self._spawn_vighnas()
                    self.cinematic_text = ""
                else:
                    self.cinematic_text = ""
                    self.state = "COMBAT"
                    self.state_timer = 0.0
                    
            elif self.state == "COMBAT":
                self.state_timer += dt
                self._update_combat(dt)
                
            elif self.state == "VICTORY":
                self.state_timer += dt
                if self.state_timer < 3.0:
                    self.cinematic_text = "THE MOUNTAIN FALLS SILENT..."
                elif self.state_timer < 3.1:
                    if self.cinematic_text != "":
                        self.cinematic_text = ""
                        dialogue = [
                            ("GANESHA", "They came for the gate... but why?"),
                            ("GANESHA", "Something is wrong.")
                        ]
                        def on_end():
                            self.state = "EXPLORE"
                            self.set_objective("EXAMINE THE TEMPLE ENTRANCE")
                        self.dialogue_manager.start_dialogue(dialogue, on_end)
                        
            elif self.state == "DISTURBANCE":
                self.state_timer += dt
                if self.state_timer < 3.0:
                    self.camera.add_shake(2.0, 0.1)
                elif self.state_timer < 5.0:
                    self.cinematic_text = "Something is approaching."
                else:
                    self.cinematic_text = ""
                    self.state = "EXPLORE"
                    self.set_objective("INVESTIGATE THE MOUNTAIN")
                    
            elif self.state == "STRANGER_ARRIVAL":
                self.state_timer += dt
                if self.state_timer > 2.0 and self.state_timer < 2.1:
                    dialogue = [
                        ("GANESHA", "Someone is approaching."),
                        ("GANESHA", "I cannot leave the entrance.")
                    ]
                    def on_end():
                        self.state = "EXPLORE"
                        self.set_objective("RETURN TO THE TEMPLE ENTRANCE")
                        self.stranger.target = (self.entrance.x + 100, self.entrance.y)
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 3.0
                    
            elif self.state == "FINAL_STANDOFF":
                self.state_timer += dt
                if self.state_timer > 2.0:
                    self.state = "CLIFFHANGER"
                    self.state_timer = 0.0
                    self.game.save_manager.data["checkpoint"] = "gate_standoff_complete"
                    self.game.save_manager.save()
                    
            elif self.state == "CLIFFHANGER":
                self.state_timer += dt
                if self.state_timer > 3.0:
                    self.set_chapter(2)
                    self.state = "CHAPTER_2_INTRO"
                    self.state_timer = 0.0
                    self.set_objective("")
                
            elif self.state == "CHAPTER_2_INTRO":
                self.state_timer += dt
                if self.state_timer > 6.0:
                    dialogue = [
                        ("STRANGER", "You were told to guard this door?"),
                        ("GANESHA", "Yes."),
                        ("STRANGER", "And you will not move?"),
                        ("GANESHA", "Not without Mother's permission."),
                        ("STRANGER", "I am the lord of this mountain."),
                        ("GANESHA", "Then you must still wait.")
                    ]
                    def on_end():
                        self.trigger_shiva_reveal()
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state = "GATE_CONFRONTATION_2"
                    self.state_timer = 0.0
                    
            elif self.state == "SHIVA_REVEAL":
                self.state_timer += dt
                if self.state_timer > 3.0 and self.state_timer < 3.1:
                    self.stranger.is_shiva_revealed = True
                    dialogue = [
                        ("SHIVA", "Do you know whom you stand before?"),
                        ("GANESHA", "No."),
                        ("SHIVA", "I am Shiva.")
                    ]
                    def on_end():
                        self.state = "GANESHA_REALIZATION"
                        self.state_timer = 0.0
                        self.game.save_manager.data["checkpoint"] = "shiva_revealed"
                        self.game.save_manager.save()
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 4.0
                    
            elif self.state == "GANESHA_REALIZATION":
                self.state_timer += dt
                if self.state_timer > 2.0 and self.state_timer < 2.1:
                    dialogue = [
                        ("GANESHA", "You... know Mother?"),
                        ("SHIVA", "She is my wife."),
                        ("GANESHA", "Then... you are...")
                    ]
                    def on_end():
                        self.state = "POST_REVEAL"
                        self.set_objective("PROTECT THE GATE")
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 3.0
                    
            elif self.state == "SHIVA_POWER_DEMO":
                self.state_timer += dt
                if self.state_timer > 1.0 and self.state_timer < 1.1:
                    dialogue = [
                        ("GANESHA", "I cannot let you pass."),
                        ("SHIVA", "Then you have chosen your path.")
                    ]
                    def on_end():
                        self.state = "SHIVA_BATTLE_INTRO"
                        self.state_timer = 0.0
                        self.game.save_manager.data["checkpoint"] = "broken_gate_complete"
                        self.game.save_manager.save()
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 2.0
                    
            elif self.state == "BROKEN_GATE_CLIFFHANGER":
                self.state_timer += dt
                if self.state_timer > 1.0:
                    self.state = "SHIVA_BATTLE_INTRO"
                    self.state_timer = 0.0
                    self.set_objective("")
                
            elif self.state == "SHIVA_BATTLE_INTRO":
                self.state_timer += dt
                if self.state_timer > 4.0:
                    self.state = "SHIVA_BATTLE_DIALOGUE"
                    self.state_timer = 0.0
                    dialogue = [
                        ("SHIVA", "Child, step aside."),
                        ("GANESHA", "Mother entrusted this gate to me."),
                        ("SHIVA", "You do not know who stands before you."),
                        ("GANESHA", "I know only the promise I gave."),
                        ("SHIVA", "Then you leave me no choice."),
                        ("GANESHA", "I will not fail Mother.")
                    ]
                    def on_end():
                        self.state = "SHIVA_BATTLE"
                        self.set_objective("HOLD THE GATE")
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    
            elif self.state == "SHIVA_BATTLE":
                self.state_timer += dt
                self.battle_timer -= dt
                
                # Check win condition
                if self.battle_timer <= 0:
                    self.state = "SHIVA_BATTLE_END"
                    self.state_timer = 0.0
                    
                # Check fail conditions
                if self.player.health <= 0 or self.gate_integrity <= 0:
                    self.state = "SHIVA_BATTLE_FAIL"
                    self.state_timer = 0.0
                    
                # Power moment at 30 seconds
                if self.battle_timer <= 30.0 and not self.power_moment_triggered:
                    self.power_moment_triggered = True
                    self.state = "SHIVA_POWER_MOMENT"
                    self.state_timer = 0.0
                    self.camera.add_shake(10.0, 1.0)
                    
                # Spawn Attacks
                self.shiva_attack_cooldown -= dt
                if self.shiva_attack_cooldown <= 0:
                    self.shiva_attack_cooldown = random.uniform(2.5, 4.0)
                    attack_type = random.choice(["SHOCKWAVE", "TRIDENT"])
                    if attack_type == "SHOCKWAVE":
                        self.world.add_entity(DivineShockwave(self.stranger.x, self.stranger.y))
                    else:
                        target_x = self.player.x if random.random() > 0.5 else self.entrance.x
                        target_y = self.player.y if random.random() > 0.5 else self.entrance.y
                        self.world.add_entity(TridentStrikeArea(target_x, target_y))
                        
                # Check Attack hits
                for e in self.world.entities:
                    if isinstance(e, DivineShockwave):
                        dist = math.hypot(self.player.x - e.x, self.player.y - e.y)
                        if dist < e.radius and dist > e.radius - 20:
                            if self.player.hurt( (self.player.x - e.x)/dist, (self.player.y - e.y)/dist ):
                                self.camera.add_shake(5.0, 0.3)
                        # Damage gate
                        gate_dist = math.hypot(self.entrance.x - e.x, self.entrance.y - e.y)
                        if gate_dist < e.radius and gate_dist > e.radius - 20:
                            self.gate_integrity -= 10 * dt
                            
                    elif isinstance(e, TridentStrikeArea):
                        if e.struck and e.strike_duration > 0:
                            dist = math.hypot(self.player.x - e.x, self.player.y - e.y)
                            if dist < e.radius:
                                if self.player.hurt( (self.player.x - e.x)/max(dist, 1), (self.player.y - e.y)/max(dist, 1) ):
                                    self.camera.add_shake(8.0, 0.3)
                            gate_dist = math.hypot(self.entrance.x - e.x, self.entrance.y - e.y)
                            if gate_dist < e.radius:
                                self.gate_integrity -= 30 * dt
                                
            elif self.state == "SHIVA_POWER_MOMENT":
                self.state_timer += dt
                if self.state_timer > 2.0 and self.state_timer < 2.1:
                    dialogue = [
                        ("SHIVA", "Your courage honors your mother."),
                        ("GANESHA", "I must keep my promise.")
                    ]
                    def on_end():
                        self.state = "SHIVA_BATTLE"
                        self.set_objective("HOLD THE GATE")
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 3.0
                    
            elif self.state == "SHIVA_BATTLE_END":
                self.state_timer += dt
                if self.state_timer > 5.0 and self.state_timer < 5.1:
                    self.game.save_manager.data["checkpoint"] = "father_son_confrontation_complete"
                    self.game.save_manager.save()
                    self.state_timer = 6.0
                elif self.state_timer > 8.0:
                    self.state = "FINAL_STAND_RETURN"
                    self.state_timer = 0.0
                    self.set_objective("RETURN TO THE GATE")
                    
            elif self.state == "SHIVA_BATTLE_FAIL":
                self.state_timer += dt
                if self.state_timer > 5.0:
                    # Retry — reload scene from checkpoint
                    from src.scenes.kailash_world import KailashWorldScene
                    self.game.scene_manager.change_scene(KailashWorldScene(self.game))
            elif self.state == "FINAL_STAND_RETURN":
                self.state_timer += dt
                if self.state_timer > 5.0:
                    # Auto-trigger final stand without requiring proximity
                    self.state = "FINAL_STAND_DIALOGUE"
                    self.state_timer = 0.0
                    self.set_objective("")
                    dialogue = [
                        ("SHIVA", "Child. The gate is no longer yours to guard."),
                        ("GANESHA", "Mother gave me this duty."),
                        ("SHIVA", "You have stood against me long enough."),
                        ("GANESHA", "I will not abandon my promise."),
                        ("SHIVA", "Then stand."),
                        ("GANESHA", "I will.")
                    ]
                    def on_end():
                        self.state = "FINAL_STAND_BATTLE"
                        self.set_objective("PROTECT THE GATE")
                        self.battle_timer = 60.0
                        self.power_moment_triggered = False
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                        
            elif self.state == "FINAL_STAND_BATTLE":
                self.state_timer += dt
                self.battle_timer -= dt
                
                # Check cinematic condition
                if self.battle_timer <= 0:
                    self.state = "THE_INEVITABLE_MOMENT"
                    self.state_timer = 0.0
                    
                # Power moment at 15 seconds remaining (75% through 60s)
                if self.battle_timer <= 15.0 and not self.power_moment_triggered:
                    self.power_moment_triggered = True
                    self.state = "FINAL_STAND_MID_DIALOGUE"
                    self.state_timer = 0.0
                    
                # Intensity phases
                if self.battle_timer > 40:
                    cooldown = random.uniform(2.0, 3.0) # Phase 1
                elif self.battle_timer > 20:
                    cooldown = random.uniform(1.0, 2.0) # Phase 2
                else:
                    cooldown = random.uniform(0.5, 1.5) # Phase 3/4
                    self.camera.add_shake(2.0, 0.1) # Constant rumble
                    
                self.shiva_attack_cooldown -= dt
                if self.shiva_attack_cooldown <= 0:
                    self.shiva_attack_cooldown = cooldown
                    attack_type = random.choice(["SHOCKWAVE", "TRIDENT"])
                    if attack_type == "SHOCKWAVE":
                        self.world.add_entity(DivineShockwave(self.stranger.x, self.stranger.y))
                    else:
                        target_x = self.player.x if random.random() > 0.3 else self.entrance.x
                        target_y = self.player.y if random.random() > 0.3 else self.entrance.y
                        self.world.add_entity(TridentStrikeArea(target_x, target_y))
                        
                # Check Attack hits (but no fail state for Ganesha dying, just damage/shake)
                for e in self.world.entities:
                    if isinstance(e, DivineShockwave):
                        dist = math.hypot(self.player.x - e.x, self.player.y - e.y)
                        if dist < e.radius and dist > e.radius - 20:
                            if self.player.hurt((self.player.x - e.x)/dist, (self.player.y - e.y)/dist):
                                self.camera.add_shake(8.0, 0.3)
                    elif isinstance(e, TridentStrikeArea):
                        if e.struck and e.strike_duration > 0:
                            dist = math.hypot(self.player.x - e.x, self.player.y - e.y)
                            if dist < e.radius:
                                if self.player.hurt((self.player.x - e.x)/max(dist, 1), (self.player.y - e.y)/max(dist, 1)):
                                    self.camera.add_shake(12.0, 0.4)
                                    
            elif self.state == "FINAL_STAND_MID_DIALOGUE":
                self.state_timer += dt
                if self.state_timer > 1.0 and self.state_timer < 1.1:
                    dialogue = [
                        ("SHIVA", "You have courage, child."),
                        ("GANESHA", "I have my mother's trust.")
                    ]
                    def on_end():
                        self.state = "FINAL_STAND_BATTLE"
                        self.set_objective("PROTECT THE GATE")
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 2.0
                    
            elif self.state == "THE_INEVITABLE_MOMENT":
                self.state_timer += dt
                self.set_objective("")
                if self.state_timer > 0.1 and self.state_timer < 0.2:
                    self.stranger.target = (self.entrance.x + 100, self.entrance.y)
                elif self.state_timer > 2.0 and self.state_timer < 2.1:
                    dialogue = [("GANESHA", "I will not fail Mother.")]
                    self.dialogue_manager.start_dialogue(dialogue, lambda: None)
                    self.state_timer = 3.0
                elif self.state_timer > 6.0 and self.state_timer < 6.1 and not self.dialogue_manager.active:
                    self.camera.add_shake(20.0, 1.0)
                    self.game.save_manager.data["checkpoint"] = "ganesha_fallen"
                    self.game.save_manager.save()
                    self.player.health = 0
                    self.state_timer = 7.0
                elif self.state_timer > 10.0:
                    self.state = "GANESHA_FALLEN"
                    self.state_timer = 0.0
                    
            elif self.state == "GANESHA_FALLEN":
                self.state_timer += dt
                if self.state_timer > 8.0 and self.state_timer < 8.1:
                    self.state = "PARVATI_ARRIVES"
                    self.state_timer = 0.0
                    self.game.save_manager.data["checkpoint"] = "parvati_arrived"
                    self.game.save_manager.save()
                    self.parvati.x = self.player.x - 150
                    self.parvati.y = self.player.y
                    
            elif self.state == "PARVATI_ARRIVES":
                self.state_timer += dt
                if self.state_timer > 6.0 and self.state_timer < 6.1:
                    dialogue = [
                        ("PARVATI", "Ganesha..."),
                        ("PARVATI", "My child..."),
                        ("PARVATI", "What have you done?"),
                        ("SHIVA", "He stood before me."),
                        ("PARVATI", "He was only doing what I asked of him."),
                        ("SHIVA", "He did not know me."),
                        ("PARVATI", "He knew only that he had a duty."),
                        ("SHIVA", "...And he did not break it.")
                    ]
                    def on_end():
                        self.state = "SHIVA_REALIZATION"
                        self.state_timer = 0.0
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 7.0
                    
            elif self.state == "SHIVA_REALIZATION":
                self.state_timer += dt
                if self.state_timer > 3.0 and self.state_timer < 3.1:
                    dialogue = [
                        ("SHIVA", "He was protecting you."),
                        ("SHIVA", "I will restore what was lost."),
                        ("PARVATI", "You will.")
                    ]
                    def on_end():
                        self.state = "CHAPTER_2_ENDING"
                        self.state_timer = 0.0
                        self.game.save_manager.data["checkpoint"] = "chapter_2_complete"
                        self.game.save_manager.save()
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 4.0
                    
            elif self.state == "CHAPTER_2_ENDING":
                self.state_timer += dt
                if self.state_timer > 27.0:
                    self.set_chapter(3)
                    self.state = "CHAPTER_3_INTRO"
                    self.state_timer = 0.0
                    self.set_objective("")
                    self.player.x = self.entrance.x
                    self.player.y = self.entrance.y
                    self.player.health = 0
                    self.parvati.x = self.player.x - 50
                    self.parvati.y = self.player.y
                
            elif self.state == "CHAPTER_3_INTRO":
                self.state_timer += dt
                if self.state_timer > 9.0:
                    self.state = "PARVATI_GRIEF"
                    self.state_timer = 0.0
                    
            elif self.state == "PARVATI_GRIEF":
                self.state_timer += dt
                if self.state_timer > 3.0 and self.state_timer < 3.1:
                    dialogue = [
                        ("PARVATI", "My child..."),
                        ("PARVATI", "You were only protecting what I asked you to protect."),
                        ("PARVATI", "I never wished this fate upon you."),
                        ("SHIVA", "Parvati..."),
                        ("PARVATI", "You came too late."),
                        ("SHIVA", "I did not know who stood before me."),
                        ("PARVATI", "He was our son.")
                    ]
                    def on_end():
                        self.state = "PARVATI_GRIEF_PAUSE"
                        self.state_timer = 0.0
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 4.0
                    
            elif self.state == "PARVATI_GRIEF_PAUSE":
                self.state_timer += dt
                if self.state_timer > 2.0 and self.state_timer < 2.1:
                    dialogue = [
                        ("SHIVA", "He knew only his duty."),
                        ("SHIVA", "And he did not abandon it.")
                    ]
                    def on_end():
                        self.state = "SHIVA_PROMISE"
                        self.state_timer = 0.0
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 3.0
                    
            elif self.state == "SHIVA_PROMISE":
                self.state_timer += dt
                if self.state_timer > 2.0 and self.state_timer < 2.1:
                    dialogue = [
                        ("SHIVA", "I gave my word."),
                        ("SHIVA", "I will restore him."),
                        ("PARVATI", "Then bring my child back."),
                        ("SHIVA", "I will.")
                    ]
                    def on_end():
                        self.state = "DIVINE_RESTORATION"
                        self.state_timer = 0.0
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 3.0
                    
            elif self.state == "DIVINE_RESTORATION":
                self.state_timer += dt
                
                # Spawn particles
                if self.state_timer > 5.0 and self.state_timer < 15.0:
                    for _ in range(int(self.state_timer - 4.0) * 2):
                        angle = random.uniform(0, math.pi * 2)
                        dist = random.uniform(100, 300)
                        self.rebirth_particles.append({
                            "x": self.player.x + math.cos(angle) * dist,
                            "y": self.player.y - 20 + math.sin(angle) * dist,
                            "vx": -math.cos(angle) * random.uniform(20, 50),
                            "vy": -math.sin(angle) * random.uniform(20, 50),
                            "life": random.uniform(1.0, 2.0),
                            "max_life": 2.0
                        })
                
                if self.state_timer > 10.0 and self.state_timer < 15.0:
                    self.camera.add_shake(2.0, 0.1)
                
                if self.state_timer > 15.0 and self.state_timer < 15.1:
                    self.player.is_reborn = True
                    self.player.health = 3
                
                if self.state_timer > 18.0:
                    self.state = "ELEPHANT_REVEAL"
                    self.state_timer = 0.0
                    self.rebirth_particles = []
                    
            elif self.state == "ELEPHANT_REVEAL":
                self.state_timer += dt
                if self.state_timer > 5.0 and self.state_timer < 5.1:
                    self.state = "PARVATI_REACTION"
                    self.state_timer = 0.0
                    
            elif self.state == "PARVATI_REACTION":
                self.state_timer += dt
                if self.state_timer > 2.0 and self.state_timer < 2.1:
                    dialogue = [
                        ("PARVATI", "My child..."),
                        ("GANESHA", "Mother?"),
                        ("SHIVA", "From this day, you will be known as Ganesha."),
                        ("GANESHA", "Father?"),
                        ("SHIVA", "Yes, child.")
                    ]
                    def on_end():
                        self.state = "GANESHA_IDENTITY"
                        self.state_timer = 0.0
                    self.dialogue_manager.start_dialogue(dialogue, on_end)
                    self.state_timer = 3.0
                    
            elif self.state == "GANESHA_IDENTITY":
                self.state_timer += dt
                if self.state_timer > 8.0:
                    self.state = "REBORN_EXPLORE"
                    self.state_timer = 0.0
                    self.set_objective("STAND WITH YOUR FAMILY")
                    self.game.save_manager.data["checkpoint"] = "ganesha_reborn"
                    self.game.save_manager.save()
                    
            elif self.state == "REBORN_EXPLORE":
                self.state_timer += dt
                # After 30 seconds of exploration, auto-trigger ending
                if self.state_timer > 30.0:
                    self.state = "START_FINAL_ENDING"
                    self.state_timer = 0.0
                    self.set_objective("")
            elif self.state == "START_FINAL_ENDING":
                self.state_timer += dt
                if self.state_timer > 3.0:
                    self.state = "FINAL_ENDING_CARDS"
                    self.state_timer = 0.0
                    self.set_objective("")
                    
            elif self.state == "FINAL_ENDING_CARDS":
                self.state_timer += dt
                if self.state_timer > 26.0:
                    # Return to main menu
                    from src.scenes.main_menu import MainMenuScene
                    self.game.scene_manager.change_scene(MainMenuScene(self.game))

        for p in self.rebirth_particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        self.rebirth_particles = [p for p in self.rebirth_particles if p["life"] > 0]
        
        self.camera.update(self.player, dt)

    def draw(self, surface: pygame.Surface):
        # Darken atmosphere during combat
        darken = 0.0
        if self.state == "VIGHNA_INTRO":
            darken = min(0.4, self.state_timer * 0.1)
        elif self.state == "COMBAT":
            darken = 0.4
        elif self.state == "VICTORY":
            darken = max(0.0, 0.4 - self.state_timer * 0.1)
        elif self.state == "DISTURBANCE":
            darken = min(0.3, self.state_timer * 0.1)
        elif self.state == "STRANGER_ARRIVAL" or self.objective == "RETURN TO THE TEMPLE ENTRANCE":
            darken = 0.3
        elif self.objective == "HOLD THE GATE":
            darken = 0.4
        elif self.state in ["FINAL_STANDOFF", "CHAPTER_2_INTRO", "GATE_CONFRONTATION_2"]:
            darken = 0.6
        elif self.state == "SHIVA_REVEAL":
            darken = min(0.8, 0.6 + self.state_timer * 0.1)
        elif self.state in ["GANESHA_REALIZATION", "POST_REVEAL", "SHIVA_POWER_DEMO"]:
            darken = 0.7
        elif self.state in ["SHIVA_BATTLE_INTRO", "SHIVA_BATTLE_DIALOGUE"]:
            darken = 0.5
        elif self.state == "SHIVA_BATTLE":
            darken = 0.4
            if self.battle_timer <= 30.0:
                darken = 0.6
        elif self.state == "SHIVA_POWER_MOMENT":
            darken = 0.8
        elif self.state == "SHIVA_BATTLE_END":
            darken = 0.5
        elif self.state == "SHIVA_BATTLE_FAIL":
            darken = min(1.0, self.state_timer * 0.2)
        elif self.state == "FINAL_STAND_RETURN":
            darken = 0.4
        elif self.state == "FINAL_STAND_DIALOGUE":
            darken = 0.6
        elif self.state == "FINAL_STAND_BATTLE":
            if self.battle_timer > 40:
                darken = 0.6
            elif self.battle_timer > 20:
                darken = 0.7
            else:
                darken = 0.8
        elif self.state == "FINAL_STAND_MID_DIALOGUE":
            darken = 0.9
        elif self.state == "THE_INEVITABLE_MOMENT":
            darken = min(1.0, 0.8 + self.state_timer * 0.1)
        elif self.state == "GANESHA_FALLEN":
            darken = 1.0 # Overlay will handle pitch black with text
        elif self.state == "PARVATI_ARRIVES":
            darken = 0.9
        elif self.state == "CHAPTER_2_ENDING":
            darken = 0.0 # Overlay handles it
        elif self.state == "CHAPTER_3_INTRO":
            darken = 1.0
        elif self.state == "PARVATI_GRIEF" or self.state == "PARVATI_GRIEF_PAUSE" or self.state == "SHIVA_PROMISE":
            darken = 0.9
        elif self.state == "DIVINE_RESTORATION":
            darken = max(0.0, 0.9 - (self.state_timer / 15.0) * 0.9)
        elif self.state in ["ELEPHANT_REVEAL", "PARVATI_REACTION", "GANESHA_IDENTITY"]:
            darken = 0.0
        elif self.state == "REBORN_EXPLORE":
            darken = 0.0
        elif self.state == "START_FINAL_ENDING":
            darken = min(1.0, self.state_timer / 3.0)
        elif self.state == "FINAL_ENDING_CARDS":
            darken = 1.0
        elif self.state in ["CLIFFHANGER", "BROKEN_GATE_CLIFFHANGER"]:
            darken = 0.0 # Overlay will handle black screen
            
        self.world.draw(surface, self.camera, darken)
        self.dialogue_manager.draw(surface)
        
        # Draw minimal UI
        surface.blit(self.ui_title_surf, (20, 20))
        
        # Draw health hearts if taking damage or in combat
        if self.state in ["COMBAT", "VIGHNA_INTRO", "VICTORY"] or self.player.health < 3:
            for i in range(self.player.health):
                surface.blit(self.heart_surf, (20 + i * 40, 60))
        
        # Draw objective panel
        if self.objective and not self.dialogue_manager.active and self.state not in ["GANESHA_FALLEN", "THE_INEVITABLE_MOMENT", "PARVATI_ARRIVES", "SHIVA_REALIZATION", "CHAPTER_2_ENDING", "CLIFFHANGER", "BROKEN_GATE_CLIFFHANGER", "CHAPTER_2_INTRO", "CHAPTER_3_INTRO", "PARVATI_GRIEF", "PARVATI_GRIEF_PAUSE", "SHIVA_PROMISE", "DIVINE_RESTORATION", "ELEPHANT_REVEAL", "PARVATI_REACTION", "GANESHA_IDENTITY", "FINAL_ENDING_CARDS"]:
            obj_surf = self.font_ui_obj.render(self.objective, True, COLORS["ivory"])
            RIGHT_MARGIN = 30
            TOP_MARGIN = 20
            
            obj_w = max(self.ui_obj_title.get_width(), obj_surf.get_width())
            box_rect = pygame.Rect(LOGICAL_WIDTH - RIGHT_MARGIN - obj_w - 20, TOP_MARGIN, obj_w + 40, 70)
            
            # Draw background panel
            s = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            pygame.draw.rect(s, COLORS["gold"], s.get_rect(), 1)
            surface.blit(s, box_rect)
            
            # Right align text inside box
            title_x = box_rect.right - 10 - self.ui_obj_title.get_width()
            obj_x = box_rect.right - 10 - obj_surf.get_width()
            
            surface.blit(self.ui_obj_title, (title_x, TOP_MARGIN + 10))
            surface.blit(obj_surf, (obj_x, TOP_MARGIN + 35))
        
        # Draw Waypoint
        target = None
        if self.objective in ["GO TO THE TEMPLE ENTRANCE", "EXAMINE THE TEMPLE ENTRANCE", "RETURN TO THE TEMPLE ENTRANCE"]:
            target = self.entrance
        elif self.objective == "INVESTIGATE THE MOUNTAIN":
            target = self.mountain_path
            
        if target:
            dx = target.x - self.player.x
            dy = target.y - self.player.y
            dist = math.hypot(dx, dy)
            if dist > 200:
                if dist > 0: dx, dy = dx/dist, dy/dist
                
                # Screen center offset
                cx = LOGICAL_WIDTH // 2
                cy = LOGICAL_HEIGHT // 2
                
                # Draw at radius
                radius = 150
                wp_x = cx + dx * radius
                wp_y = cy + dy * radius
                
                wp_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.polygon(wp_surf, COLORS["gold"], [(10, 0), (20, 10), (10, 20), (0, 10)])
                
                # Pulsing
                import time
                alpha = max(50, min(255, int(150 + math.sin(time.time() * 5.0) * 100)))
                wp_surf.set_alpha(alpha)
                
                surface.blit(wp_surf, wp_surf.get_rect(center=(wp_x, wp_y)))
        
        # Draw cinematic text
        if self.cinematic_text and not self.dialogue_manager.active:
            cin_surf = self.font_cinematic.render(self.cinematic_text, True, COLORS["gold"])
            cin_rect = cin_surf.get_rect(center=(LOGICAL_WIDTH // 2, LOGICAL_HEIGHT // 2))
            
            # Simple fade math based on state timer
            alpha = 255
            if self.state_timer % 2.0 < 0.5:
                alpha = int((self.state_timer % 2.0) * 2 * 255)
            elif self.state_timer % 2.0 > 1.5:
                alpha = int((2.0 - (self.state_timer % 2.0)) * 2 * 255)
                
            cin_surf.set_alpha(max(0, min(255, alpha)))
            surface.blit(cin_surf, cin_rect)
            
        # Draw Combat Tutorial
        if self.state == "COMBAT" and self.state_timer < 5.0:
            alpha = 255
            if self.state_timer > 4.0:
                alpha = max(0, min(255, int((5.0 - self.state_timer) * 255)))
                
            tut_w, tut_h = 300, 150
            tut_x = LOGICAL_WIDTH // 2 - tut_w // 2
            tut_y = LOGICAL_HEIGHT - tut_h - 100
            
            tut_surf = pygame.Surface((tut_w, tut_h), pygame.SRCALPHA)
            tut_surf.fill((0, 0, 0, int(150 * (alpha/255))))
            pygame.draw.rect(tut_surf, (*COLORS["gold"], alpha), tut_surf.get_rect(), 2)
            
            lines = [
                ("COMBAT", self.font_tutorial_title, COLORS["saffron"]),
                ("[WASD] MOVE", self.font_tutorial_text, COLORS["ivory"]),
                ("[SPACE] DIVINE STRIKE", self.font_tutorial_text, COLORS["gold"]),
                ("[ESC] PAUSE", self.font_tutorial_text, COLORS["ivory"])
            ]
            
            cy = 15
            for text, font, color in lines:
                surf = font.render(text, True, color)
                surf.set_alpha(alpha)
                tut_surf.blit(surf, (tut_w//2 - surf.get_width()//2, cy))
                cy += 30
                
            surface.blit(tut_surf, (tut_x, tut_y))
            
        if self.state in ["SHIVA_BATTLE", "FINAL_STAND_BATTLE"] and self.state_timer < 5.0:
            surf1 = self.font_tutorial_text.render("[WASD / ARROWS] MOVE", True, COLORS["saffron"])
            surf2 = self.font_tutorial_text.render("[SPACE] DIVINE STRIKE", True, COLORS["saffron"])
            surf3 = self.font_tutorial_text.render("[SHIFT] DODGE", True, COLORS["saffron"])
            surface.blit(surf1, (20, LOGICAL_HEIGHT - 90))
            surface.blit(surf2, (20, LOGICAL_HEIGHT - 60))
            surface.blit(surf3, (20, LOGICAL_HEIGHT - 30))
        elif self.state == "REBORN_EXPLORE" and self.state_timer < 10.0:
            alpha = 255
            if self.state_timer > 4.0:
                alpha = max(0, min(255, int((5.0 - self.state_timer) * 255)))
                
            tut_w, tut_h = 350, 180
            tut_x = LOGICAL_WIDTH // 2 - tut_w // 2
            tut_y = LOGICAL_HEIGHT - tut_h - 100
            
            tut_surf = pygame.Surface((tut_w, tut_h), pygame.SRCALPHA)
            tut_surf.fill((0, 0, 0, int(150 * (alpha/255))))
            pygame.draw.rect(tut_surf, (*COLORS["gold"], alpha), tut_surf.get_rect(), 2)
            
            lines = [
                ("HOLD THE GATE", self.font_tutorial_title, COLORS["saffron"]),
                ("[WASD] MOVE", self.font_tutorial_text, COLORS["ivory"]),
                ("[SPACE] DIVINE STRIKE", self.font_tutorial_text, COLORS["gold"]),
                ("[SHIFT] DASH / DODGE", self.font_tutorial_text, COLORS["ivory"])
            ]
            
            cy = 15
            for text, font, color in lines:
                surf = font.render(text, True, color)
                surf.set_alpha(alpha)
                tut_surf.blit(surf, (tut_w//2 - surf.get_width()//2, cy))
                cy += 30
                
            surface.blit(tut_surf, (tut_x, tut_y))
            
        if self.state in ["SHIVA_BATTLE", "SHIVA_POWER_MOMENT", "FINAL_STAND_BATTLE", "FINAL_STAND_MID_DIALOGUE"] and not self.dialogue_manager.active:
            # Draw Timer
            timer_text = f"SURVIVE: {max(0, int(self.battle_timer))} SECONDS"
            timer_surf = self.font_ui_obj.render(timer_text, True, COLORS["gold"])
            surface.blit(timer_surf, (LOGICAL_WIDTH//2 - timer_surf.get_width()//2, 20))
            
            # Draw Gate Integrity
            int_text = f"GATE INTEGRITY: {max(0, int(self.gate_integrity))}%"
            int_color = COLORS["ivory"] if self.gate_integrity > 50 else COLORS["crimson"]
            int_surf = self.font_ui_obj.render(int_text, True, int_color)
            surface.blit(int_surf, (LOGICAL_WIDTH//2 - int_surf.get_width()//2, 60))
            
        # Draw Cliffhanger
        if self.state in ["CLIFFHANGER", "CHAPTER_2_INTRO", "BROKEN_GATE_CLIFFHANGER", "GANESHA_FALLEN", "THE_INEVITABLE_MOMENT", "CHAPTER_2_ENDING", "SHIVA_REALIZATION", "PARVATI_ARRIVES", "CHAPTER_3_INTRO", "SHIVA_PROMISE", "DIVINE_RESTORATION", "ELEPHANT_REVEAL", "GANESHA_IDENTITY", "FINAL_ENDING_CARDS"]:
            alpha = min(255, int(self.state_timer * 128)) if self.state != "CHAPTER_2_INTRO" else max(0, 255 - int(self.state_timer * 128))
            if self.state == "BROKEN_GATE_CLIFFHANGER":
                alpha = min(255, int(self.state_timer * 128))
            elif self.state == "THE_INEVITABLE_MOMENT":
                if self.state_timer > 3.0:
                    alpha = min(255, int((self.state_timer - 3.0) * 200))
                else:
                    alpha = 0
            elif self.state == "GANESHA_FALLEN":
                alpha = 255


            elif self.state == "CHAPTER_2_ENDING":
                alpha = min(255, int(self.state_timer * 128))
                
            fade_surf = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((0, 0, 0, alpha))
            surface.blit(fade_surf, (0, 0))
            
            if self.state == "CHAPTER_2_INTRO":
                if self.state_timer > 1.0 and self.state_timer < 5.0:
                    t1 = self.font_cinematic.render("CHAPTER II", True, COLORS["gold"])
                    t2 = self.font_cinematic.render("THE FATHER AND THE SON", True, COLORS["ivory"])
                    t_alpha = min(255, int((self.state_timer - 1.0) * 255)) if self.state_timer < 2.0 else min(255, int((5.0 - self.state_timer) * 255))
                    t1.set_alpha(t_alpha)
                    t2.set_alpha(t_alpha)
                    surface.blit(t1, t1.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 40)))
                    surface.blit(t2, t2.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 40)))
                    
            elif self.state == "BROKEN_GATE_CLIFFHANGER":
                if self.state_timer > 2.0 and self.state_timer < 5.0:
                    text_surf = self.font_cinematic.render("CHAPTER II — THE FATHER AND THE SON", True, COLORS["gold"])
                    t_alpha = min(255, int((self.state_timer - 2.0) * 255)) if self.state_timer < 3.0 else min(255, int((5.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 5.0 and self.state_timer < 8.0:
                    text_surf = self.font_cinematic.render("THE BROKEN GATE", True, COLORS["saffron"])
                    t_alpha = min(255, int((self.state_timer - 5.0) * 255)) if self.state_timer < 6.0 else min(255, int((8.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))

            elif self.state == "CLIFFHANGER":
                if self.state_timer > 2.0 and self.state_timer < 5.0:
                    text_surf = self.font_cinematic.render("THE FATHER RETURNS", True, COLORS["ivory"])
                    t_alpha = min(255, int((self.state_timer - 2.0) * 255)) if self.state_timer < 3.0 else min(255, int((5.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 5.0 and self.state_timer < 8.0:
                    text_surf = self.font_cinematic.render("CHAPTER I — THE CHILD OF PARVATI", True, COLORS["gold"])
                    t_alpha = min(255, int((self.state_timer - 5.0) * 255)) if self.state_timer < 6.0 else min(255, int((8.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                    
            elif self.state == "SHIVA_BATTLE_INTRO":
                if self.state_timer > 1.0 and self.state_timer < 4.0:
                    t1 = self.font_cinematic.render("CHAPTER II", True, COLORS["gold"])
                    t2 = self.font_cinematic.render("THE FATHER AND THE SON", True, COLORS["ivory"])
                    t_alpha = min(255, int((self.state_timer - 1.0) * 255)) if self.state_timer < 2.0 else min(255, int((4.0 - self.state_timer) * 255))
                    t1.set_alpha(t_alpha)
                    t2.set_alpha(t_alpha)
                    surface.blit(t1, t1.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 40)))
                    surface.blit(t2, t2.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 40)))
                    
            elif self.state == "SHIVA_BATTLE_END":
                if self.state_timer > 1.0 and self.state_timer < 6.0:
                    t1 = self.font_cinematic.render("THE OATH REMAINS UNBROKEN", True, COLORS["ivory"])
                    t2 = self.font_cinematic.render("CHAPTER II — THE FATHER AND THE SON", True, COLORS["gold"])
                    t3 = self.font_cinematic.render("THE STORY CONTINUES...", True, COLORS["saffron"])
                    
                    t_alpha = min(255, int((self.state_timer - 1.0) * 255)) if self.state_timer < 2.0 else min(255, int((6.0 - self.state_timer) * 255))
                    t1.set_alpha(t_alpha)
                    t2.set_alpha(t_alpha)
                    t3.set_alpha(t_alpha)
                    
                    surface.blit(t1, t1.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 60)))
                    surface.blit(t2, t2.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                    surface.blit(t3, t3.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 60)))
                    
            elif self.state == "SHIVA_BATTLE_FAIL":
                if self.state_timer > 1.0:
                    t1 = self.font_cinematic.render("THE GATE HAS FALLEN", True, COLORS["crimson"])
                    t2 = self.font_cinematic.render("Rise, Ganesha.", True, COLORS["ivory"])
                    
                    t_alpha = min(255, int((self.state_timer - 1.0) * 255))
                    t1.set_alpha(t_alpha)
                    t2.set_alpha(t_alpha)
                    
                    surface.blit(t1, t1.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 30)))
                    surface.blit(t2, t2.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 30)))
                    
            elif self.state == "THE_INEVITABLE_MOMENT":
                if self.state_timer > 7.0 and self.state_timer < 7.3:
                    surface.fill((255, 255, 255))
            elif self.state == "GANESHA_FALLEN":
                if self.state_timer > 2.0 and self.state_timer < 6.0:
                    text_surf = self.font_cinematic.render("THE MOUNTAIN FELL SILENT.", True, COLORS["ivory"])
                    t_alpha = min(255, int((self.state_timer - 2.0) * 255)) if self.state_timer < 3.0 else min(255, int((6.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 6.0 and self.state_timer < 10.0:
                    text_surf = self.font_cinematic.render("THE CHILD HAD KEPT HIS PROMISE.", True, COLORS["saffron"])
                    t_alpha = min(255, int((self.state_timer - 6.0) * 255)) if self.state_timer < 7.0 else min(255, int((10.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 10.0 and self.state_timer < 14.0:
                    text_surf = self.font_cinematic.render("BUT A MOTHER'S HEART DOES NOT ACCEPT SILENCE.", True, COLORS["gold"])
                    t_alpha = min(255, int((self.state_timer - 10.0) * 255)) if self.state_timer < 11.0 else min(255, int((14.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))

            elif self.state == "CHAPTER_3_INTRO":
                if self.state_timer > 1.0 and self.state_timer < 8.0:
                    t1 = self.font_cinematic.render("CHAPTER III", True, COLORS["gold"])
                    t2 = self.font_cinematic.render("GANESHA REBORN", True, COLORS["ivory"])
                    t3 = self.font_tutorial_text.render("From loss, a new beginning.", True, COLORS["saffron"])
                    
                    t_alpha = min(255, int((self.state_timer - 1.0) * 255)) if self.state_timer < 2.0 else min(255, int((8.0 - self.state_timer) * 255))
                    t1.set_alpha(t_alpha)
                    t2.set_alpha(t_alpha)
                    t3.set_alpha(t_alpha)
                    
                    surface.blit(t1, t1.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 40)))
                    surface.blit(t2, t2.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 20)))
                    surface.blit(t3, t3.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 60)))
            elif self.state == "SHIVA_PROMISE":
                if self.state_timer > 3.0 and self.state_timer < 6.0:
                    text_surf = self.font_cinematic.render("THE PROMISE WAS MADE.", True, COLORS["ivory"])
                    t_alpha = min(255, int((self.state_timer - 3.0) * 255)) if self.state_timer < 4.0 else min(255, int((6.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
            elif self.state == "DIVINE_RESTORATION":
                # Draw particles
                for p in self.rebirth_particles:
                    p_alpha = max(0, min(255, int(255 * (p["life"] / p["max_life"]))))
                    pygame.draw.circle(surface, (*COLORS["gold"], p_alpha), (int(p["x"] - self.camera.x), int(p["y"] - self.camera.y)), 3)
                
                # Draw growing rings around Ganesha
                if self.state_timer > 10.0 and self.state_timer < 15.0:
                    radius = int((self.state_timer - 10.0) * 40)
                    pygame.draw.circle(surface, COLORS["gold"], (int(self.player.x - self.camera.x), int(self.player.y - 20 - self.camera.y)), radius, 2)
                    
                # White flash at peak
                if self.state_timer > 14.5 and self.state_timer < 16.5:
                    flash_surf = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
                    f_alpha = min(255, int((self.state_timer - 14.5) * 510)) if self.state_timer < 15.0 else min(255, int((16.5 - self.state_timer) * 170))
                    flash_surf.fill((255, 240, 200, f_alpha))
                    surface.blit(flash_surf, (0,0))
                    
            elif self.state == "GANESHA_IDENTITY":
                if self.state_timer > 1.0 and self.state_timer < 7.0:
                    t1 = self.font_cinematic.render("GANESHA", True, COLORS["gold"])
                    t2 = self.font_cinematic.render("THE ELEPHANT-HEADED CHILD", True, COLORS["ivory"])
                    t_alpha = min(255, int((self.state_timer - 1.0) * 255)) if self.state_timer < 2.0 else min(255, int((7.0 - self.state_timer) * 255))
                    t1.set_alpha(t_alpha)
                    t2.set_alpha(t_alpha)
                    surface.blit(t1, t1.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 30)))
                    surface.blit(t2, t2.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 30)))
            elif self.state == "FINAL_ENDING_CARDS":
                if self.state_timer > 2.0 and self.state_timer < 6.0:
                    text_surf = self.font_cinematic.render("THE OATH WAS KEPT.", True, COLORS["gold"])
                    t_alpha = min(255, int((self.state_timer - 2.0) * 255)) if self.state_timer < 3.0 else min(255, int((6.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 6.0 and self.state_timer < 10.0:
                    text_surf = self.font_cinematic.render("THE CHILD RETURNED.", True, COLORS["ivory"])
                    t_alpha = min(255, int((self.state_timer - 6.0) * 255)) if self.state_timer < 7.0 else min(255, int((10.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 10.0 and self.state_timer < 14.0:
                    text_surf = self.font_cinematic.render("GANESHA WAS REBORN.", True, COLORS["saffron"])
                    t_alpha = min(255, int((self.state_timer - 10.0) * 255)) if self.state_timer < 11.0 else min(255, int((14.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 14.0 and self.state_timer < 18.0:
                    text_surf = self.font_cinematic.render("AND A NEW STORY BEGAN.", True, COLORS["ivory"])
                    t_alpha = min(255, int((self.state_timer - 14.0) * 255)) if self.state_timer < 15.0 else min(255, int((18.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 18.0 and self.state_timer < 26.0:
                    t1 = self.font_cinematic.render("EKADANTA", True, COLORS["gold"])
                    t2 = self.font_tutorial_text.render("THE STORY CONTINUES...", True, COLORS["saffron"])
                    t_alpha = min(255, int((self.state_timer - 18.0) * 255)) if self.state_timer < 19.0 else min(255, int((26.0 - self.state_timer) * 255))
                    t1.set_alpha(t_alpha)
                    t2.set_alpha(t_alpha)
                    surface.blit(t1, t1.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 20)))
                    surface.blit(t2, t2.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 20)))
            elif self.state == "CHAPTER_2_ENDING":
                if self.state_timer > 2.0 and self.state_timer < 6.0:
                    text_surf = self.font_cinematic.render("THE OATH WAS KEPT.", True, COLORS["gold"])
                    t_alpha = min(255, int((self.state_timer - 2.0) * 255)) if self.state_timer < 3.0 else min(255, int((6.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 6.0 and self.state_timer < 10.0:
                    text_surf = self.font_cinematic.render("THE SON HAD FALLEN.", True, COLORS["saffron"])
                    t_alpha = min(255, int((self.state_timer - 6.0) * 255)) if self.state_timer < 7.0 else min(255, int((10.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 10.0 and self.state_timer < 14.0:
                    text_surf = self.font_cinematic.render("THE FATHER WOULD RESTORE HIM.", True, COLORS["ivory"])
                    t_alpha = min(255, int((self.state_timer - 10.0) * 255)) if self.state_timer < 11.0 else min(255, int((14.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))
                elif self.state_timer > 14.0 and self.state_timer < 18.0:
                    t1 = self.font_cinematic.render("CHAPTER II", True, COLORS["gold"])
                    t2 = self.font_cinematic.render("THE FATHER AND THE SON", True, COLORS["ivory"])
                    t_alpha = min(255, int((self.state_timer - 14.0) * 255)) if self.state_timer < 15.0 else min(255, int((18.0 - self.state_timer) * 255))
                    t1.set_alpha(t_alpha)
                    t2.set_alpha(t_alpha)
                    surface.blit(t1, t1.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 40)))
                    surface.blit(t2, t2.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 + 40)))

                elif self.state_timer > 22.0 and self.state_timer < 26.0:
                    text_surf = self.font_cinematic.render("CHAPTER III - GANESHA REBORN", True, COLORS["gold"])
                    t_alpha = min(255, int((self.state_timer - 22.0) * 255)) if self.state_timer < 23.0 else min(255, int((26.0 - self.state_timer) * 255))
                    text_surf.set_alpha(t_alpha)
                    surface.blit(text_surf, text_surf.get_rect(center=(LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2)))

