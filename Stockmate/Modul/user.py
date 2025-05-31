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

def hitung_harga_diskon(harga, diskon):
    return harga * (1 - diskon / 100)

def tampilkan_produk_toko(ascending=True, filter_kategori=None):
    """
    Menampilkan daftar produk di toko dengan opsi pengurutan dan filter kategori.
    """
    data = load_data()
    produk_list = data.get("toko", {})
    filtered = {
        k: v for k, v in produk_list.items()
        if (filter_kategori is None or v["kategori"] == filter_kategori) and v["stok"] > 0
    }

    produk_items = list(filtered.items())
    sorted_produk = quick_sort(produk_items, ascending)

    if not sorted_produk:
        print("Tidak ada produk yang tersedia.")
        return

    tabel = []
    for nama, info in sorted_produk:
        harga_asli = info.get('harga_jual', 0)  # ✅ Perbaikan di sini
        diskon = info.get('diskon', 0)
        harga_diskon = hitung_harga_diskon(harga_asli, diskon)

        tabel.append([
            nama,
            info.get('stok', 0),
            f"Rp {harga_asli:,.2f}",
            f"{diskon}%",
            f"Rp {harga_diskon:,.2f}"
        ])

    print("\n=== DAFTAR PRODUK TERSEDIA ===")
    print(tabulate(
        tabel,
        headers=["Nama", "Stok", "Harga", "Diskon", "Harga Setelah Diskon"],
        tablefmt="grid"
    ))


def menu_tampilkan_produk():
    """
    Menu untuk menampilkan produk di toko dengan filter kategori dan pengurutan.
    """
    print("\n--- Lihat Produk ---")
    print("1. Tampilkan semua produk")
    print("2. Tampilkan berdasarkan kategori")
    opsi = input("Pilih opsi (1/2): ").strip()

    if opsi not in ["1", "2"]:
        print("Opsi tidak valid.")
        return

    filter_kategori = None
    if opsi == "2":
        if not KATEGORI_OPSI:
            print("Belum ada kategori yang tersedia.")
            return
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

    urutan = input("Urutkan nama ascending (a) atau descending (d)? [a/d]: ").lower()
    ascending = (urutan != "d")

    tampilkan_produk_toko(ascending=ascending, filter_kategori=filter_kategori)

# -------------------- PENCARIAN PRODUK --------------------
def sequential_search(data_dict, produk_dicari):
    """
    Melakukan pencarian produk dengan algoritma sequential search.
    """
    for nama_produk in data_dict:
        if nama_produk.lower() == produk_dicari.lower():
            return nama_produk, data_dict[nama_produk]
    return None, None

def cari_produk():
    """
    Mencari produk di toko berdasarkan nama.
    """
    data = load_data()
    toko = data.get("toko", {})
    produk_dicari = input("Masukkan nama produk yang ingin dicari: ").strip()
    nama_asli, hasil = sequential_search(toko, produk_dicari)
    
    if hasil:
        harga_jual = hasil.get('harga_jual', 0)
        diskon = hasil.get('diskon', 0)
        harga_diskon = hitung_harga_diskon(harga_jual, diskon)

        print(f"\nProduk '{nama_asli}' ditemukan:")
        print(f"  Kategori: {hasil.get('kategori', '-')}")
        print(f"  Stok: {hasil.get('stok', 0)}")
        print(f"  Harga: Rp {harga_jual:,.2f}")
        print(f"  Diskon: {diskon}%")
        print(f"  Harga Setelah Diskon: Rp {harga_diskon:,.2f}")
    else:
        print(f"\nProduk '{produk_dicari}' tidak ditemukan atau tidak tersedia.")

