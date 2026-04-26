from typing import TYPE_CHECKING

import pygame

from .config import LANES

if TYPE_CHECKING:
    from .game import OceanRunner


class InputHandler:
    def __init__(self, app: "OceanRunner") -> None:
        self.app = app

    def move_selection(self, delta: int, size: int, target: str) -> None:
        if target == "menu":
            self.app.menu_index = (self.app.menu_index + delta) % size
        else:
            self.app.settings_index = (self.app.settings_index + delta) % size
        self.app.audio.play_sfx("select")

    def handle_menu_input(self, event: pygame.event.Event) -> None:
        menu_items = self.app.current_menu_items()
        if event.key in (pygame.K_UP, pygame.K_w):
            self.move_selection(-1, len(menu_items), "menu")
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.move_selection(1, len(menu_items), "menu")
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.app.audio.play_sfx("confirm")
            choice = menu_items[self.app.menu_index]
            if choice == "RESUME":
                self.app.gameplay.resume_game_with_countdown()
            elif choice == "PLAY":
                if self.app.menu_from_pause:
                    self.app.gameplay.open_confirmation("restart_run", "Mulai run baru? Progres run saat ini akan hilang.")
                else:
                    self.app.gameplay.start_game()
            elif choice == "GUIDE":
                self.app.switch_state("guide")
            elif choice == "HIGH SCORE":
                self.app.records = self.app.storage.load_records()
                self.app.switch_state("scores")
            elif choice == "SETTINGS":
                self.app.switch_state("settings")
            elif choice == "EXIT":
                self.app.gameplay.open_confirmation("exit_game", "Keluar dari game sekarang?")

    def handle_settings_input(self, event: pygame.event.Event) -> None:
        if event.key in (pygame.K_UP, pygame.K_w):
            self.move_selection(-1, len(self.app.settings_items), "settings")
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.move_selection(1, len(self.app.settings_items), "settings")
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            choice = self.app.settings_items[self.app.settings_index]
            if choice == "SFX":
                self.app.settings["sfx_enabled"] = not self.app.settings["sfx_enabled"]
                self.app.save_settings()
                self.app.audio.play_sfx("confirm")
            elif choice == "MUSIC":
                self.app.settings["music_enabled"] = not self.app.settings["music_enabled"]
                self.app.save_settings()
            elif choice == "RESET HIGH SCORE":
                if self.app.menu_from_pause:
                    self.app.audio.play_sfx("select")
                else:
                    self.app.gameplay.open_confirmation("reset_scores", "Reset semua high score yang tersimpan?")
            elif choice == "CREDIT":
                self.app.switch_state("credits")
                self.app.audio.play_sfx("confirm")
            elif choice == "BACK":
                self.app.switch_state("menu")
                self.app.audio.play_sfx("confirm")
        elif event.key == pygame.K_ESCAPE:
            self.app.switch_state("menu")

    def handle_game_input(self, event: pygame.event.Event) -> None:
        if event.key in (pygame.K_UP, pygame.K_w):
            self.app.player_lane = max(0, self.app.player_lane - 1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.app.player_lane = min(LANES - 1, self.app.player_lane + 1)

    def handle_input(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if self.app.confirm_action is not None:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.app.gameplay.execute_confirmation()
            elif event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.app.gameplay.close_confirmation()
                self.app.audio.play_sfx("select")
            return

        if event.key == pygame.K_ESCAPE:
            if self.app.state == "playing":
                self.app.gameplay.pause_game()
            elif self.app.state in {"guide", "scores", "settings", "credits", "game_over"}:
                self.app.switch_state("menu")
                self.app.audio.play_sfx("select")
            elif self.app.state == "menu" and self.app.menu_from_pause:
                self.app.gameplay.resume_game_with_countdown()
            return

        if self.app.state == "menu":
            self.handle_menu_input(event)
        elif self.app.state == "settings":
            self.handle_settings_input(event)
        elif self.app.state == "playing":
            if event.key == pygame.K_p:
                self.app.gameplay.pause_game()
            else:
                self.handle_game_input(event)
        elif self.app.state == "countdown":
            return
        elif self.app.state in {"guide", "scores", "credits"}:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.app.switch_state("menu")
                self.app.audio.play_sfx("confirm")
        elif self.app.state == "game_over":
            if event.key == pygame.K_r:
                self.app.gameplay.open_confirmation("restart_run", "Mulai run baru? Skor run yang sedang tampil akan ditinggalkan.")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.app.switch_state("menu")
                self.app.audio.play_sfx("confirm")
