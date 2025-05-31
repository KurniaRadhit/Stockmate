import json
import os
import uuid
from datetime import datetime, timedelta
from tabulate import tabulate
from collections import deque

# Folder dan File paths
DATA_FOLDER = "Data"
FILE_PATH = os.path.join(DATA_FOLDER, "inv.json")
ANTREAN_PATH = os.path.join(DATA_FOLDER, "antrean.json")
KATEGORI_OPSI = ["Makanan", "Minuman", "Elektronik"]

# -------------------- FUNGSI FILE HANDLING --------------------
def init_file():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w') as f:
            json.dump({"gudang": {}, "toko": {}}, f, indent=4)

def load_data():
    init_file()
    with open(FILE_PATH, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(FILE_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def cari_nama_produk(koleksi, nama):
    nama_lower = nama.lower()
    return any(nama_lower == key.lower() for key in koleksi)

def dapatkan_nama_asli(koleksi, nama):
    nama_lower = nama.lower()
    for key in koleksi:
        if key.lower() == nama_lower:
            return key
    return None

# -------------------- CLASS QUEQUE --------------------
class FIFOQueue:
    """
    A FIFO (First In, First Out) queue implementation using deque.
    """
    def __init__(self):
        self.queue = deque()
    
    def enqueue(self, item):
        """Add an item to the rear of the queue."""
        self.queue.append(item)
    
    def dequeue(self):
        """Remove and return an item from the front of the queue."""
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.queue.popleft()
    
    def peek(self):
        """Return the front item without removing it."""
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.queue[0]
    
    def is_empty(self):
        """Check if the queue is empty."""
        return len(self.queue) == 0
    
    def size(self):
        """Return the number of items in the queue."""
        return len(self.queue)
    
    def to_list(self):
        """Convert queue to list for JSON serialization."""
        return list(self.queue)
    
    def from_list(self, items):
        """Load queue from a list."""
        self.queue = deque(items)
    
    def find_and_update(self, condition_func, update_func):
        """
        Find item in queue based on condition and update it.
        Returns True if item was found and updated, False otherwise.
        """
        for i, item in enumerate(self.queue):
            if condition_func(item):
                updated_item = update_func(item)
                self.queue[i] = updated_item
                return True
        return False
    
    def find_index(self, condition_func):
        """Find the index of the first item that matches the condition."""
        for i, item in enumerate(self.queue):
            if condition_func(item):
                return i
        return -1

# Global queue instance
antrean_queue = FIFOQueue()

# -------------------- QUICK SORT --------------------
def quick_sort(arr, ascending=True):
    if len(arr) <= 1:
        return arr
    pivot = arr[0]
    pivot_key = pivot[0].lower()
    left = [item for item in arr[1:] if (item[0].lower() <= pivot_key) == ascending]
    right = [item for item in arr[1:] if (item[0].lower() > pivot_key) == ascending]
    return quick_sort(left, ascending) + [pivot] + quick_sort(right, ascending)

# -------------------- CEK KADALUARSA --------------------

def cek_dan_bersihkan_kadaluarsa():
    """Cek produk yang sudah kadaluarsa dan hapus dari gudang dan toko"""
    data = load_data()
    hari_ini = datetime.now().strftime('%Y-%m-%d')
    
    # Cek di gudang
    gudang_untuk_dihapus = []
    for produk, info in data["gudang"].items():
        if "tanggal_kadaluarsa" in info and info["tanggal_kadaluarsa"] <= hari_ini:
            gudang_untuk_dihapus.append(produk)
    
    # Cek di toko
    toko_untuk_dihapus = []
    for produk, info in data["toko"].items():
        if "tanggal_kadaluarsa" in info and info["tanggal_kadaluarsa"] <= hari_ini:
            toko_untuk_dihapus.append(produk)
    
    # Hapus produk kadaluarsa
    for produk in gudang_untuk_dihapus:
        del data["gudang"][produk]
        print(f"Produk '{produk}' di gudang telah kadaluarsa dan dihapus dari sistem.")
    
    for produk in toko_untuk_dihapus:
        del data["toko"][produk]
        print(f"Produk '{produk}' di toko telah kadaluarsa dan dihapus dari sistem.")
    
    if gudang_untuk_dihapus or toko_untuk_dihapus:
        save_data(data)
        return True
    return False


# -------------------- TAMBAHKAN PRODUK KE TOKO --------------------
def tambah_produk_ke_toko(nama, jumlah, diskon=None):
    # Validasi input terlebih dahulu
    if not nama or not isinstance(nama, str):
        print("Nama produk tidak valid.")
        return False
    
    if not isinstance(jumlah, int) or jumlah <= 0:
        print("Jumlah harus berupa angka positif.")
        return False
    
    try:
        data = load_data()
        gudang = data["gudang"]
        toko = data["toko"]
        
        # Cari nama asli produk di gudang
        nama_asli = dapatkan_nama_asli(gudang, nama)
        
        # Pengecekan keberadaan produk di gudang - STOP di sini jika tidak ada
        if not nama_asli:
            print(f"Produk '{nama}' tidak ditemukan di gudang.")
            return False
        
        # Pengecekan stok di gudang - STOP di sini jika stok tidak mencukupi
        if gudang[nama_asli]["stok"] < jumlah:
            print(f"Stok '{nama_asli}' di gudang tidak mencukupi. Stok tersedia: {gudang[nama_asli]['stok']}")
            return False
        
        # Cek apakah produk sudah ada di toko
        if cari_nama_produk(toko, nama):
            # Produk sudah ada di toko, tambah stok saja
            nama_toko = dapatkan_nama_asli(toko, nama)
            print(f"Produk '{nama_toko}' sudah ada di toko. Menambah stok tanpa mengubah diskon.")
            toko[nama_toko]["stok"] += jumlah
        else:
            # Produk baru di toko
            if diskon is None:
                print(f"Produk '{nama_asli}' adalah produk baru di toko dan memerlukan diskon.")
                return False
            
            # Validasi diskon
            if not isinstance(diskon, (int, float)) or diskon < 0 or diskon > 100:
                print("Diskon harus berupa angka antara 0-100.")
                return False
            
            # Salin atribut dari gudang ke toko
            toko[nama_asli] = {
                "stok": jumlah,
                "kategori": gudang[nama_asli]["kategori"],
                "harga_modal": gudang[nama_asli]["harga_modal"],
                "harga_jual": gudang[nama_asli]["harga_jual"],
                "diskon": diskon,
                "tanggal_input": gudang[nama_asli]["tanggal_input"]
            }
            
            # Salin tanggal kadaluarsa jika ada
            if "tanggal_kadaluarsa" in gudang[nama_asli]:
                toko[nama_asli]["tanggal_kadaluarsa"] = gudang[nama_asli]["tanggal_kadaluarsa"]
                print(f"Produk '{nama_asli}' akan kadaluarsa pada: {gudang[nama_asli]['tanggal_kadaluarsa']}")
        
        # Kurangi stok gudang
        gudang[nama_asli]["stok"] -= jumlah
        
        # Simpan data
        save_data(data)
        print(f"{jumlah} unit produk '{nama_asli}' berhasil dipindahkan ke toko.")
        return True
        
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        return False
    
# -------------------- TAMPILKAN PRODUK -----------------------------
def hitung_harga_diskon(harga, diskon):
    return harga * (1 - diskon / 100)

def tampilkan_produk(lokasi="gudang", ascending=True, filter_kategori=None):
    data = load_data()
    if lokasi not in data:
        print("Lokasi tidak valid.")
        return

    produk_list = data[lokasi]
    filtered = {
        k: v for k, v in produk_list.items()
        if filter_kategori is None or v["kategori"] == filter_kategori
    }

    produk_items = list(filtered.items())
    sorted_produk = quick_sort(produk_items, ascending)

    if not sorted_produk:
        print("Tidak ada produk yang ditemukan.")
        return

    tabel = []
    for nama, info in sorted_produk:
        if lokasi == "toko":
            harga_jual = info['harga_jual']
            diskon = info.get('diskon', 0)
            harga_diskon = hitung_harga_diskon(harga_jual, diskon)
            tabel.append([
                nama, info['stok'], f"Rp {harga_jual:,.2f}", info['kategori'],
                f"{diskon}%", f"Rp {harga_diskon:,.2f}"
            ])
        else:  # lokasi == "gudang"
            tabel.append([
                nama,
                info['stok'],
                f"Rp {info['harga_modal']:,.2f}",
                f"Rp {info['harga_jual']:,.2f}",
                info['kategori']
            ])

    print(f"\nProduk di {lokasi.upper()}:")
    if lokasi == "toko":
        print(tabulate(
            tabel,
            headers=["Nama", "Stok", "Harga Jual", "Kategori", "Diskon", "Harga Setelah Diskon"],
            tablefmt="grid"
        ))
    else:
        print(tabulate(
            tabel,
            headers=["Nama", "Stok", "Harga Modal", "Harga Jual", "Kategori"],
            tablefmt="grid"
        ))

def menu_tampilkan_produk(lokasi):
    print(f"\n=== Tampilkan Produk di {lokasi.upper()} ===")
    print("1. Tampilkan semua")
    print("2. Tampilkan berdasarkan kategori")
    opsi = input("Pilih opsi (1/2): ").strip()

    filter_kategori = None
    if opsi == "2":
        print("Pilih kategori:")
        for i, kategori in enumerate(KATEGORI_OPSI):
            print(f"{i+1}. {kategori}")
        try:
            idx = int(input("Masukkan nomor kategori: ")) - 1
            if idx < 0 or idx >= len(KATEGORI_OPSI):
                print("Kategori tidak valid.")
                return
            filter_kategori = KATEGORI_OPSI[idx]
        except ValueError:
            print("Input tidak valid.")
            return

    urutan = input("Urutkan ascending (a) atau descending (d)? [a/d]: ").lower()
    ascending = (urutan != "d")

    tampilkan_produk(lokasi=lokasi, ascending=ascending, filter_kategori=filter_kategori)

def menu_tampilan_produk_utama():
    while True:
        print("\n=== MENU UTAMA ===")
        print("1. Tampilkan Produk di Gudang")
        print("2. Tampilkan Produk di Toko")
        print("3. Keluar")

        pilihan = input("Pilih opsi (1-3): ").strip()

        if pilihan == "1":
            menu_tampilkan_produk(lokasi="gudang")
        elif pilihan == "2":
            menu_tampilkan_produk("toko")
        elif pilihan == "3":
            print("Terima kasih! Program selesai.")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# -------------------- CETAK TOTAL STOK --------------------
def cetak_total_stok():
    data = load_data()
    gabungan = {}

    # Proses data gudang
    for nama, info in data["gudang"].items():
        nama_lower = nama.lower()
        gabungan[nama_lower] = {
            "nama_asli": nama,
            "stok": info["stok"],
            "harga_modal": info.get("harga_modal", 0),
            "harga_jual": info.get("harga_jual", 0),
            "kategori": info.get("kategori", "-"),
            "diskon": 0
        }

    # Proses data toko
    for nama, info in data["toko"].items():
        nama_lower = nama.lower()
        if nama_lower in gabungan:
            gabungan[nama_lower]["stok"] += info["stok"]
            gabungan[nama_lower]["harga_jual"] = info.get("harga_jual", gabungan[nama_lower]["harga_jual"])
            gabungan[nama_lower]["harga_modal"] = info.get("harga_modal", gabungan[nama_lower]["harga_modal"])
            gabungan[nama_lower]["diskon"] = info.get("diskon", 0)
        else:
            gabungan[nama_lower] = {
                "nama_asli": nama,
                "stok": info["stok"],
                "harga_modal": info.get("harga_modal", 0),
                "harga_jual": info.get("harga_jual", 0),
                "kategori": info.get("kategori", "-"),
                "diskon": info.get("diskon", 0)
            }

    if not gabungan:
        print("Tidak ada produk yang ditemukan.")
        return

    produk_items = [(v["nama_asli"], v) for v in gabungan.values()]
    sorted_produk = quick_sort(produk_items, True)

    tabel = []
    for nama, item in sorted_produk:
        harga_diskon = hitung_harga_diskon(item['harga_jual'], item['diskon'])
        tabel.append([
            nama,
            item["stok"],
            f"Rp {item['harga_modal']:,.2f}",
            f"Rp {item['harga_jual']:,.2f}",
            item["kategori"],
            f"{item['diskon']}%",
            f"Rp {harga_diskon:,.2f}"
        ])

    print("\n=== TOTAL STOK PRODUK (GUDANG + TOKO) ===")
    print(tabulate(
        tabel,
        headers=["Nama", "Total Stok", "Harga Modal", "Harga Jual", "Kategori", "Diskon", "Harga Setelah Diskon"],
        tablefmt="grid"
    ))

# -------------------- SEQUENTIAL SEARCH --------------------
def sequential_search(data_dict, produk_dicari):
    for nama_produk in data_dict:
        if nama_produk.lower() == produk_dicari.lower():
            return data_dict[nama_produk]
    return None

def cari_produk_toko():
    data = load_data()
    produk_dicari = input("Masukkan nama produk yang ingin dicari di TOKO: ").strip()
    hasil = sequential_search(data.get("toko", {}), produk_dicari)
    
    if hasil:
        print(f"\nProduk '{produk_dicari}' ditemukan di TOKO:")
        for k, v in hasil.items():
            print(f"  {k}: {v}")
    else:
        print(f"\nProduk '{produk_dicari}' tidak ditemukan di TOKO.")

# -------------------- UPDATE PRODUK TOKO --------------------
def update_produk_toko():
    data = load_data()
    toko = data["toko"]

    nama = input("Masukkan nama produk yang ingin diupdate: ").strip()
    nama_asli = dapatkan_nama_asli(toko, nama)

    if not nama_asli:
        print(f"Produk '{nama}' tidak ditemukan di toko.")
        return

    produk = toko[nama_asli]
    print(f"\nProduk ditemukan: {nama_asli}")
    print(f"Harga jual saat ini: Rp{produk.get('harga_jual', 0):,.2f}")
    print(f"Diskon saat ini: {produk.get('diskon', 0.0)}%")

    try:
        harga_baru = input("Masukkan harga jual baru (tekan Enter jika tidak ingin mengubah): ").strip()
        if harga_baru:
            produk["harga_jual"] = float(harga_baru)

        diskon_input = input("Masukkan diskon baru (%): (tekan Enter jika tidak ingin mengubah) ").strip()
        if diskon_input:
            produk["diskon"] = float(diskon_input)

        save_data(data)
        print(f"Produk '{nama_asli}' di toko berhasil diperbarui.")
    except ValueError:
        print("Input tidak valid. Pastikan harga dan diskon berupa angka.")


# -------------------- KONFIRMASI PESANAN --------------------
def init_antrean_file():
    if not os.path.exists(ANTREAN_PATH):
        with open(ANTREAN_PATH, 'w') as f:
            json.dump([], f, indent=4)

def load_antrean():
    """
    Memuat data antrean dari file ke FIFO queue.
    """
    global antrean_queue
    init_antrean_file()
    with open(ANTREAN_PATH, 'r') as f:
        content = f.read().strip()
        if not content:
            antrean_queue = FIFOQueue()
        else:
            data = json.loads(content)
            antrean_queue = FIFOQueue()
            antrean_queue.from_list(data)
    return antrean_queue

def save_antrean():
    """
    Menyimpan data antrean dari FIFO queue ke file.
    """
    global antrean_queue
    with open(ANTREAN_PATH, 'w') as f:
        json.dump(antrean_queue.to_list(), f, indent=4)

def konfirmasi_pesanan():
    """
    Automatically confirm the first (oldest) unconfirmed order in the queue.
    This follows true FIFO principle - first in, first confirmed.
    """
    global antrean_queue
    load_antrean()
    data = load_data()
    clean_expired_orders()

    if antrean_queue.is_empty():
        print("Tidak ada pesanan dalam antrean.")
        return

    # Find the first unconfirmed order (maintaining FIFO)
    queue_list = antrean_queue.to_list()
    first_unconfirmed = None
    first_unconfirmed_index = -1

    for idx, order in enumerate(queue_list):
        if order['status'] == "not confirmed":
            first_unconfirmed = order
            first_unconfirmed_index = idx + 1  # Human-readable position
            break

    if not first_unconfirmed:
        print("Tidak ada pesanan yang belum dikonfirmasi.")
        return

    print(f"Mengkonfirmasi pesanan pertama dalam antrean (posisi {first_unconfirmed_index}):")
    print(f"ID Antrean: {first_unconfirmed.get('id_antrean', '(tidak tersedia)')}")
    print(f"Nama Pembeli: {first_unconfirmed['nama_pembeli']}")
    print(f"Waktu: {first_unconfirmed['waktu']}")
    print(f"Jumlah item: {len(first_unconfirmed['pesanan'])}")
    print("Daftar Pesanan:")
    total_harga = 0
    for item in first_unconfirmed['pesanan']:
        harga_diskon = item['harga_satuan'] * (1 - item['diskon']/100)
        subtotal = harga_diskon * item['jumlah']
        total_harga += subtotal
        print(f" - {item['produk']} | Jumlah: {item['jumlah']} | Harga: {item['harga_satuan']} | Diskon: {item['diskon']}% | Setelah Diskon: {harga_diskon:.2f} | Subtotal: {subtotal:.2f}")
    print(f"Total Harga: {total_harga:.2f}")

    # Confirm the order automatically
    def find_order(order):
        return (order['nama_pembeli'] == first_unconfirmed['nama_pembeli'] and 
                order['waktu'] == first_unconfirmed['waktu'] and
                order['status'] == "not confirmed")

    def update_status(order):
        order['status'] = "confirmed"
        return order

    if antrean_queue.find_and_update(find_order, update_status):
        save_antrean()

        # Remove products with zero stock
        produk_dihapus = []
        for item in first_unconfirmed['pesanan']:
            nama_produk = item['produk']
            if nama_produk in data["toko"] and data["toko"][nama_produk]["stok"] == 0:
                produk_dihapus.append(nama_produk)
                del data["toko"][nama_produk]

        save_data(data)
        print("Pesanan berhasil dikonfirmasi secara otomatis!")

        if produk_dihapus:
            print("\nBeberapa produk telah otomatis dihapus karena stok habis:")
            for produk in produk_dihapus:
                print(f"- {produk}")
    else:
        print("Gagal memperbarui status pesanan.")

# -------------------- LIHAT ANTREAN LENGKAP --------------------
def lihat_antrean_lengkap():
    """
    View complete queue with detailed information.
    """
    global antrean_queue
    clean_expired_orders()
    load_antrean()

    if antrean_queue.is_empty():
        print("Tidak ada pesanan dalam antrean.")
        return

    print(f"\n=== ANTREAN LENGKAP (Total: {antrean_queue.size()} pesanan) ===")
    print("Urutan berdasarkan FIFO (First In, First Out):")

    queue_list = antrean_queue.to_list()
    unconfirmed_count = 0
    confirmed_count = 0
    total_pending_revenue = 0
    total_confirmed_revenue = 0

    for idx, pesanan in enumerate(queue_list, 1):
        status_text = "Menunggu konfirmasi" if pesanan['status'] == "not confirmed" else "Dikonfirmasi"
        order_total = 0
        for item in pesanan['pesanan']:
            harga_diskon = item['harga_satuan'] * (1 - item['diskon']/100)
            subtotal = harga_diskon * item['jumlah']
            order_total += subtotal

        if pesanan['status'] == "not confirmed":
            unconfirmed_count += 1
            total_pending_revenue += order_total
            status_text += " ⏳"
        else:
            confirmed_count += 1
            total_confirmed_revenue += order_total
            status_text += " ✅"

        print(f"\n{idx}. ID: {pesanan.get('id_antrean', '-')}, {pesanan['nama_pembeli']} - {pesanan['waktu']}")
        print(f"   Status: {status_text}")
        print(f"   Jumlah item: {len(pesanan['pesanan'])}")
        print(f"   Total harga: {order_total:.2f}")
        items_text = ", ".join([f"{item['produk']} ({item['jumlah']})" for item in pesanan['pesanan']])
        if len(items_text) > 80:
            items_text = items_text[:77] + "..."
        print(f"   Items: {items_text}")

    print(f"\n📊 Ringkasan:")
    print(f"   Pesanan belum dikonfirmasi: {unconfirmed_count} (Pending revenue: {total_pending_revenue:.2f})")
    print(f"   Pesanan sudah dikonfirmasi: {confirmed_count} (Confirmed revenue: {total_confirmed_revenue:.2f})")
    print(f"   Total revenue: {total_pending_revenue + total_confirmed_revenue:.2f}")

    if unconfirmed_count > 0:
        first_unconfirmed_pos = next((idx + 1 for idx, order in enumerate(queue_list) if order['status'] == 'not confirmed'), None)
        print(f"   Pesanan tertua yang belum dikonfirmasi: Posisi {first_unconfirmed_pos}")

# -------------------- PENGHAPUSAN PESANAN KEDALUARSA --------------------
def clean_expired_orders():
    """
    Remove orders that haven't been confirmed within 12 hours.
    Uses a temporary queue to maintain FIFO order while filtering.
    """
    global antrean_queue
    load_antrean()
    current_time = datetime.now()

    # Create a new queue for valid orders
    new_queue = FIFOQueue()
    expired_count = 0

    # Process each order in FIFO order
    temp_list = antrean_queue.to_list()
    for order in temp_list:
        if order['status'] == "not confirmed":
            try:
                order_time = datetime.strptime(order['waktu'], "%Y-%m-%d %H:%M:%S")
                if current_time - order_time > timedelta(hours=12):
                    expired_count += 1
                    print(f"Pesanan kedaluwarsa dihapus: {order['nama_pembeli']} - {order['waktu']}")
                    continue
            except:
                continue
        new_queue.enqueue(order)

    antrean_queue = new_queue

    if expired_count > 0:
        save_antrean()
        print(f"{expired_count} pesanan kedaluwarsa telah dihapus dari antrean.")

    return expired_count
def pilih_rentang_waktu():
    while True:
        print("\n=== PILIH RENTANG WAKTU ===")
        print("1. Hari ini")
        print("2. Kemarin")
        print("3. 7 hari terakhir")
        print("4. 30 hari terakhir")
        print("5. Bulan ini")
        print("6. Bulan lalu")
        print("7. Rentang tanggal kustom")
        print("8. Semua waktu")
        print("0. Kembali")
        
        pilihan = input("Pilih opsi (0-8): ").strip()
        
        today = datetime.now()
        today_start = datetime(today.year, today.month, today.day)
        
        if pilihan == "0":
            return None, None
        elif pilihan == "1":  # Hari ini
            return today_start, today_start + timedelta(days=1)
        elif pilihan == "2":  # Kemarin
            yesterday = today_start - timedelta(days=1)
            return yesterday, today_start
        elif pilihan == "3":  # 7 hari terakhir
            return today_start - timedelta(days=7), today_start + timedelta(days=1)
        elif pilihan == "4":  # 30 hari terakhir
            return today_start - timedelta(days=30), today_start + timedelta(days=1)
        elif pilihan == "5":  # Bulan ini
            start_of_month = datetime(today.year, today.month, 1)
            return start_of_month, today_start + timedelta(days=1)
        elif pilihan == "6":  # Bulan lalu
            if today.month == 1:
                start_of_last_month = datetime(today.year - 1, 12, 1)
                end_of_last_month = datetime(today.year, 1, 1)
            else:
                start_of_last_month = datetime(today.year, today.month - 1, 1)
                end_of_last_month = datetime(today.year, today.month, 1)
            return start_of_last_month, end_of_last_month
        elif pilihan == "7":  # Rentang tanggal kustom
            try:
                print("\nMasukkan rentang tanggal (format: DD-MM-YYYY)")
                tanggal_awal = input("Tanggal awal: ").strip()
                tanggal_akhir = input("Tanggal akhir: ").strip()
                
                start_date = datetime.strptime(tanggal_awal, "%d-%m-%Y")
                end_date = datetime.strptime(tanggal_akhir, "%d-%m-%Y") + timedelta(days=1)  # Include the end date
                
                return start_date, end_date
            except ValueError:
                print("\nFormat tanggal tidak valid. Gunakan format DD-MM-YYYY.")
                continue
        elif pilihan == "8":  # Semua waktu
            return None, None
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

def filter_pesanan_by_date_range(pesanan_list, start_date, end_date):
    if start_date is None and end_date is None:
        return pesanan_list
        
    filtered_pesanan = []
    for pesanan in pesanan_list:
        try:
            pesanan_date = datetime.strptime(pesanan['waktu'], "%Y-%m-%d %H:%M:%S")
            if (start_date is None or pesanan_date >= start_date) and (end_date is None or pesanan_date < end_date):
                filtered_pesanan.append(pesanan)
        except (ValueError, KeyError):
            # Skip pesanan if it doesn't have a valid date
            continue
            
    return filtered_pesanan

# -------------------- HITUNG KEUNTUNGAN --------------------
def hitung_profit_loss(total_per_produk, produk_toko):
    """
    Menghitung keuntungan/kerugian secara riil berdasarkan harga modal, harga jual, diskon, dan jumlah terjual.
    """

    hasil = {
        'total_produk_terjual': 0,
        'total_produk_tersedia': 0,
        'target_penjualan': 0,
        'persentase_terjual': 0,
        'status': '',  # 'PROFIT' atau 'LOSS'
        'persentase_profit_loss': 0,
        'nominal_profit_loss': 0,
        'total_modal': 0,
        'total_penjualan': 0
    }

    for produk, info in total_per_produk.items():
        jumlah_terjual = info['jumlah']
        hasil['total_produk_terjual'] += jumlah_terjual

        nama_asli = dapatkan_nama_asli(produk_toko, produk)
        if not nama_asli:
            continue

        data_produk = produk_toko.get(nama_asli, {})
        harga_modal = data_produk.get('harga_modal', 0)
        harga_jual = data_produk.get('harga_jual', 0)
        diskon = data_produk.get('diskon', 0)

        harga_setelah_diskon = harga_jual * (1 - diskon / 100)
        subtotal_penjualan = jumlah_terjual * harga_setelah_diskon
        subtotal_modal = jumlah_terjual * harga_modal

        hasil['total_modal'] += subtotal_modal
        hasil['total_penjualan'] += subtotal_penjualan

    # Hitung total stok tersedia
    for produk_info in produk_toko.values():
        hasil['total_produk_tersedia'] += produk_info.get('stok', 0)

    hasil['target_penjualan'] = hasil['total_produk_tersedia'] * 0.75

    if hasil['total_produk_tersedia'] > 0:
        hasil['persentase_terjual'] = (hasil['total_produk_terjual'] / hasil['total_produk_tersedia']) * 100

    # Hitung profit atau loss
    hasil['nominal_profit_loss'] = hasil['total_penjualan'] - hasil['total_modal']
    if hasil['nominal_profit_loss'] >= 0:
        hasil['status'] = 'PROFIT'
        hasil['persentase_profit_loss'] = (hasil['nominal_profit_loss'] / hasil['total_modal']) * 100 if hasil['total_modal'] > 0 else 0
    else:
        hasil['status'] = 'LOSS'
        hasil['persentase_profit_loss'] = (abs(hasil['nominal_profit_loss']) / hasil['total_modal']) * 100 if hasil['total_modal'] > 0 else 0

    return hasil


def lihat_laporan_penjualan():
    print("\n=== LAPORAN PENJUALAN ===")
    
    # Pilih rentang waktu
    start_date, end_date = pilih_rentang_waktu()
    if start_date is None and end_date is None and not isinstance(start_date, datetime):
        print("Kembali ke menu utama.")
        return
    
    # Tampilkan rentang waktu yang dipilih
    if start_date is None and end_date is None:
        print("\nMenampilkan laporan untuk: SEMUA WAKTU")
    else:
        print(f"\nMenampilkan laporan untuk periode: {start_date.strftime('%d-%m-%Y')} hingga {(end_date - timedelta(days=1)).strftime('%d-%m-%Y')}")
    
    # Fix: Get the queue object and convert to list
    antrean_queue = load_antrean()
    antrean_list = antrean_queue.to_list()
    antrean_confirmed = [p for p in antrean_list if p['status'] == "confirmed"]
    
    # Filter berdasarkan rentang tanggal
    filtered_pesanan = filter_pesanan_by_date_range(antrean_confirmed, start_date, end_date)
    
    if not filtered_pesanan:
        print("Tidak ada pesanan terkonfirmasi dalam rentang waktu yang dipilih.")
        return
    
    print("\nA. DAFTAR TRANSAKSI TERKONFIRMASI")
    print("----------------------------------")
    for idx, pesanan in enumerate(filtered_pesanan, 1):
        print(f"\n{idx}. Nama Pembeli: {pesanan['nama_pembeli']}")
        print(f"   Waktu: {pesanan['waktu']}")
        print(f"   Status: {pesanan['status']}")
        print("   Daftar Pesanan:")   
        
        total_harga = 0
        for item in pesanan['pesanan']:
            harga_diskon = item['harga_satuan'] * (1 - item['diskon']/100)
            subtotal = harga_diskon * item['jumlah']
            total_harga += subtotal        
            print(f"   - {item['produk']} | Jumlah: {item['jumlah']} | "
                  f"Harga: {item['harga_satuan']} | Diskon: {item['diskon']}% | "
                  f"Subtotal: {subtotal}")
        print(f"   Total Harga: {total_harga}")
    
    pilihan = input("\nApakah Anda ingin melihat ringkasan penjualan? (y/n): ").strip().lower()
    if pilihan != "y":
        return
    
    print("\n\nB. RINGKASAN TOTAL PENJUALAN")
    print("----------------------------------")
    print(f"Jumlah Transaksi: {len(filtered_pesanan)}")
    
    total_per_produk = {}
    total_per_kategori = {}
    total_keseluruhan = 0
    
    # Load data untuk mendapatkan informasi kategori produk
    data = load_data()
    produk_toko = data.get("toko", {})
    
    for pesanan in filtered_pesanan:
        subtotal_transaksi = 0
        for item in pesanan['pesanan']:
            nama_produk = item['produk']
            jumlah = item['jumlah']
            harga_satuan = item['harga_satuan']
            diskon = item['diskon']
            harga_diskon = harga_satuan * (1 - diskon/100)
            subtotal = jumlah * harga_diskon
            subtotal_transaksi += subtotal
            
            # Catat total per produk
            if nama_produk not in total_per_produk:
                total_per_produk[nama_produk] = {
                    'jumlah': 0,
                    'total_harga': 0
                }
            total_per_produk[nama_produk]['jumlah'] += jumlah
            total_per_produk[nama_produk]['total_harga'] += subtotal
            
            # Catat total per kategori
            kategori = "Tidak terkategori"
            nama_asli = dapatkan_nama_asli(produk_toko, nama_produk)
            if nama_asli and 'kategori' in produk_toko.get(nama_asli, {}):
                kategori = produk_toko[nama_asli]['kategori']
                
            if kategori not in total_per_kategori:
                total_per_kategori[kategori] = {
                    'jumlah': 0,
                    'total_harga': 0
                }
            total_per_kategori[kategori]['jumlah'] += jumlah
            total_per_kategori[kategori]['total_harga'] += subtotal
        
        total_keseluruhan += subtotal_transaksi
    
    # Tampilkan ringkasan per produk
    print("\nRINGKASAN PENJUALAN PER PRODUK:")
    header = ["Produk", "Jumlah Terjual", "Total Penjualan"]
    table_data = []
    for produk, info in total_per_produk.items():
        table_data.append([produk, info['jumlah'], f"Rp {info['total_harga']:,.2f}"])
    
    print(tabulate(table_data, headers=header, tablefmt="grid"))
    
    # Tampilkan ringkasan per kategori
    print("\nRINGKASAN PENJUALAN PER KATEGORI:")
    header = ["Kategori", "Jumlah Terjual", "Total Penjualan", "Persentase"]
    table_data = []
    for kategori, info in total_per_kategori.items():
        persentase = (info['total_harga'] / total_keseluruhan * 100) if total_keseluruhan > 0 else 0
        table_data.append([kategori, info['jumlah'], f"Rp {info['total_harga']:,.2f}", f"{persentase:.2f}%"])
    
    print(tabulate(table_data, headers=header, tablefmt="grid"))
    print(f"\nTOTAL PENJUALAN KESELURUHAN: Rp {total_keseluruhan:,.2f}")
    
    # Tampilkan rata-rata penjualan per hari
    if start_date and end_date:
        jumlah_hari = (end_date - start_date).days
        if jumlah_hari > 0:
            rata_rata_per_hari = total_keseluruhan / jumlah_hari
            print(f"RATA-RATA PENJUALAN PER HARI: Rp {rata_rata_per_hari:,.2f}")
    
    # MULAI FITUR PROFIT DAN LOSS
    # Hitung profit/loss berdasarkan target penjualan 75%
    profit_loss = hitung_profit_loss(total_per_produk, produk_toko)
    
    # Tampilkan hasil perhitungan profit/loss
    print("\nC. ANALISIS TARGET PENJUALAN")
    print("----------------------------------")
    print(f"Total Produk Terjual: {profit_loss['total_produk_terjual']} unit")
    print(f"Total Produk Tersedia: {profit_loss['total_produk_tersedia']} unit")
    print(f"Target Penjualan (75%): {profit_loss['target_penjualan']:.2f} unit")
    print(f"Persentase Terjual: {profit_loss['persentase_terjual']:.2f}%")
    
    # Tampilkan status profit/loss
    if profit_loss['status'] == 'PROFIT':
        print(f"\nStatus: PROFIT (Melebihi target sebesar {profit_loss['persentase_profit_loss']:.2f}%)")
        print(f"Nominal Profit: Rp {profit_loss['nominal_profit_loss']:,.2f}")
    else:
        print(f"\nStatus: LOSS (Di bawah target sebesar {profit_loss['persentase_profit_loss']:.2f}%)")
        print(f"Nominal Loss: Rp {profit_loss['nominal_profit_loss']:,.2f}")
    
    # Export data sebagai CSV jika diminta
    pilihan = input("\nApakah Anda ingin mengekspor laporan ini sebagai CSV? (y/n): ").strip().lower()
    if pilihan == "y":
        export_laporan_to_csv(filtered_pesanan, total_per_produk, total_per_kategori, total_keseluruhan, start_date, end_date, profit_loss)

def export_laporan_to_csv(pesanan_list, total_per_produk, total_per_kategori, total_keseluruhan, start_date, end_date, profit_loss):
    import csv
    from datetime import datetime, timedelta
    import os
    
    # Format number helper function that follows Indonesian format
    def format_number(value):
        if isinstance(value, (int, float)):
            # Format with thousand separator using dots and decimal comma
            formatted = f"{value:,.1f}".replace(',', '_').replace('.', ',').replace('_', '.')
            
            # Remove trailing zero after decimal point if it's a whole number
            if formatted.endswith(',0'):
                formatted = formatted[:-2]
                
            return f'"{formatted}"'  # Wrap in quotes to preserve formatting in CSV
        return f'"{value}"' if value else ""
    
    # Create export filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if start_date and end_date:
        period = f"{start_date.strftime('%Y%m%d')}_to_{(end_date - timedelta(days=1)).strftime('%Y%m%d')}"
    else:
        period = "all_time"
    
    filename = f"laporan_penjualan_{period}_{timestamp}.csv"
    
    try:
        # Try to generate an Excel file first if xlsxwriter is available
        try:
            import xlsxwriter
            excel_available = True
        except ImportError:
            excel_available = False
            
        if excel_available:
            try:
                # Create Excel file with proper formatting
                excel_filename = f"laporan_penjualan_{period}_{timestamp}.xlsx"
                workbook = xlsxwriter.Workbook(excel_filename)
                worksheet = workbook.add_worksheet('Laporan Penjualan')
                
                # Define formats
                header_format = workbook.add_format({
                    'bold': True,
                    'font_size': 12,
                    'align': 'center',
                    'bg_color': '#D9E1F2',
                    'border': 1
                })
                
                subheader_format = workbook.add_format({
                    'bold': True,
                    'font_size': 11,
                    'align': 'left',
                    'bg_color': '#E2EFDA',
                    'border': 1
                })
                
                profit_format = workbook.add_format({
                    'bold': True,
                    'font_size': 11,
                    'align': 'left',
                    'bg_color': '#C6E0B4',  # Light green for profit
                    'border': 1
                })
                
                loss_format = workbook.add_format({
                    'bold': True,
                    'font_size': 11,
                    'align': 'left',
                    'bg_color': '#F8CBAD',  # Light red for loss
                    'border': 1
                })
                
                title_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14,
                    'align': 'left',
                })
                
                date_format = workbook.add_format({
                    'num_format': 'yyyy-mm-dd hh:mm:ss',
                    'align': 'left',
                    'border': 1
                })
                
                number_format = workbook.add_format({
                    'num_format': '#,##0',
                    'align': 'right',
                    'border': 1
                })
                
                percentage_format = workbook.add_format({
                    'num_format': '0.0%',
                    'align': 'right',
                    'border': 1
                })
                
                currency_format = workbook.add_format({
                    'num_format': '#,##0',
                    'align': 'right',
                    'border': 1
                })
                
                text_format = workbook.add_format({
                    'align': 'left',
                    'border': 1
                })
                
                # Set column widths
                worksheet.set_column('A:A', 5)   # No.
                worksheet.set_column('B:B', 15)  # Nama Pembeli
                worksheet.set_column('C:C', 20)  # Waktu
                worksheet.set_column('D:D', 15)  # Produk
                worksheet.set_column('E:E', 10)  # Jumlah
                worksheet.set_column('F:F', 15)  # Harga Satuan
                worksheet.set_column('G:G', 10)  # Diskon
                worksheet.set_column('H:H', 15)  # Subtotal
                
                # Title and period
                row = 0
                worksheet.write(row, 0, 'LAPORAN PENJUALAN', title_format)
                row += 1
                
                if start_date and end_date:
                    worksheet.write(row, 0, f"Periode: {start_date.strftime('%d-%m-%Y')} hingga {(end_date - timedelta(days=1)).strftime('%d-%m-%Y')}")
                else:
                    worksheet.write(row, 0, 'Periode: SEMUA WAKTU')
                row += 2  # Add extra space
                
                # Daftar Transaksi section
                worksheet.write(row, 0, 'DAFTAR TRANSAKSI', subheader_format)
                row += 1
                
                # Transaction header row
                col_headers = ['No.', 'Nama Pembeli', 'Waktu', 'Produk', 'Jumlah', 'Harga Satuan', 'Diskon', 'Subtotal']
                for col, header in enumerate(col_headers):
                    worksheet.write(row, col, header, header_format)
                row += 1
                
                # Transaction rows
                transaction_idx = 1
                for pesanan in pesanan_list:
                    for item in pesanan['pesanan']:
                        harga_diskon = item['harga_satuan'] * (1 - item['diskon']/100)
                        subtotal = harga_diskon * item['jumlah']
                        
                        # Format date from string if needed
                        waktu = pesanan['waktu']
                        if isinstance(waktu, str):
                            try:
                                waktu = datetime.strptime(waktu, "%Y-%m-%d %H:%M:%S")
                            except:
                                pass
                        
                        worksheet.write(row, 0, transaction_idx, text_format)
                        worksheet.write(row, 1, pesanan['nama_pembeli'], text_format)
                        
                        # Handle the date format properly
                        if isinstance(waktu, datetime):
                            worksheet.write_datetime(row, 2, waktu, date_format)
                        else:
                            worksheet.write(row, 2, str(waktu), text_format)
                            
                        worksheet.write(row, 3, item['produk'], text_format)
                        worksheet.write(row, 4, item['jumlah'], number_format)
                        worksheet.write(row, 5, item['harga_satuan'], currency_format)
                        worksheet.write(row, 6, f"{item['diskon']}%", text_format)
                        worksheet.write(row, 7, subtotal, currency_format)
                        
                        row += 1
                        transaction_idx += 1
                
                row += 1  # Add extra space
                
                # Ringkasan Per Produk section
                worksheet.write(row, 0, 'RINGKASAN PER PRODUK', subheader_format)
                row += 1
                
                # Product summary header
                prod_headers = ['Produk', 'Jumlah Terjual', 'Total Penjualan']
                for col, header in enumerate(prod_headers):
                    worksheet.write(row, col, header, header_format)
                row += 1
                
                # Product summary rows
                for produk, info in total_per_produk.items():
                    worksheet.write(row, 0, produk, text_format)
                    worksheet.write(row, 1, info['jumlah'], number_format)
                    worksheet.write(row, 2, info['total_harga'], currency_format)
                    row += 1
                
                row += 1  # Add extra space
                
                # Ringkasan Per Kategori section
                worksheet.write(row, 0, 'RINGKASAN PER KATEGORI', subheader_format)
                row += 1
                
                # Category summary header
                cat_headers = ['Kategori', 'Jumlah Terjual', 'Total Penjualan', 'Persentase']
                for col, header in enumerate(cat_headers):
                    worksheet.write(row, col, header, header_format)
                row += 1
                
                # Category summary rows
                for kategori, info in total_per_kategori.items():
                    persentase = (info['total_harga'] / total_keseluruhan) if total_keseluruhan > 0 else 0
                    worksheet.write(row, 0, kategori, text_format)
                    worksheet.write(row, 1, info['jumlah'], number_format)
                    worksheet.write(row, 2, info['total_harga'], currency_format)
                    worksheet.write(row, 3, persentase, percentage_format)
                    row += 1
                
                row += 1  # Add extra space
                
                # Total summary
                worksheet.write(row, 0, 'TOTAL KESELURUHAN', subheader_format)
                worksheet.write(row, 2, total_keseluruhan, currency_format)
                row += 1
                
                if start_date and end_date:
                    jumlah_hari = (end_date - start_date).days
                    if jumlah_hari > 0:
                        rata_rata_per_hari = total_keseluruhan / jumlah_hari
                        worksheet.write(row, 0, 'RATA-RATA PER HARI', subheader_format)
                        worksheet.write(row, 2, rata_rata_per_hari, currency_format)
                        row += 1
                
                # TAMBAHAN: Profit/Loss Analysis Section
                row += 1  # Add extra space
                worksheet.write(row, 0, 'ANALISIS TARGET PENJUALAN', subheader_format)
                row += 1
                
                # Format rows based on profit/loss status
                status_format = profit_format if profit_loss['status'] == 'PROFIT' else loss_format
                
                # Write profit/loss headers
                pl_headers = ['Metrik', 'Nilai']
                for col, header in enumerate(pl_headers):
                    worksheet.write(row, col, header, header_format)
                row += 1
                
                # Write profit/loss data
                worksheet.write(row, 0, 'Total Produk Terjual', text_format)
                worksheet.write(row, 1, profit_loss['total_produk_terjual'], number_format)
                row += 1
                
                worksheet.write(row, 0, 'Total Produk Tersedia', text_format)
                worksheet.write(row, 1, profit_loss['total_produk_tersedia'], number_format)
                row += 1
                
                worksheet.write(row, 0, 'Target Penjualan (75%)', text_format)
                worksheet.write(row, 1, profit_loss['target_penjualan'], number_format)
                row += 1
                
                worksheet.write(row, 0, 'Persentase Terjual', text_format)
                worksheet.write(row, 1, profit_loss['persentase_terjual']/100, percentage_format)  # Convert to decimal for Excel percentage format
                row += 1
                
                # Status row with special formatting
                worksheet.write(row, 0, 'Status', status_format)
                worksheet.write(row, 1, profit_loss['status'], status_format)
                row += 1
                
                # Percentage profit/loss
                if profit_loss['status'] == 'PROFIT':
                    worksheet.write(row, 0, 'Persentase Profit', status_format)
                    worksheet.write(row, 1, profit_loss['persentase_profit_loss']/100, percentage_format)  # Convert to decimal
                else:
                    worksheet.write(row, 0, 'Persentase Loss', status_format)
                    worksheet.write(row, 1, profit_loss['persentase_profit_loss']/100, percentage_format)  # Convert to decimal
                row += 1
                
                # Nominal profit/loss
                if profit_loss['status'] == 'PROFIT':
                    worksheet.write(row, 0, 'Nominal Profit', status_format)
                    worksheet.write(row, 1, profit_loss['nominal_profit_loss'], currency_format)
                else:
                    worksheet.write(row, 0, 'Nominal Loss', status_format)
                    worksheet.write(row, 1, profit_loss['nominal_profit_loss'], currency_format)
                
                # Finalize and close Excel workbook
                workbook.close()
                
                # Try to open the file automatically
                try:
                    if os.name == 'nt':  # Windows
                        os.system(f'start excel "{excel_filename}"')
                    elif os.name == 'posix':  # macOS or Linux
                        if os.system('which open > /dev/null') == 0:  # macOS
                            os.system(f'open "{excel_filename}"')
                        else:  # Linux
                            os.system(f'xdg-open "{excel_filename}"')
                except:
                    pass  # Ignore if auto-open fails
                
                print(f"\nLaporan berhasil diekspor ke file Excel '{excel_filename}'")
                return True, excel_filename
                
            except Exception as excel_error:
                print(f"Gagal membuat file Excel: {excel_error}")
                # Continue with CSV creation if Excel creation fails
                pass
        
        # Fall back to CSV format if Excel wasn't created
        with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            
            # Header laporan - span across multiple columns for better appearance
            writer.writerow(["LAPORAN PENJUALAN", "", "", "", "", "", "", ""])
            if start_date and end_date:
                writer.writerow([f"Periode: {start_date.strftime('%d-%m-%Y')} hingga {(end_date - timedelta(days=1)).strftime('%d-%m-%Y')}", "", "", "", "", "", "", ""])
            else:
                writer.writerow(["Periode: SEMUA WAKTU", "", "", "", "", "", "", ""])
            writer.writerow([])  # Empty row for spacing
            
            # Daftar transaksi
            writer.writerow(["DAFTAR TRANSAKSI", "", "", "", "", "", "", ""])
            writer.writerow(["No.", "Nama Pembeli", "Waktu", "Produk", "Jumlah", "Harga Satuan", "Diskon", "Subtotal"])
            
            transaction_idx = 1
            for pesanan in pesanan_list:
                for item in pesanan['pesanan']:
                    harga_diskon = item['harga_satuan'] * (1 - item['diskon']/100)
                    subtotal = harga_diskon * item['jumlah']
                    
                    # Format date properly for CSV
                    waktu = pesanan['waktu']
                    if isinstance(waktu, str):
                        try:
                            dt = datetime.strptime(waktu, "%Y-%m-%d %H:%M:%S")
                            waktu_formatted = f'"{dt.strftime("%d-%m-%Y %H:%M:%S")}"'
                        except:
                            waktu_formatted = f'"{waktu}"'
                    else:
                        waktu_formatted = f'"{waktu}"'
                    
                    writer.writerow([
                        transaction_idx,
                        pesanan['nama_pembeli'],
                        waktu_formatted,
                        item['produk'],
                        item['jumlah'],
                        format_number(item['harga_satuan']),
                        f'"{item["diskon"]}%"',
                        format_number(subtotal)
                    ])
                    transaction_idx += 1
            
            writer.writerow([])  # Empty row for spacing
            
            # Ringkasan per produk
            writer.writerow(["RINGKASAN PER PRODUK", "", "", "", "", "", "", ""])
            writer.writerow(["Produk", "Jumlah Terjual", "Total Penjualan", "", "", "", "", ""])
            for produk, info in total_per_produk.items():
                writer.writerow([
                    produk,
                    info['jumlah'],
                    format_number(info['total_harga']),
                    "", "", "", "", ""
                ])
            
            writer.writerow([])  # Empty row for spacing
            
            # Ringkasan per kategori
            writer.writerow(["RINGKASAN PER KATEGORI", "", "", "", "", "", "", ""])
            writer.writerow(["Kategori", "Jumlah Terjual", "Total Penjualan", "Persentase", "", "", "", ""])
            for kategori, info in total_per_kategori.items():
                persentase = (info['total_harga'] / total_keseluruhan * 100) if total_keseluruhan > 0 else 0
                writer.writerow([
                    kategori,
                    info['jumlah'],
                    format_number(info['total_harga']),
                    f'"{persentase:.2f}%"',
                    "", "", "", ""
                ])
            
            writer.writerow([])  # Empty row for spacing
            
            # Summary totals - align with the "Total Penjualan" column
            writer.writerow(["TOTAL KESELURUHAN", "", format_number(total_keseluruhan), "", "", "", "", ""])
            
            # Average per day if date range is provided
            if start_date and end_date:
                jumlah_hari = (end_date - start_date).days
                if jumlah_hari > 0:
                    rata_rata_per_hari = total_keseluruhan / jumlah_hari
                    writer.writerow(["RATA-RATA PER HARI", "", format_number(rata_rata_per_hari), "", "", "", "", ""])
            
            writer.writerow([])  # Empty row for spacing
            
            # TAMBAHAN: Profit/Loss Analysis Section
            writer.writerow(["ANALISIS TARGET PENJUALAN", "", "", "", "", "", "", ""])
            writer.writerow(["Metrik", "Nilai", "", "", "", "", "", ""])
            writer.writerow(["Total Produk Terjual", profit_loss['total_produk_terjual'], "", "", "", "", "", ""])
            writer.writerow(["Total Produk Tersedia", profit_loss['total_produk_tersedia'], "", "", "", "", "", ""])
            writer.writerow(["Target Penjualan (75%)", profit_loss['target_penjualan'], "", "", "", "", "", ""])
            writer.writerow(["Persentase Terjual", f'"{profit_loss["persentase_terjual"]:.2f}%"', "", "", "", "", "", ""])
            writer.writerow(["Status", profit_loss['status'], "", "", "", "", "", ""])
            
            # Percentage and nominal profit/loss with the appropriate label based on status
            if profit_loss['status'] == 'PROFIT':
                writer.writerow(["Persentase Profit", f'"{profit_loss["persentase_profit_loss"]:.2f}%"', "", "", "", "", "", ""])
                writer.writerow(["Nominal Profit", format_number(profit_loss['nominal_profit_loss']), "", "", "", "", "", ""])
            else:
                writer.writerow(["Persentase Loss", f'"{profit_loss["persentase_profit_loss"]:.2f}%"', "", "", "", "", "", ""])
                writer.writerow(["Nominal Loss", format_number(profit_loss['nominal_profit_loss']), "", "", "", "", "", ""])
        
        # Try to open the CSV file automatically
        try:
            if os.name == 'nt':  # Windows
                os.system(f'start excel "{filename}"')
            elif os.name == 'posix':  # macOS or Linux
                if os.system('which open > /dev/null') == 0:  # macOS
                    os.system(f'open "{filename}"')
                else:  # Linux
                    os.system(f'xdg-open "{filename}"')
        except:
            pass  # Ignore if auto-open fails
        
        print(f"\nLaporan berhasil diekspor ke file CSV '{filename}'")
        return True, filename
        
    except Exception as e:
        print(f"Terjadi kesalahan saat mengekspor laporan: {e}")
        return False, None


