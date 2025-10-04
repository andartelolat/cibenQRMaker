# qr_app.py
from flask import Flask, request, render_template_string
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
import base64

app = Flask(__name__)

# ========= Template (Tailwind + Alpine, Notion-like theme) =========
HTML = r"""
<!doctype html>
<html lang="id" x-data="qrApp()" :class="darkMode ? 'dark' : ''">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="theme-color" content="#ffffff" />
  <title>Ciben QR Maker</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
  <style>
    /* ===== Notion-ish design tokens ===== */
    :root{
      --bg:        #fbfbfa;    /* halaman */
      --card:      #ffffff;    /* permukaan card */
      --border:    #e7e7e5;    /* garis lembut */
      --text:      #1f2328;    /* teks utama */
      --text-dim:  #5b5f66;    /* teks sekunder */
      --accent:    #111827;    /* tombol/aksi */
      --accent-2:  #2b2f36;
      --ring:      #6b7280;    /* fokus ring */
      --link:      #2563eb;
    }
    .dark:root{
      --bg:        #191919;
      --card:      #1f1f1f;
      --border:    #2a2a2a;
      --text:      #e6e6e6;
      --text-dim:  #a7a7a7;
      --accent:    #e6e6e6;
      --accent-2:  #d1d1d1;
      --ring:      #94a3b8;
      --link:      #60a5fa;
    }

    html, body { background: var(--bg); color: var(--text); }

    /* Page container (Notion-style width) */
    .page-wrap { max-width: 900px; margin-left: auto; margin-right: auto; }

    /* App bar minimal */
    .appbar{
      position: sticky; top: 0; z-index: 40;
      backdrop-filter: saturate(1) blur(6px);
      background: color-mix(in oklab, var(--bg), transparent 8%);
      border-bottom: 1px solid var(--border);
    }
    .brand-dot{
      width: 26px; height: 26px; border-radius: 6px;
      background: #111827; color: #fff; display: grid; place-items: center; font-weight: 700;
    }
    .dark .brand-dot{ background: #e6e6e6; color: #111827; }

    /* Notion-like card */
    .card{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
    }

    /* Inputs */
    .inpt{
      width: 100%;
      background: color-mix(in oklab, var(--card), transparent 0%);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      color: var(--text);
      outline: none;
    }
    .inpt:focus{
      border-color: var(--ring);
      box-shadow: 0 0 0 2px color-mix(in oklab, var(--ring), transparent 70%);
    }
    .inpt::placeholder{ color: var(--text-dim); }

    /* Labels & small text */
    .label{ font-size: 13px; color: var(--text-dim); font-weight: 600; }
    .muted{ font-size: 12px; color: var(--text-dim); }

    /* Buttons (neutral/blackish) */
    .btn{
      display:inline-flex; align-items:center; justify-content:center; gap:8px;
      padding: 10px 14px; border-radius: 10px; font-weight: 600;
      border: 1px solid var(--border); background: var(--accent); color: #fff;
      transition: transform .1s ease, box-shadow .15s ease, background .15s ease;
    }
    .btn:hover{ transform: translateY(-1px); box-shadow: 0 6px 14px rgba(0,0,0,.08); background: var(--accent-2); }
    .btn:active{ transform: translateY(0); }

    /* Secondary button */
    .btn-sec{
      background: transparent; color: var(--text);
      border: 1px solid var(--border);
    }
    .btn-sec:hover{ background: color-mix(in oklab, var(--card), transparent 92%); }

    /* Link */
    a.link{ color: var(--link); }

    /* Checkerboard untuk preview transparan (sangat halus) */
    .checker {
      background-image:
        linear-gradient(45deg, #eaeaea 25%, transparent 25%),
        linear-gradient(-45deg, #eaeaea 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #eaeaea 75%),
        linear-gradient(-45deg, transparent 75%, #eaeaea 75%);
      background-size: 14px 14px;
      background-position: 0 0, 0 7px, 7px -7px, -7px 0px;
      border-radius: 10px;
    }
    .dark .checker {
      background-image:
        linear-gradient(45deg, #242424 25%, transparent 25%),
        linear-gradient(-45deg, #242424 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #242424 75%),
        linear-gradient(-45deg, transparent 75%, #242424 75%);
    }

    /* Divider halus */
    .divider{ height:1px; background: var(--border); }

    /* Reduce motion friendly */
    @media (prefers-reduced-motion: reduce){
      .btn{ transition: none }
    }
  </style>
</head>
<body>
  <!-- App Bar -->
  <header class="appbar">
    <div class="page-wrap px-5 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="brand-dot">QR</div>
        <div>
          <div class="text-[13px] text-[color:var(--text-dim)]">by Cibens</div>
          <div class="font-semibold leading-tight">Maker</div>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button @click="toggleTheme" class="btn-sec px-3 py-2 rounded-lg text-sm">
          <span x-show="!darkMode">🌙</span><span x-show="darkMode">☀️</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Page Content -->
  <main class="page-wrap px-5 py-6">
    <!-- Title like Notion page title -->
    <h1 class="text-3xl font-semibold mb-4 tracking-[-0.01em]">QR Maker</h1>
    <div class="muted mb-6">Generate QR code dengan gaya simple ala Notion. Dukung warna, rounded modules, logo tengah, dan download PNG.</div>

    <!-- Main Card -->
    <div class="card">
      <form id="qrForm" method="POST" enctype="multipart/form-data" class="p-5 grid md:grid-cols-2 gap-6" @submit="loading=true">
        <!-- Controls -->
        <section class="space-y-5">
          <div>
            <label class="label mb-1 block">Data / URL</label>
            <textarea name="data" rows="3" placeholder="https://contoh.com / Teks apa saja" class="inpt" required>{{ data or '' }}</textarea>
            <div class="muted mt-1">Masukkan URL atau teks apa pun yang ingin dijadikan QR.</div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label mb-1 block">Ukuran (px)</label>
              <input type="number" name="size" min="128" max="2048" value="{{ size or 768 }}" class="inpt">
            </div>
            <div>
              <label class="label mb-1 block">Margin (modul)</label>
              <input type="number" name="border" min="0" max="8" value="{{ border or 4 }}" class="inpt">
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label mb-1 block">Warna QR</label>
              <input type="color" name="fg" value="{{ fg or '#111827' }}" class="inpt h-10 p-1">
            </div>
            <div>
              <label class="label mb-1 block">Background</label>
              <div class="flex gap-2">
                <input type="color" name="bg" value="{{ bg or '#ffffff' }}" class="inpt h-10 p-1">
                <label class="inline-flex items-center gap-2 text-xs px-3 rounded-lg border" style="border-color:var(--border);">
                  <input type="checkbox" name="transparent" {% if transparent %}checked{% endif %}> Transparan
                </label>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label mb-1 block">Error Correction</label>
              <select name="ecc" class="inpt">
                {% for code,label in [('L','L (7%)'),('M','M (15%)'),('Q','Q (25%)'),('H','H (30%)')] %}
                  <option value="{{ code }}" {% if ecc==code or (not ecc and code=='H') %}selected{% endif %}>{{ label }}</option>
                {% endfor %}
              </select>
            </div>
            <div>
              <label class="label mb-1 block">Rounded Modules</label>
              <select name="rounded" class="inpt">
                <option value="0" {% if not rounded %}selected{% endif %}>Off (kotak)</option>
                <option value="1" {% if rounded %}selected{% endif %}>On (membulat)</option>
              </select>
            </div>
          </div>

          <div>
            <label class="label mb-1 block">Logo (opsional)</label>
            <input type="file" name="logo" accept="image/*" class="inpt">
            <div class="grid grid-cols-2 gap-3 mt-2">
              <div>
                <label class="label mb-1 block">Ukuran Logo (%)</label>
                <input type="number" name="logo_pct" min="10" max="40" value="{{ logo_pct or 24 }}" class="inpt">
              </div>
              <div class="flex items-end gap-3">
                <label class="inline-flex items-center gap-2 text-xs px-3 py-2 rounded-lg border" style="border-color:var(--border);">
                  <input type="checkbox" name="logo_circle" {% if logo_circle %}checked{% endif %}> Bulatkan logo
                </label>
                <label class="inline-flex items-center gap-2 text-xs px-3 py-2 rounded-lg border" style="border-color:var(--border);">
                  <input type="checkbox" name="logo_border" {% if logo_border or logo_border is not defined %}checked{% endif %}> Border putih
                </label>
              </div>
            </div>
          </div>

          <div class="flex gap-2">
            <button type="submit" :disabled="loading" class="btn">
              <svg x-show="loading" class="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg>
              <span x-text="loading ? 'Membuat…' : 'Generate QR'"></span>
            </button>
            <a href="https://github.com/andartelolat" target="_blank" class="btn btn-sec">Repo</a>
          </div>
        </section>

        <!-- Preview -->
        <section class="space-y-4">
          <div class="label">Preview</div>
          <div class="checker grid place-items-center min-h-[320px] p-3">
            {% if qr_data_url %}
              <img src="{{ qr_data_url }}" alt="QR Preview" class="max-w-full h-auto rounded-lg" style="border:1px solid var(--border)">
            {% else %}
              <div class="muted text-center px-6">
                Isi data lalu klik <b>Generate QR</b>. Logo di tengah (opsional) akan otomatis disesuaikan.
              </div>
            {% endif %}
          </div>

          {% if qr_data_url %}
          <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2">
            <div class="muted">
              PNG siap diunduh. Ukuran akhir: <b style="color:var(--text)">{{ rendered_w }} × {{ rendered_h }}</b> px
            </div>
            <a download="qr.png" href="{{ qr_data_url }}" class="btn">⬇️ Download PNG</a>
          </div>
          {% endif %}
        </section>
      </form>
      <div class="divider"></div>
      <div class="px-5 py-4 muted">
        Tip: Warna QR kontras tinggi (gelap di atas terang) memudahkan pemindaian. Untuk latar transparan, gunakan logo dengan border putih.
      </div>
    </div>
  </main>

  <script>
    function qrApp(){
      return {
        loading:false,
        darkMode:(() => {
          const saved=localStorage.getItem('theme');
          if(saved==='dark') return true;
          if(saved==='light') return false;
          return window.matchMedia('(prefers-color-scheme: dark)').matches;
        })(),
        toggleTheme(){
          this.darkMode=!this.darkMode;
          localStorage.setItem('theme', this.darkMode?'dark':'light');
          const meta=document.querySelector('meta[name="theme-color"]');
          if(meta) meta.setAttribute('content', this.darkMode ? '#191919' : '#ffffff');
        }
      }
    }
    // Sync theme-color on load
    (function(){
      const saved=localStorage.getItem('theme');
      const isDark = saved ? saved==='dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
      const meta=document.querySelector('meta[name="theme-color"]');
      if(meta) meta.setAttribute('content', isDark ? '#191919' : '#ffffff');
    })();
  </script>
</body>
</html>
"""