# -------------------- KERANJANG BELANJA --------------------
class Keranjang:
    def __init__(self):
        self.items = {}

    def tambah_item(self, nama_produk, jumlah, harga, diskon):
        """
        Menambahkan item ke keranjang atau memperbarui jumlah jika sudah ada.
        """
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0.")
            return

        if nama_produk in self.items:
            self.items[nama_produk]["jumlah"] += jumlah
        else:
            self.items[nama_produk] = {
                "jumlah": jumlah,
                "harga_satuan": harga,
                "diskon": diskon
            }

    def tampilkan_keranjang(self):
        """
        Menampilkan isi keranjang belanja dalam bentuk tabel.
        """
        if not self.items:
            print("\nKeranjang belanja kosong.")
            return False

        tabel = []
        total_harga = 0
        total_item = 0

        for nama, info in self.items.items():
            harga_diskon = hitung_harga_diskon(info["harga_satuan"], info["diskon"])
            subtotal = harga_diskon * info["jumlah"]
            total_harga += subtotal
            total_item += info["jumlah"]

            tabel.append([
                nama,
                info["jumlah"],
                f"Rp {info['harga_satuan']:,.2f}",
                f"{info['diskon']}%",
                f"Rp {harga_diskon:,.2f}",
                f"Rp {subtotal:,.2f}"
            ])

        print("\n=== ISI KERANJANG BELANJA ===")
        print(tabulate(
            tabel,
            headers=["Produk", "Jumlah", "Harga", "Diskon", "Harga Diskon", "Subtotal"],
            tablefmt="grid"
        ))
        print(f"\nTOTAL ITEM : {total_item} pcs")
        print(f"TOTAL BAYAR: Rp {total_harga:,.2f}")
        return True

    def kosongkan_keranjang(self):
        """
        Mengosongkan keranjang belanja.
        """
        self.items.clear()
        print("Keranjang belanja telah dikosongkan.")

    def ubah_jumlah_item(self, nama_produk, jumlah_baru):
        """
        Mengubah jumlah item dalam keranjang.
        """
        if jumlah_baru < 0:
            print("Jumlah tidak boleh negatif.")
            return False

        if nama_produk in self.items:
            self.items[nama_produk]["jumlah"] = jumlah_baru
            print(f"Jumlah '{nama_produk}' diperbarui.")
            return True
        print(f"Produk '{nama_produk}' tidak ditemukan di keranjang.")
        return False

    def hapus_item(self, nama_produk):
        """
        Menghapus item dari keranjang.
        """
        if nama_produk in self.items:
            del self.items[nama_produk]
            print(f"Produk '{nama_produk}' dihapus dari keranjang.")
            return True
        print(f"Produk '{nama_produk}' tidak ditemukan di keranjang.")
        return False

# -------------------- FUNGSI TAMBAH KE KERANJANG --------------------
def tambah_ke_keranjang(keranjang):
    """
    Menambahkan produk ke keranjang belanja.
    """
    data = load_data()
    toko = data.get("toko", {})
    
    nama = input("Masukkan nama produk yang ingin dibeli: ").strip()
    nama_asli = dapatkan_nama_asli(toko, nama)
    
    if not nama_asli:
        print(f"Produk '{nama}' tidak ditemukan.")
        return
    
    stok_tersedia = toko[nama_asli]["stok"]
    if stok_tersedia <= 0:
        print(f"Produk '{nama_asli}' sedang kosong.")
        return

    try:
        jumlah = int(input(f"Jumlah {nama_asli} yang ingin dibeli: "))
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0.")
            return
        
        if jumlah > stok_tersedia:
            print(f"Stok tidak cukup. Stok tersedia: {stok_tersedia}")
            return
        
        harga = toko[nama_asli]["harga_jual"]  # ✅ fix: harga_jual
        diskon = toko[nama_asli].get("diskon", 0)
        
        keranjang.tambah_item(nama_asli, jumlah, harga, diskon)
        print(f"{jumlah} {nama_asli} ditambahkan ke keranjang.")
    
    except ValueError:
        print("Input jumlah tidak valid. Masukkan angka.")

def kelola_keranjang(keranjang):
    """
    Menu untuk mengelola keranjang belanja.
    """
    if not keranjang.tampilkan_keranjang():
        return
    
    data = load_data()
    toko = data.get("toko", {})
    
    while True:
        print("\n--- Kelola Keranjang ---")
        print("1. Ubah jumlah item")
        print("2. Hapus item")
        print("3. Kosongkan keranjang")
        print("4. Kembali")
        
        pilihan = input("Pilih menu (1-4): ").strip()
        
        if pilihan == "1":
            nama = input("Masukkan nama produk yang ingin diubah: ").strip()
            nama_asli = dapatkan_nama_asli(toko, nama)
            
            if not nama_asli or nama_asli not in keranjang.items:
                print(f"Produk '{nama}' tidak ada di keranjang.")
                continue
            
            try:
                jumlah_baru = int(input("Jumlah baru: "))
                if jumlah_baru <= 0:
                    print("Jumlah harus lebih dari 0.")
                    continue
                
                stok_tersedia = toko.get(nama_asli, {}).get("stok", None)
                if stok_tersedia is not None and jumlah_baru > stok_tersedia:
                    print(f"Stok tidak cukup. Stok tersedia: {stok_tersedia}")
                    continue
                
                if keranjang.ubah_jumlah_item(nama_asli, jumlah_baru):
                    print(f"Jumlah {nama_asli} diubah menjadi {jumlah_baru}.")
                    keranjang.tampilkan_keranjang()
            except ValueError:
                print("Input jumlah tidak valid. Masukkan angka.")
        
        elif pilihan == "2":
            nama = input("Masukkan nama produk yang ingin dihapus: ").strip()
            nama_asli = dapatkan_nama_asli(toko, nama)
            
            if not nama_asli or nama_asli not in keranjang.items:
                print(f"Produk '{nama}' tidak ada di keranjang.")
                continue
            
            if keranjang.hapus_item(nama_asli):
                print(f"{nama_asli} dihapus dari keranjang.")
                keranjang.tampilkan_keranjang()
        
        elif pilihan == "3":
            konfirmasi = input("Yakin ingin mengosongkan keranjang? (y/n): ").strip().lower()
            if konfirmasi == 'y':
                keranjang.kosongkan_keranjang()
                break
        
        elif pilihan == "4":
            break
        
        else:
            print("Pilihan tidak valid. Silakan pilih menu 1-4.")


