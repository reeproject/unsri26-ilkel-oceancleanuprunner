from typing import TYPE_CHECKING

import pygame

from .config import CREDIT, GREEN, LANES, PANEL, PANEL_ALT, RED, SAND, SEA_LEFT, SEA_RIGHT, SHARK_CATCH_DISTANCE, SHARK_DISTANCE_START, WHITE, YELLOW
from .models import Entity

if TYPE_CHECKING:
    from .game import OceanRunner


class OceanRenderer:
    def __init__(self, app: "OceanRunner") -> None:
        self.app = app

    def draw_background(self) -> None:
        bg_sprite = self.app.sprites.get("background")
        if bg_sprite is not None:
            offset = int(self.app.bg_scroll) % self.app.width
            self.app.screen.blit(bg_sprite, (-offset, 0))
            self.app.screen.blit(bg_sprite, (self.app.width - offset, 0))
        else:
            for x in range(self.app.width):
                t = x / self.app.width
                color = (
                    int(SEA_LEFT[0] * (1 - t) + SEA_RIGHT[0] * t),
                    int(SEA_LEFT[1] * (1 - t) + SEA_RIGHT[1] * t),
                    int(SEA_LEFT[2] * (1 - t) + SEA_RIGHT[2] * t),
                )
                pygame.draw.line(self.app.screen, color, (x, 0), (x, self.app.height))
        pygame.draw.rect(self.app.screen, SAND, (0, self.app.height - self.app.sy(60), self.app.width, self.app.sy(60)))
        for lane in range(LANES):
            y = self.app.lane_center(lane)
            pygame.draw.line(self.app.screen, (171, 223, 236), (0, y), (self.app.width, y), max(1, self.app.ss(3)))
        for bubble in self.app.bubbles:
            shimmer = 0.7 + 0.3 * abs(pygame.math.Vector2(1, 0).rotate_rad(pygame.time.get_ticks() * 0.002 + bubble.phase).x)
            color = (int(160 * shimmer), int(210 * shimmer + 20), int(225 * shimmer + 20))
            pygame.draw.circle(self.app.screen, color, (int(bubble.x), int(bubble.y)), bubble.radius, max(1, self.app.ss(2)))

    def draw_player(self) -> None:
        player_sprite = self.app.sprites.get("player")
        if player_sprite is not None:
            self.app.screen.blit(player_sprite, player_sprite.get_rect(center=(self.app.player_x, int(self.app.player_y))))
            return
        pygame.draw.circle(self.app.screen, YELLOW, (self.app.player_x, int(self.app.player_y)), self.app.ss(20))

    def draw_shark(self) -> None:
        shark_x = self.app.shark_center_x()
        shark_y = int(self.app.shark_y)
        shark_sprite = self.app.sprites.get("shark")
        if shark_sprite is not None:
            self.app.screen.blit(shark_sprite, shark_sprite.get_rect(center=(shark_x, shark_y)))
            return
        pygame.draw.ellipse(self.app.screen, (170, 181, 190), (shark_x - self.app.sx(88), shark_y - self.app.sy(34), self.app.sx(176), self.app.sy(68)))

    def draw_entity(self, entity: Entity) -> None:
        x = int(entity.x)
        y = self.app.lane_center(entity.lane)
        if entity.kind == "trash":
            trash_sprites = self.app.sprites.get("trash", [])
            if trash_sprites:
                sprite = trash_sprites[entity.variant % len(trash_sprites)]
                self.app.screen.blit(sprite, sprite.get_rect(center=(x, y)))
                return
            pygame.draw.circle(self.app.screen, WHITE, (x, y), self.app.ss(16))
            return
        if entity.kind == "mine":
            pygame.draw.circle(self.app.screen, (74, 88, 97), (x, y), self.app.ss(24))
            for dx, dy in [(-25, 0), (25, 0), (0, -25), (0, 25), (-18, -18), (18, 18)]:
                pygame.draw.line(self.app.screen, RED, (x, y), (x + self.app.sx(dx), y + self.app.sy(dy)), self.app.ss(4))
            return
        if entity.kind == "net":
            net_sprites = self.app.sprites.get("net", [])
            if net_sprites:
                sprite = net_sprites[entity.variant % len(net_sprites)]
                self.app.screen.blit(sprite, sprite.get_rect(center=(x, y)))
                return
            pygame.draw.rect(self.app.screen, WHITE, (x - self.app.sx(20), y - self.app.sy(20), self.app.sx(40), self.app.sy(40)), 2)
            return
        coral_sprites = self.app.sprites.get("coral", [])
        if coral_sprites:
            sprite = coral_sprites[entity.variant % len(coral_sprites)]
            self.app.screen.blit(sprite, sprite.get_rect(center=(x, y)))
            return
        pygame.draw.polygon(
            self.app.screen,
            (173, 91, 64),
            [(x - self.app.sx(34), y + self.app.sy(28)), (x - self.app.sx(8), y - self.app.sy(30)), (x + self.app.sx(16), y - self.app.sy(6)), (x + self.app.sx(34), y + self.app.sy(30))],
        )

    def draw_shark_warning(self) -> None:
        effective_range = max(1, SHARK_DISTANCE_START - SHARK_CATCH_DISTANCE)
        effective_distance = max(0.0, self.app.shark_distance - SHARK_CATCH_DISTANCE)
        ratio = max(0.0, min(1.0, effective_distance / effective_range))
        bar_width = int((self.app.width - self.app.sx(40)) * ratio)
        pygame.draw.rect(self.app.screen, (31, 55, 77), (self.app.sx(20), self.app.sy(20), self.app.width - self.app.sx(40), self.app.sy(24)), border_radius=self.app.ss(8))
        pygame.draw.rect(self.app.screen, RED if ratio < 0.35 else GREEN, (self.app.sx(20), self.app.sy(20), bar_width, self.app.sy(24)), border_radius=self.app.ss(8))
        shark_x = self.app.sx(20) + bar_width
        pygame.draw.polygon(self.app.screen, (210, 220, 228), [(shark_x, self.app.sy(56)), (shark_x - self.app.sx(24), self.app.sy(42)), (shark_x - self.app.sx(24), self.app.sy(70))])
        pygame.draw.polygon(self.app.screen, (210, 220, 228), [(shark_x - self.app.sx(24), self.app.sy(56)), (shark_x - self.app.sx(48), self.app.sy(42)), (shark_x - self.app.sx(48), self.app.sy(70))])

    def draw_hud(self) -> None:
        self.app.screen.blit(self.app.font.render(f"Skor: {int(self.app.score)}", True, WHITE), (self.app.sx(20), self.app.sy(74)))
        self.app.screen.blit(self.app.small_font.render(f"Sampah: {self.app.trash_collected}", True, WHITE), (self.app.sx(20), self.app.sy(108)))
        self.app.screen.blit(self.app.small_font.render(f"High Score: {self.app.top_score()}", True, WHITE), (self.app.sx(20), self.app.sy(136)))
        self.draw_shark_warning()

    def draw_panel(self, title: str, lines: list[str], footer: str | None = None) -> pygame.Rect:
        panel = pygame.Rect(self.app.sx(92), self.app.sy(68), self.app.width - self.app.sx(184), self.app.height - self.app.sy(136))
        overlay = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
        overlay.fill((4, 8, 14, 176))
        self.app.screen.blit(overlay, (0, 0))

        shadow = panel.move(self.app.sx(10), self.app.sy(12))
        pygame.draw.rect(self.app.screen, (3, 10, 18), shadow, border_radius=self.app.ss(26))
        pygame.draw.rect(self.app.screen, PANEL, panel, border_radius=self.app.ss(26))
        pygame.draw.rect(self.app.screen, CREDIT, panel, self.app.ss(2), border_radius=self.app.ss(26))

        header = pygame.Rect(panel.x, panel.y, panel.width, self.app.sy(98))
        pygame.draw.rect(self.app.screen, PANEL_ALT, header, border_top_left_radius=self.app.ss(26), border_top_right_radius=self.app.ss(26))
        pygame.draw.line(self.app.screen, CREDIT, (panel.x + self.app.sx(28), header.bottom), (panel.right - self.app.sx(28), header.bottom), self.app.ss(2))
        self.app.screen.blit(self.app.title_font.render(title, True, WHITE), (panel.x + self.app.sx(32), panel.y + self.app.sy(22)))

        y = header.bottom + self.app.sy(26)
        for line in lines:
            self.app.screen.blit(self.app.small_font.render(line, True, WHITE), (panel.x + self.app.sx(34), y))
            y += self.app.sy(34)

        if footer:
            footer_surface = self.app.small_font.render(footer, True, CREDIT)
            self.app.screen.blit(footer_surface, (panel.x + self.app.sx(34), panel.bottom - self.app.sy(44)))
        return panel

    def draw_menu_button(self, rect: pygame.Rect, label: str, selected: bool, prefix: str | None = None, disabled: bool = False) -> None:
        bg = (22, 30, 38) if disabled else (PANEL_ALT if selected else (10, 31, 49))
        border = (90, 108, 120) if disabled else (YELLOW if selected else CREDIT)
        pygame.draw.rect(self.app.screen, bg, rect, border_radius=self.app.ss(14))
        pygame.draw.rect(self.app.screen, border, rect, self.app.ss(2), border_radius=self.app.ss(14))

        if selected:
            accent = pygame.Rect(rect.x + self.app.sx(10), rect.y + self.app.sy(8), self.app.sx(6), rect.height - self.app.sy(16))
            pygame.draw.rect(self.app.screen, YELLOW, accent, border_radius=self.app.ss(4))

        text_x = rect.x + self.app.sx(28)
        label_color = (128, 140, 152) if disabled else (WHITE if not selected else YELLOW)
        label_surface = self.app.medium_font.render(label, True, label_color)
        if prefix:
            prefix_color = (120, 132, 142) if disabled else (YELLOW if selected else CREDIT)
            prefix_surface = self.app.small_font.render(prefix, True, prefix_color)
            self.app.screen.blit(prefix_surface, (text_x, rect.y + self.app.sy(6)))
            self.app.screen.blit(label_surface, (text_x, rect.y + self.app.sy(24)))
        else:
            label_rect = label_surface.get_rect()
            label_rect.midleft = (text_x, rect.centery)
            self.app.screen.blit(label_surface, label_rect)

    def draw_info_card(self, rect: pygame.Rect, title: str, lines: list[str]) -> None:
        pygame.draw.rect(self.app.screen, (8, 28, 44), rect, border_radius=self.app.ss(18))
        pygame.draw.rect(self.app.screen, CREDIT, rect, self.app.ss(2), border_radius=self.app.ss(18))
        self.app.screen.blit(self.app.medium_font.render(title, True, WHITE), (rect.x + self.app.sx(22), rect.y + self.app.sy(18)))
        y = rect.y + self.app.sy(56)
        for line in lines:
            self.app.screen.blit(self.app.small_font.render(line, True, CREDIT), (rect.x + self.app.sx(22), y))
            y += self.app.sy(30)

    def draw_stat_chip(self, x: int, y: int, label: str, value: str) -> None:
        rect = pygame.Rect(x, y, self.app.sx(182), self.app.sy(76))
        pygame.draw.rect(self.app.screen, (8, 29, 45), rect, border_radius=self.app.ss(18))
        pygame.draw.rect(self.app.screen, CREDIT, rect, self.app.ss(2), border_radius=self.app.ss(18))
        self.app.screen.blit(self.app.small_font.render(label, True, CREDIT), (rect.x + self.app.sx(18), rect.y + self.app.sy(12)))
        self.app.screen.blit(self.app.medium_font.render(value, True, WHITE), (rect.x + self.app.sx(18), rect.y + self.app.sy(36)))

    def draw_menu(self) -> None:
        footer = "Gunakan panah atas/bawah lalu Enter untuk memilih." if not self.app.menu_from_pause else "Menu pause. Resume di paling atas, aksi destruktif butuh konfirmasi."
        panel = self.draw_panel("Ocean Cleanup Runner", ["Bersihkan laut, hindari hiu, dan pecahkan rekor tertinggi."], footer)

        left_col_x = panel.x + self.app.sx(34)
        right_col_x = panel.x + self.app.sx(520)
        content_top = panel.y + self.app.sy(176)

        self.draw_stat_chip(right_col_x, panel.y + self.app.sy(18), "TOP SCORE", str(self.app.top_score()))
        self.draw_stat_chip(right_col_x + self.app.sx(196), panel.y + self.app.sy(18), "TARGET", "NEW BEST")

        label_map = {
            "RESUME": "Lanjutkan run saat ini",
            "PLAY": "Mulai run baru" if not self.app.menu_from_pause else "Mulai ulang run ini",
            "GUIDE": "Kontrol dan aturan",
            "HIGH SCORE": "Rekor tersimpan",
            "SETTINGS": "Audio dan data",
            "EXIT": "Keluar dari game",
        }
        labels = []
        for item in self.app.current_menu_items():
            display = "RESTART" if self.app.menu_from_pause and item == "PLAY" else item
            labels.append((display, label_map[item], item))
        for index, (label, prefix, _item) in enumerate(labels):
            rect = pygame.Rect(left_col_x, content_top + index * self.app.sy(72), self.app.sx(390), self.app.sy(60))
            self.draw_menu_button(rect, label, index == self.app.menu_index, prefix)

        info_rect = pygame.Rect(right_col_x, content_top, panel.right - right_col_x - self.app.sx(34), self.app.sy(330))
        info_lines = [
            "Kumpulkan sampah sebanyak mungkin.",
            "Hindari ranjau, jaring, dan karang.",
            "Sampah menjauhkan hiu. Rintangan mendekatkan hiu.",
            "Target utamanya: cetak high score terbaru.",
        ]
        if self.app.menu_from_pause:
            info_lines = [
                "Run sedang dipause.",
                "RESUME akan melanjutkan dengan countdown 3 detik.",
                "PLAY akan memulai run baru dan menghapus progres run ini.",
                "Reset high score dinonaktifkan saat pause menu aktif.",
            ]
        self.draw_info_card(info_rect, "Mission Brief" if not self.app.menu_from_pause else "Pause Brief", info_lines)

    def draw_guide(self) -> None:
        panel = self.draw_panel("Guide", [], "ESC untuk kembali ke menu.")
        guide_rect = pygame.Rect(panel.x + self.app.sx(34), panel.y + self.app.sy(126), panel.width - self.app.sx(68), self.app.sy(360))
        self.draw_info_card(
            guide_rect,
            "Cara Main",
            [
                "1. Gunakan W/S atau panah atas/bawah untuk pindah lajur.",
                "2. Ambil sampah untuk menambah skor dan menjauhkan hiu.",
                "3. Hindari rintangan karena hiu akan lebih cepat mendekat.",
                "4. Baca indikator hiu di atas untuk menilai bahaya.",
                "5. Mainkan beberapa run untuk memecahkan high score terbaik.",
            ],
        )

    def draw_scores(self) -> None:
        panel = self.draw_panel("High Score", [], "Data disimpan di records.dat. ESC untuk kembali.")
        table = pygame.Rect(panel.x + self.app.sx(34), panel.y + self.app.sy(126), panel.width - self.app.sx(68), self.app.sy(400))
        pygame.draw.rect(self.app.screen, (8, 28, 44), table, border_radius=self.app.ss(18))
        pygame.draw.rect(self.app.screen, CREDIT, table, self.app.ss(2), border_radius=self.app.ss(18))

        header_y = table.y + self.app.sy(18)
        self.app.screen.blit(self.app.medium_font.render("Rank", True, WHITE), (table.x + self.app.sx(24), header_y))
        self.app.screen.blit(self.app.medium_font.render("Score", True, WHITE), (table.x + self.app.sx(120), header_y))
        self.app.screen.blit(self.app.medium_font.render("Date", True, WHITE), (table.x + self.app.sx(250), header_y))
        pygame.draw.line(self.app.screen, CREDIT, (table.x + self.app.sx(20), table.y + self.app.sy(56)), (table.right - self.app.sx(20), table.y + self.app.sy(56)), self.app.ss(2))

        sorted_records = sorted(self.app.records, key=lambda item: int(item["score"]), reverse=True)[:10]
        if not sorted_records:
            self.app.screen.blit(self.app.small_font.render("Belum ada record. Main dulu untuk membuat high score pertama.", True, CREDIT), (table.x + self.app.sx(24), table.y + self.app.sy(92)))
        else:
            for index, record in enumerate(sorted_records, start=1):
                row_y = table.y + self.app.sy(74) + (index - 1) * self.app.sy(32)
                self.app.screen.blit(self.app.small_font.render(f"#{index:02d}", True, WHITE), (table.x + self.app.sx(24), row_y))
                self.app.screen.blit(self.app.small_font.render(str(int(record["score"])), True, YELLOW), (table.x + self.app.sx(120), row_y))
                self.app.screen.blit(self.app.small_font.render(str(record["date"]), True, CREDIT), (table.x + self.app.sx(250), row_y))

    def draw_settings(self) -> None:
        panel = self.draw_panel("Settings", ["Atur audio dan data progress dari sini."], "Enter untuk ubah. ESC untuk kembali.")
        list_rect = pygame.Rect(panel.x + self.app.sx(34), panel.y + self.app.sy(164), panel.width - self.app.sx(68), self.app.sy(320))
        items = [
            f"SFX: {'ON' if self.app.settings['sfx_enabled'] else 'OFF'}",
            f"MUSIC: {'ON' if self.app.settings['music_enabled'] else 'OFF'}",
            "RESET HIGH SCORE",
            "CREDIT",
            "BACK",
        ]
        for index, label in enumerate(items):
            rect = pygame.Rect(list_rect.x, list_rect.y + index * self.app.sy(58), list_rect.width, self.app.sy(46))
            disabled = self.app.menu_from_pause and label == "RESET HIGH SCORE"
            self.draw_menu_button(rect, label, index == self.app.settings_index, disabled=disabled)

        if self.app.pending_reset_confirm:
            notice = self.app.small_font.render("Tekan Enter sekali lagi untuk reset high score.", True, YELLOW)
            self.app.screen.blit(notice, (panel.x + self.app.sx(34), panel.bottom - self.app.sy(78)))

    def draw_credit(self) -> None:
        panel = self.draw_panel("Credit", [], "ESC untuk kembali.")
        credit_rect = pygame.Rect(panel.x + self.app.sx(34), panel.y + self.app.sy(126), panel.width - self.app.sx(68), self.app.sy(300))
        self.draw_info_card(
            credit_rect,
            "Credits",
            [
                "Concept & Direction: You",
                "Implementation: Codex",
                "Engine: Python + pygame",
                "Art Assets: custom assets dari folder assets/",
                "Audio: generated in-game untuk menu, SFX, dan backsound.",
            ],
        )

    def draw_game_over(self) -> None:
        lines = [f"Skor akhir: {self.app.last_score}", f"Sampah terkumpul: {self.app.trash_collected}", f"High score saat ini: {self.app.top_score()}"]
        if self.app.last_run_was_highscore:
            lines.insert(1, "High score baru berhasil dibuat.")
        self.draw_panel("Game Over", lines, "Enter untuk kembali ke menu, R untuk main lagi.")

    def draw_countdown(self) -> None:
        self.draw_shark()
        for entity in self.app.entities:
            self.draw_entity(entity)
        self.draw_player()
        self.draw_hud()
        overlay = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
        overlay.fill((4, 8, 14, 120))
        self.app.screen.blit(overlay, (0, 0))
        count = max(1, int(self.app.resume_countdown) + (0 if self.app.resume_countdown.is_integer() else 1))
        circle_rect = pygame.Rect(0, 0, self.app.sx(150), self.app.sx(150))
        circle_rect.center = (self.app.width // 2, self.app.height // 2)
        pygame.draw.ellipse(self.app.screen, PANEL_ALT, circle_rect)
        pygame.draw.ellipse(self.app.screen, YELLOW, circle_rect, self.app.ss(3))
        number = self.app.title_font.render(str(count), True, WHITE)
        self.app.screen.blit(number, number.get_rect(center=circle_rect.center))
        hint = self.app.small_font.render("Bersiap...", True, CREDIT)
        self.app.screen.blit(hint, hint.get_rect(center=(self.app.width // 2, self.app.height // 2 + self.app.sy(72))))

    def draw_confirmation(self) -> None:
        overlay = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.app.screen.blit(overlay, (0, 0))
        box = pygame.Rect(self.app.sx(240), self.app.sy(220), self.app.width - self.app.sx(480), self.app.sy(180))
        pygame.draw.rect(self.app.screen, PANEL, box, border_radius=self.app.ss(20))
        pygame.draw.rect(self.app.screen, YELLOW, box, self.app.ss(2), border_radius=self.app.ss(20))
        title = self.app.medium_font.render("Konfirmasi", True, WHITE)
        msg = self.app.small_font.render(self.app.confirm_message, True, WHITE)
        hint = self.app.small_font.render("Enter untuk lanjut, ESC untuk batal.", True, CREDIT)
        self.app.screen.blit(title, title.get_rect(center=(box.centerx, box.y + self.app.sy(38))))
        self.app.screen.blit(msg, msg.get_rect(center=(box.centerx, box.y + self.app.sy(86))))
        self.app.screen.blit(hint, hint.get_rect(center=(box.centerx, box.y + self.app.sy(132))))

    def draw(self) -> None:
        self.draw_background()
        if self.app.state == "playing":
            self.draw_shark()
            for entity in self.app.entities:
                self.draw_entity(entity)
            self.draw_player()
            self.draw_hud()
            if self.app.hit_flash > 0:
                flash = pygame.Surface((self.app.width, self.app.height), pygame.SRCALPHA)
                flash.fill((255, 70, 70, 42))
                self.app.screen.blit(flash, (0, 0))
        elif self.app.state == "countdown":
            self.draw_countdown()
        elif self.app.state == "menu":
            self.draw_menu()
        elif self.app.state == "guide":
            self.draw_guide()
        elif self.app.state == "scores":
            self.draw_scores()
        elif self.app.state == "settings":
            self.draw_settings()
        elif self.app.state == "credits":
            self.draw_credit()
        elif self.app.state == "game_over":
            self.draw_game_over()

        if self.app.confirm_action is not None:
            self.draw_confirmation()
        pygame.display.flip()
