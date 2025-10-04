# Ciben QR Maker — Notion Theme

Generator QR code berbasis **Flask** dengan tampilan **minimalis ala Notion**. Mendukung:
- 🎨 **Warna kustom** (QR & background), **mode transparan**
- ◻️ **Rounded modules** (opsional)
- 🖼️ **Logo di tengah** (opsional, bisa dibulatkan & diberi border)
- 🧰 **Error correction** (L/M/Q/H)
- 🧩 **Preview** dengan checkerboard halus (agar QR transparan tetap terlihat)
- ⬇️ **Unduh PNG** ukuran penuh
- 🌓 **Light/Dark** mengikuti preferensi OS + toggle
- 📱 **Mobile-first** & ringan

> UI dibuat tanpa framework frontend berat; hanya **Tailwind CDN** + **Alpine.js** kecil untuk interaksi (loading state & theme).

---

## Demo Lokal

```bash
# 1) Siapkan environment
python -m venv .venv
# Windows: .venv\Scripts\Activate
# macOS/Linux: source .venv/bin/activate

# 2) Install dependensi
pip install flask qrcode[pil] pillow

# 3) Jalankan
python qr_app.py

# 4) Buka di browser
http://localhost:5001/

Fitur & Opsi

Data / URL
Masukkan teks bebas atau tautan apa saja.

Ukuran (px) & Margin (modul)
Atur resolusi gambar PNG dan margin modul QR.

Warna QR & Background
Pilih warna; aktifkan “Transparan” jika ingin latar tembus pandang (preview tetap terlihat berkat checkerboard).
Tips: gunakan kontras tinggi (mis. QR gelap di atas latar terang) agar mudah discan.

Error Correction (L/M/Q/H)
Gunakan H (30%) bila menambahkan logo agar tetap terbaca.

Rounded Modules
Modul QR dengan sudut membulat agar tampil lebih modern.

Logo Tengah (opsional)
Unggah PNG/JPG/WebP (raster). Opsi:

Ukuran Logo (%)

Bulatkan logo

Border putih (disarankan untuk latar gelap/kompleks)

Download PNG
Hasil yang sama persis dengan preview.

Tech Stack

Python: Flask, Pillow, qrcode[pil]

UI: Tailwind CDN, Alpine.js (sangat kecil)

Arsitektur: Single-file Flask + template inline (mudah di-deploy & dimodifikasi)

Struktur Proyek
.
├─ qr_app.py        # aplikasi Flask + template Notion-like
├─ README.md        # dokumentasi ini
└─ LICENSE          # lisensi (MIT) © andartelolat

Troubleshooting

QR tidak terlihat → Pastikan warna QR dan background tidak sama.

QR sulit dipindai setelah pakai logo → Perkecil Ukuran Logo (%) atau naikkan Error Correction ke H.

“PIL cannot identify image file” → Format logo tidak valid/korup; coba PNG/JPG/WebP lain.

Tailwind/Alpine tidak termuat (offline) → Ganti CDN dengan salinan lokal (optional), atau sambungkan internet.

Roadmap (opsional)

Ekspor SVG & PDF

Batch generator (CSV → ZIP)

Preset palet warna & tema

Drag-and-drop logo + auto-fit

Kontribusi

Issue/PR sangat diterima!
Standar gaya: ringkas, jelas, tanpa dependensi berat. Sertakan deskripsi perubahan dan alasan teknis.
