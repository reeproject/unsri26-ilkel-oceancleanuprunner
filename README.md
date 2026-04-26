# Ocean Cleanup Runner

Game runner 3 lajur bertema kelautan dengan Python dan `pygame`, dengan arah permainan dari kiri ke kanan.

## Cara menjalankan

```bash
python main.py
```

## Kontrol

- `W` / `Panah Atas`: pindah ke lajur atas
- `S` / `Panah Bawah`: pindah ke lajur bawah
- `R`: ulangi setelah kalah
- `ESC`: keluar

## Aturan game

- Kumpulkan sampah laut untuk menambah skor.
- Hindari ranjau, terumbu, dan jaring.
- Hiu akan terus mendekat seiring waktu.
- Mengambil sampah membuat jarak hiu sedikit menjauh.
- Menabrak rintangan membuat hiu lebih cepat menangkap pemain.
- Generator spawn menjaga agar tidak pernah ada pola yang menutup semua 3 lajur sekaligus.
