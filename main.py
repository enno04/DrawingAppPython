from browser import document, html

# --- Inisialisasi Elemen ---
canvas = document["canvas"]
ctx = canvas.getContext("2d")

mode_select = document["mode"]
color_picker = document["color"]
line_width_input = document["line-width"]
line_width_value_span = document["line-width-value"]

# --- Tombol-tombol Baru ---
clear_button = document["clear-button"]
undo_button = document["undo-button"]
redo_button = document["redo-button"]

# --- Variabel untuk State Management ---
start_x = start_y = None
history = []
history_index = -1

# --- Fungsi-Fungsi ---

def update_line_width_display(evt=None):
    line_width_value_span.text = line_width_input.value

def get_line_width():
    return int(line_width_input.value)

def save_state():
    """Menyimpan state kanvas saat ini ke dalam riwayat."""
    global history, history_index
    # Jika kita melakukan undo lalu menggambar lagi, hapus riwayat redo
    history = history[0:history_index + 1]
    
    # Simpan data gambar kanvas
    image_data = ctx.getImageData(0, 0, canvas.width, canvas.height)
    history.append(image_data)
    history_index += 1
    update_button_states()

def restore_state(index):
    """Mengembalikan kanvas ke state tertentu dari riwayat."""
    if 0 <= index < len(history):
        ctx.putImageData(history[index], 0, 0)
    elif index == -1: # Jika kembali ke state awal (kosong)
        clear_canvas(None, save=False)

def update_button_states():
    """Mengaktifkan/menonaktifkan tombol undo/redo."""
    undo_button.disabled = (history_index <= 0)
    redo_button.disabled = (history_index >= len(history) - 1)

def undo_action(evt):
    """Aksi untuk tombol Undo."""
    global history_index
    if history_index > 0:
        history_index -= 1
        restore_state(history_index)
        update_button_states()

def redo_action(evt):
    """Aksi untuk tombol Redo."""
    global history_index
    if history_index < len(history) - 1:
        history_index += 1
        restore_state(history_index)
        update_button_states()

def mousedown_action(evt):
    """Aksi saat tombol mouse ditekan."""
    global start_x, start_y
    
    ctx.lineWidth = get_line_width()
    ctx.strokeStyle = color_picker.value
    ctx.fillStyle = color_picker.value

    mode = mode_select.value
    x = evt.offsetX
    y = evt.offsetY

    if mode == "dot":
        ctx.beginPath()
        radius = get_line_width() / 2
        ctx.arc(x, y, radius if radius > 0 else 1, 0, 2 * 3.1415)
        ctx.fill()
        save_state() # Simpan state setelah menggambar titik
    else:
        start_x = x
        start_y = y

def mouseup_action(evt):
    """Aksi saat tombol mouse dilepas."""
    global start_x, start_y

    if start_x is None or start_y is None:
        return

    mode = mode_select.value
    x = evt.offsetX
    y = evt.offsetY

    if mode == "line":
        ctx.beginPath()
        ctx.moveTo(start_x, start_y)
        ctx.lineTo(x, y)
        ctx.stroke()
    elif mode == "rect":
        ctx.strokeRect(start_x, start_y, x - start_x, y - start_y)
    elif mode == "circle":
        radius = ((x - start_x) ** 2 + (y - start_y) ** 2) ** 0.5
        ctx.beginPath()
        ctx.arc(start_x, start_y, radius, 0, 2 * 3.1415)
        ctx.stroke()
    elif mode == "ellipse":
        ctx.beginPath()
        ctx.ellipse((start_x + x) / 2, (start_y + y) / 2, abs(x - start_x) / 2, abs(y - start_y) / 2, 0, 0, 2 * 3.1415)
        ctx.stroke()
    
    start_x = start_y = None
    save_state() # Simpan state setelah menggambar bentuk

def clear_canvas(evt, save=True):
    """Membersihkan seluruh isi kanvas."""
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    if save:
        save_state()

# --- Pemasangan Event Listener ---
line_width_input.bind("input", update_line_width_display)
canvas.bind("mousedown", mousedown_action)
canvas.bind("mouseup", mouseup_action)
clear_button.bind("click", clear_canvas)
undo_button.bind("click", undo_action)
redo_button.bind("click", redo_action)

# --- Inisialisasi Awal ---
def initial_setup():
    """Menyiapkan state awal saat aplikasi dimuat."""
    update_line_width_display()
    save_state() # Simpan state awal (kanvas kosong)
    update_button_states()

initial_setup()