import uuid

def init_antrean_file():
    """
    Inisialisasi file antrean jika belum ada.
    """
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

def checkout(keranjang, nama_pelanggan):
    """
    Proses checkout dan membuat pesanan.
    """
    global antrean_queue
    clean_expired_orders()
    if not keranjang.items:
        print("Keranjang belanja kosong. Tidak dapat melakukan checkout.")
        return False

    # Tampilkan ringkasan pesanan
    if not keranjang.tampilkan_keranjang():
        return False

    konfirmasi = input("\nLanjutkan checkout? (y/n): ").strip().lower()
    if konfirmasi != 'y':
        return False

    # Validasi stok terakhir kali sebelum checkout
    data = load_data()
    for nama_produk, info in keranjang.items.items():
        if nama_produk not in data["toko"] or data["toko"][nama_produk]["stok"] < info["jumlah"]:
            print(f"\nStok untuk '{nama_produk}' tidak mencukupi. Checkout dibatalkan.")
            return False

    # Buat data pesanan
    daftar_pesanan = []
    for nama_produk, info in keranjang.items.items():
        daftar_pesanan.append({
            "produk": nama_produk,
            "jumlah": info["jumlah"],
            "harga_satuan": info["harga_satuan"],
            "diskon": info["diskon"]
        })

    pesanan = {
        "id_pesanan": str(uuid.uuid4()),  # ID unik
        "nama_pembeli": nama_pelanggan,
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pesanan": daftar_pesanan,
        "status": "not confirmed"
    }

    # Kurangi stok di toko
    for item in daftar_pesanan:
        nama_produk = item["produk"]
        if nama_produk in data["toko"]:
            data["toko"][nama_produk]["stok"] -= item["jumlah"]

    # Load queue, add pesanan to queue (FIFO)
    load_antrean()
    antrean_queue.enqueue(pesanan)

    # Simpan perubahan
    save_data(data)
    save_antrean()

    print("\n=== CHECKOUT BERHASIL ===")
    print("Pesanan Anda telah diterima dan menunggu konfirmasi dari admin.")
    print(f"ID Pesanan: {pesanan['id_pesanan']}")
    print(f"Nama Pembeli: {nama_pelanggan}")
    print(f"Waktu: {pesanan['waktu']}")
    print("Status: Menunggu konfirmasi")
    print(f"Posisi dalam antrean: {antrean_queue.size()}")

    # Kosongkan keranjang
    keranjang.kosongkan_keranjang()
    return True

def lihat_status_pesanan(nama_pelanggan):
    """
    Melihat status pesanan berdasarkan nama pelanggan.
    """
    global antrean_queue
    clean_expired_orders()
    load_antrean()

    pesanan_pelanggan = []
    queue_list = antrean_queue.to_list()

    for pesanan in queue_list:
        if pesanan['nama_pembeli'].lower() == nama_pelanggan.lower():
            pesanan_pelanggan.append(pesanan)

    if not pesanan_pelanggan:
        print(f"Tidak ada pesanan atas nama {nama_pelanggan}.")
        return

    print(f"\n=== DAFTAR PESANAN ATAS NAMA {nama_pelanggan.upper()} ===")
    for idx, pesanan in enumerate(pesanan_pelanggan, 1):
        status = "Menunggu konfirmasi" if pesanan['status'] == "not confirmed" else "Dikonfirmasi"

        posisi_antrean = ""
        if pesanan['status'] == "not confirmed":
            for pos, order in enumerate(queue_list, 1):
                if (order['nama_pembeli'] == pesanan['nama_pembeli'] and 
                    order['waktu'] == pesanan['waktu']):
                    posisi_antrean = f" | Posisi antrean: {pos}"
                    break

        print(f"\n{idx}. ID: {pesanan.get('id_pesanan', '-')}")
        print(f"   Waktu: {pesanan['waktu']}")
        print(f"   Status: {status}{posisi_antrean}")
        print("   Daftar Pesanan:")

        total_harga = 0
        for item in pesanan['pesanan']:
            harga_diskon = hitung_harga_diskon(item['harga_satuan'], item['diskon'])
            subtotal = harga_diskon * item['jumlah']
            total_harga += subtotal
            print(f"   - {item['produk']} | Jumlah: {item['jumlah']} | "
                  f"Harga: {item['harga_satuan']} | Diskon: {item['diskon']}% | "
                  f"Subtotal: {subtotal:.2f}")

        print(f"   Total: Rp {total_harga:.2f}")


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
            # Parse the order timestamp
            order_time = datetime.strptime(order['waktu'], "%Y-%m-%d %H:%M:%S")
            
            # Check if the order is older than 12 hours
            if current_time - order_time > timedelta(hours=12):
                expired_count += 1
                # Order is expired - don't add to new_queue
                continue
        
        # Keep orders that are either confirmed or not expired
        new_queue.enqueue(order)
    
    # Replace the old queue with the new one
    antrean_queue = new_queue
    
    # If any orders were removed, update the file
    if expired_count > 0:
        save_antrean()
        print(f"{expired_count} pesanan kedaluwarsa telah dihapus.")
    
    return expired_count