# ========= util warna =========
def _hex_to_rgb(c: str, default=(0, 0, 0)):
  """Terima '#RGB' / '#RRGGBB' / '#RRGGBBAA' dan kembalikan (R,G,B)."""
  if not isinstance(c, str):
      return default
  s = c.strip()
  if s.startswith("#"): s = s[1:]
  try:
      if len(s) == 3:   # #RGB
          r = int(s[0]*2, 16); g = int(s[1]*2, 16); b = int(s[2]*2, 16)
          return (r, g, b)
      if len(s) in (6, 8):  # #RRGGBB or #RRGGBBAA
          r = int(s[0:2], 16); g = int(s[2:4], 16); b = int(s[4:6], 16)
          return (r, g, b)
  except Exception:
      pass
  return default

# ========= QR helpers =========
def generate_qr_image(
    data: str,
    size_px: int = 768,
    border: int = 4,
    fg: str = "#111827",
    bg: str = "#ffffff",
    transparent: bool = False,
    ecc: str = "H",
    rounded: bool = True,
    logo_file=None,
    logo_pct: int = 24,
    logo_circle: bool = True,
    logo_border: bool = True,
):
    """Return PIL Image (RGBA) of QR dengan warna kustom & logo opsional di tengah."""
    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }
    ec_level = ec_map.get(ecc.upper(), qrcode.constants.ERROR_CORRECT_H)

    qr = qrcode.QRCode(
        version=None,               # auto
        error_correction=ec_level,
        box_size=10,                # nanti resize ke size_px
        border=max(0, int(border)),
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Drawer + warna
    drawer = RoundedModuleDrawer() if rounded else SquareModuleDrawer()
    front_rgb = _hex_to_rgb(fg, (17, 24, 39))          # slate-900
    back_color = (255, 255, 255, 0) if transparent else _hex_to_rgb(bg, (255, 255, 255))

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer,
        color_mask=SolidFillColorMask(front_color=front_rgb, back_color=back_color),
    ).convert("RGBA")

    # Scale ke size_px (nearest menjaga ketajaman modul)
    if size_px and size_px > 0:
        img = img.resize((size_px, size_px), Image.NEAREST)

    # ===== Overlay logo (opsional) =====
    if logo_file and getattr(logo_file, "filename", ""):
        try:
            logo = Image.open(logo_file.stream).convert("RGBA")
            pct = max(10, min(logo_pct, 40)) / 100.0
            target = int(min(img.size) * pct)
            logo = ImageOps.contain(logo, (target, target))

            # Bulatkan logo
            if logo_circle:
                mask = Image.new("L", logo.size, 0)
                d = ImageDraw.Draw(mask)
                d.ellipse((0, 0, logo.size[0], logo.size[1]), fill=255)
                logo = ImageOps.fit(logo, logo.size, centering=(0.5, 0.5))
                logo.putalpha(mask)

            # Border putih agar tetap kebaca
            if logo_border:
                pad = max(4, target // 12)
                bg_size = (logo.size[0] + pad * 2, logo.size[1] + pad * 2)
                has_alpha_bg = isinstance(back_color, tuple) and len(back_color) == 4
                bg_img = Image.new("RGBA", bg_size, (255, 255, 255, 255 if not has_alpha_bg else 230))
                if logo_circle:
                    m = Image.new("L", bg_size, 0)
                    d = ImageDraw.Draw(m)
                    d.ellipse((0, 0, bg_size[0], bg_size[1]), fill=255)
                    bg_img.putalpha(m)
                bg_img.paste(logo, (pad, pad), logo)
                logo = bg_img

            # Tempel di tengah
            lx = (img.size[0] - logo.size[0]) // 2
            ly = (img.size[1] - logo.size[1]) // 2
            img.alpha_composite(logo, (lx, ly))
        except Exception:
            pass

    return img

def pil_to_data_url(pil_img: Image.Image):
    bio = BytesIO()
    pil_img.save(bio, format="PNG")
    b64 = base64.b64encode(bio.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}", pil_img.width, pil_img.height

# ========= Routes =========
@app.route("/", methods=["GET", "POST"])
def index():
    qr_data_url = None
    rendered_w = rendered_h = None

    # defaults context
    ctx = dict(
        data="",
        size=768,
        border=4,
        fg="#111827",
        bg="#ffffff",
        transparent=False,
        ecc="H",
        rounded=True,
        logo_pct=24,
        logo_circle=True,
        logo_border=True,
    )

    if request.method == "POST":
        data = (request.form.get("data") or "").strip()
        size = int(request.form.get("size", ctx["size"]))
        border = int(request.form.get("border", ctx["border"]))
        fg = request.form.get("fg", ctx["fg"])
        bg = request.form.get("bg", ctx["bg"])
        transparent = request.form.get("transparent") == "on"
        ecc = request.form.get("ecc", ctx["ecc"])
        rounded = request.form.get("rounded", "1") == "1"
        logo = request.files.get("logo")
        logo_pct = int(request.form.get("logo_pct", ctx["logo_pct"]))
        logo_circle = request.form.get("logo_circle") == "on"
        logo_border = (request.form.get("logo_border") == "on") if ("logo_border" in request.form) else True

        ctx.update(dict(
            data=data, size=size, border=border, fg=fg, bg=bg,
            transparent=transparent, ecc=ecc, rounded=rounded,
            logo_pct=logo_pct, logo_circle=logo_circle, logo_border=logo_border
        ))

        if data:
            try:
                img = generate_qr_image(
                    data=data, size_px=size, border=border, fg=fg, bg=bg,
                    transparent=transparent, ecc=ecc, rounded=rounded,
                    logo_file=logo, logo_pct=logo_pct, logo_circle=logo_circle, logo_border=logo_border
                )
                qr_data_url, rendered_w, rendered_h = pil_to_data_url(img)
            except Exception as e:
                # tampilkan error ringan via SVG inline
                msg = f"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='200'><rect width='100%%' height='100%%' fill='mistyrose'/><text x='50%%' y='50%%' dominant-baseline='middle' text-anchor='middle' font-family='monospace' font-size='14'>Terjadi kesalahan: {str(e).replace('<','&lt;')}</text></svg>"
                qr_data_url = msg

    return render_template_string(
        HTML,
        qr_data_url=qr_data_url,
        rendered_w=rendered_w,
        rendered_h=rendered_h,
        **ctx
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