# -------------------- MENU ADMIN --------------------
def menu_admin():
    
    if cek_dan_bersihkan_kadaluarsa():
        print("Pemeriksaan kadaluarsa selesai.")
        
    while True:
        print("\n=== SISTEM INVENTARIS TOKO - ADMIN PANEL ===")
        print("1. Tambah produk ke toko")
        print("2. Tampilkan produk")
        print("3. Cetak total stok produk (gudang + toko)")
        print("4. Cari produk di toko")
        print("5. Update produk toko")
        print("6. Lihat laporan penjualan")
        print("7. Konfirmasi pesanan")
        print("8. Periksa produk kadaluarsa")
        print("0. Kembali ke menu utama")
        
        pilihan = input("Pilih menu (0-8): ").strip()
        
        if pilihan == "1":
            nama = input("Nama produk yang dipindah: ").strip()
            
            if not nama:
                print("Nama produk tidak boleh kosong.")
                continue  # atau return, tergantung struktur loop Anda
            
            # PENGECEKAN PERTAMA: Apakah produk ada di GUDANG?
            try:
                data = load_data()
                gudang = data["gudang"]
                toko = data["toko"]
                
                nama_asli = dapatkan_nama_asli(gudang, nama)
                
                # Jika produk TIDAK ADA di gudang, langsung berhenti
                if not nama_asli:
                    print(f"Produk '{nama}' tidak ditemukan di gudang.")
                    print("Silakan tambah produk ke gudang terlebih dahulu.")
                    continue  # atau return
                
                # Tampilkan info produk yang ditemukan
                print(f"Produk ditemukan: {nama_asli}")
                print(f"Stok tersedia di gudang: {gudang[nama_asli]['stok']}")
                
                # Baru sekarang minta input jumlah (karena produk pasti ada di gudang)
                jumlah = int(input(f"Jumlah yang dipindah ke toko (max {gudang[nama_asli]['stok']}): "))
                
                if jumlah <= 0:
                    print("Jumlah harus lebih dari 0.")
                    continue
                    
                if jumlah > gudang[nama_asli]['stok']:
                    print(f"Jumlah melebihi stok yang tersedia ({gudang[nama_asli]['stok']}).")
                    continue
                
                # Cek apakah produk sudah ada di TOKO (untuk menentukan perlu diskon atau tidak)
                if cari_nama_produk(toko, nama):
                    # Produk sudah ada di toko, tidak perlu diskon
                    print("Produk sudah ada di toko. Menambah stok tanpa diskon baru.")
                    tambah_produk_ke_toko(nama, jumlah)
                else:
                    # Produk baru di toko, perlu diskon
                    print("Produk baru di toko, memerlukan diskon.")
                    diskon_input = input("Diskon (%): ").strip()
                    
                    try:
                        diskon = float(diskon_input) if diskon_input else 0.0
                        
                        if diskon < 0 or diskon > 100:
                            print("Diskon harus antara 0-100.")
                            continue
                            
                        tambah_produk_ke_toko(nama, jumlah, diskon)
                    except ValueError:
                        print("Input diskon harus berupa angka.")
                        continue
                        
            except ValueError:
                print("Input jumlah harus berupa angka.")
            except Exception as e:
                print(f"Terjadi kesalahan: {e}")

        elif pilihan == "2":
            menu_tampilan_produk_utama()
        
        elif pilihan == "3":
            cetak_total_stok()
        
        elif pilihan == "4":
            cari_produk_toko()
        
        elif pilihan == "5":
            update_produk_toko()
        
        elif pilihan == "6":
            lihat_laporan_penjualan()
        
        elif pilihan == "7":
            konfirmasi_pesanan()
        
        elif pilihan == "8":
            if cek_dan_bersihkan_kadaluarsa():
                print("Pemeriksaan kadaluarsa selesai.")
            else:
                print("Tidak ada produk yang kadaluarsa.")
        elif pilihan == "0":
            break
        else:
            print("Pilihan tidak valid. Silakan pilih menu 1-8.")

# This allows the file to be imported without running the menu
if __name__ == "__main__":
    menu_admin()