def lihat_antrean_admin():
    """
    Admin function to view current queue status.
    """
    global antrean_queue
    clean_expired_orders()
    load_antrean()
    
    if antrean_queue.is_empty():
        print("Tidak ada pesanan dalam antrean.")
        return
    
    print(f"\n=== STATUS ANTREAN (Total: {antrean_queue.size()} pesanan) ===")
    print("Urutan berdasarkan FIFO (First In, First Out):")
    
    queue_list = antrean_queue.to_list()
    unconfirmed_count = 0
    
    for idx, pesanan in enumerate(queue_list, 1):
        status_text = "Menunggu konfirmasi" if pesanan['status'] == "not confirmed" else "Dikonfirmasi"
        if pesanan['status'] == "not confirmed":
            unconfirmed_count += 1

        id_pesanan = pesanan.get("id_pesanan", "-")
        
        print(f"{idx}. ID: {id_pesanan} | {pesanan['nama_pembeli']} - {pesanan['waktu']} - "
              f"{len(pesanan['pesanan'])} item - {status_text}")
    
    print(f"\nPesanan belum dikonfirmasi: {unconfirmed_count}")
    print(f"Pesanan sudah dikonfirmasi: {antrean_queue.size() - unconfirmed_count}")


# -------------------- MENU USER --------------------
def menu_user(username=None):
    """
    User menu function that can accept username from login
    If no username provided, will ask for name (for backward compatibility)
    """
    if username:
        # User already logged in, use their username
        nama_pelanggan = username.title()
        print(f"\n=== SELAMAT DATANG DI SISTEM TOKO ===")
        print(f"Halo, {nama_pelanggan}!")
    else:
        # Fallback for direct access (backward compatibility)
        print("\n=== SELAMAT DATANG DI SISTEM TOKO ===")
        nama_pelanggan = input("Masukkan nama Anda: ").strip()
        if not nama_pelanggan:
            print("Nama tidak boleh kosong.")
            return
    
    # Initialize shopping cart for this user
    keranjang = Keranjang()
    
    while True:
        print(f"\n=== MENU PELANGGAN - {nama_pelanggan} ===")
        print("1. Lihat produk")
        print("2. Cari produk")
        print("3. Tambah ke keranjang")
        print("4. Lihat keranjang")
        print("5. Kelola keranjang")
        print("6. Checkout")
        print("7. Lihat status pesanan")
        print("0. Keluar")
        
        pilihan = input("Pilih menu (0-7): ").strip()
        
        if pilihan == "1":
            menu_tampilkan_produk()
        
        elif pilihan == "2":
            cari_produk()
        
        elif pilihan == "3":
            tambah_ke_keranjang(keranjang)
        
        elif pilihan == "4":
            keranjang.tampilkan_keranjang()
        
        elif pilihan == "5":
            kelola_keranjang(keranjang)
        
        elif pilihan == "6":
            checkout(keranjang, nama_pelanggan)
        
        elif pilihan == "7":
            lihat_status_pesanan(nama_pelanggan)
        
        elif pilihan == "0":
            print(f"Terima kasih, {nama_pelanggan}! Sampai jumpa kembali.")
            break
        
        else:
            print("Pilihan tidak valid. Silakan pilih menu 0-7.")

# -------------------- MAIN PROGRAM --------------------
if __name__ == "__main__":
    # For direct execution without login system
    menu_user()