import json
import os
from datetime import datetime, timedelta
from tabulate import tabulate

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


# -------------------- TAMBAHKAN PRODUK --------------------

def tambah_produk_ke_gudang(nama, stok, harga_modal=None, harga_jual=None, kategori=None):
    data = load_data()
    nama = nama.strip().title()
    nama_asli = dapatkan_nama_asli(data["gudang"], nama)

    if stok <= 0:
        print("Stok harus lebih dari 0.")
        return

    if nama_asli:  # Produk sudah ada
        data["gudang"][nama_asli]["stok"] += stok
        print(f"Stok produk '{nama_asli}' di gudang berhasil ditambah {stok} unit.")
    else:  # Produk baru
        if harga_modal is None or harga_jual is None or kategori is None:
            print("Harga modal, harga jual, dan kategori diperlukan untuk produk baru.")
            return
        if harga_modal <= 0 or harga_jual <= 0:
            print("Harga modal dan harga jual harus lebih dari 0.")
            return
        if kategori not in KATEGORI_OPSI:
            print(f"Kategori tidak valid. Pilih salah satu dari: {', '.join(KATEGORI_OPSI)}")
            return

        tanggal_kadaluarsa = None
        if kategori in ["Makanan", "Minuman"]:
            try:
                masa_simpan = input("Masukkan masa simpan (jumlah hari): ")
                if masa_simpan:
                    masa_simpan = int(masa_simpan)
                    tanggal_kadaluarsa = (datetime.now() + timedelta(days=masa_simpan)).strftime('%Y-%m-%d')
            except ValueError:
                print("Input masa simpan tidak valid. Menggunakan tanpa tanggal kadaluarsa.")

        data["gudang"][nama] = {
            "stok": stok,
            "kategori": kategori,
            "harga_modal": harga_modal,
            "harga_jual": harga_jual,
            "tanggal_input": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        if tanggal_kadaluarsa:
            data["gudang"][nama]["tanggal_kadaluarsa"] = tanggal_kadaluarsa
            print(f"Produk '{nama}' ditambahkan dengan tanggal kadaluarsa: {tanggal_kadaluarsa}")
        else:
            print(f"Produk '{nama}' ditambahkan tanpa tanggal kadaluarsa.")
        
        print(f"-> Harga beli: {harga_modal}, Harga jual: {harga_jual}")

    save_data(data)

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

# -------------------- HITUNG HARGA DISKON --------------------
def hitung_harga_diskon(harga, diskon):
    return harga * (1 - diskon / 100)

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

# -------------------- FUNGSI PENCARIAN PRODUK DI GUDANG --------------------
def sequential_search(data_dict, produk_dicari):
    for nama_produk in data_dict:
        if nama_produk.lower() == produk_dicari.lower():
            return nama_produk, data_dict[nama_produk]
    return None

def cari_produk_di_gudang():
    data = load_data()
    produk_dicari = input("Masukkan nama produk yang ingin dicari di GUDANG: ").strip()
    hasil = sequential_search(data.get("gudang", {}), produk_dicari)
    if hasil:
        nama_asli, info = hasil
        print(f"\nProduk '{nama_asli}' ditemukan di GUDANG:")
        for k, v in info.items():
            print(f"  {k}: {v}")
    else:
        print(f"\nProduk '{produk_dicari}' tidak ditemukan di GUDANG.")

# -------------------- FUNGSI HAPUS PRODUK DARI GUDANG --------------------
def hapus_produk_dari_gudang(nama):
    data = load_data()
    nama_asli = dapatkan_nama_asli(data["gudang"], nama)
    if not nama_asli:
        print(f"Produk '{nama}' tidak ditemukan di gudang.")
        return
    del data["gudang"][nama_asli]
    save_data(data)
    print(f"Produk '{nama_asli}' berhasil dihapus dari gudang.")

# -------------------- FUNGSI EDIT PRODUK DI GUDANG --------------------
def edit_produk_di_gudang():
    data = load_data()
    produk_dicari = input("Masukkan nama produk yang ingin diedit di GUDANG: ").strip()
    nama_asli = dapatkan_nama_asli(data["gudang"], produk_dicari)

    if not nama_asli:
        print(f"Produk '{produk_dicari}' tidak ditemukan di gudang.")
        return

    produk = data["gudang"][nama_asli]

    while True:
        print(f"\n=== Edit Produk: {nama_asli} ===")
        print("Data saat ini:")
        for k, v in produk.items():
            print(f"  {k}: {v}")

        print("\nPilih data yang ingin diubah:")
        print("1. Nama")
        print("2. Stok")
        print("3. Kategori")
        print("4. Harga beli (modal)")
        print("5. Harga jual")
        print("6. Tanggal kadaluarsa")
        print("0. Selesai edit")
        pilihan = input("Pilih opsi (0-6): ").strip()

        if pilihan == "0":
            break

        toko = data["toko"]
        ada_di_toko = nama_asli in toko

        if pilihan == "1":
            nama_baru = input("Masukkan nama baru: ").strip().title()
            if nama_baru:
                data["gudang"][nama_baru] = data["gudang"].pop(nama_asli)

                # Rename di toko jika ada
                if ada_di_toko:
                    data["toko"][nama_baru] = data["toko"].pop(nama_asli)

                nama_asli = nama_baru
                produk = data["gudang"][nama_asli]
                print("Nama berhasil diubah.")

        elif pilihan == "2":
            try:
                stok_baru = int(input("Masukkan stok baru: ").strip())
                if stok_baru >= 0:
                    produk["stok"] = stok_baru
                    print("Stok berhasil diubah.")
                else:
                    print("Stok tidak boleh negatif.")
            except ValueError:
                print("Input stok tidak valid.")

        elif pilihan == "3":
            print("Pilih kategori baru:")
            for i, kategori in enumerate(KATEGORI_OPSI, 1):
                print(f"{i}. {kategori}")
            try:
                idx = int(input("Masukkan nomor kategori: ")) - 1
                if 0 <= idx < len(KATEGORI_OPSI):
                    produk["kategori"] = KATEGORI_OPSI[idx]
                    if ada_di_toko:
                        toko[nama_asli]["kategori"] = KATEGORI_OPSI[idx]
                    print("Kategori berhasil diubah.")
                else:
                    print("Pilihan kategori tidak valid.")
            except ValueError:
                print("Input kategori tidak valid.")

        elif pilihan == "4":
            try:
                harga_modal_baru = float(input("Masukkan harga modal baru: ").strip())
                if harga_modal_baru > 0:
                    produk["harga_modal"] = harga_modal_baru
                    if ada_di_toko:
                        toko[nama_asli]["harga_modal"] = harga_modal_baru
                    print("Harga modal berhasil diubah.")
                else:
                    print("Harga modal harus lebih dari 0.")
            except ValueError:
                print("Input harga modal tidak valid.")

        elif pilihan == "5":
            try:
                harga_jual_baru = float(input("Masukkan harga jual baru: ").strip())
                if harga_jual_baru > 0:
                    produk["harga_jual"] = harga_jual_baru
                    if ada_di_toko:
                        toko[nama_asli]["harga_jual"] = harga_jual_baru
                    print("Harga jual berhasil diubah.")
                else:
                    print("Harga jual harus lebih dari 0.")
            except ValueError:
                print("Input harga jual tidak valid.")

        elif pilihan == "6":
            tanggal_baru = input("Masukkan tanggal kadaluarsa baru (YYYY-MM-DD), atau kosongkan untuk menghapus: ").strip()
            if tanggal_baru:
                try:
                    datetime.strptime(tanggal_baru, '%Y-%m-%d')
                    produk["tanggal_kadaluarsa"] = tanggal_baru
                    if ada_di_toko:
                        toko[nama_asli]["tanggal_kadaluarsa"] = tanggal_baru
                    print("Tanggal kadaluarsa berhasil diubah.")
                except ValueError:
                    print("Format tanggal tidak valid.")
            else:
                produk.pop("tanggal_kadaluarsa", None)
                if ada_di_toko:
                    toko[nama_asli].pop("tanggal_kadaluarsa", None)
                print("Tanggal kadaluarsa dihapus.")

        else:
            print("Pilihan tidak valid.")

    save_data(data)
    print(f"\nProduk '{nama_asli}' berhasil diperbarui.")


# -------------------- LOAD DATA ANTREAN.JSON --------------------
def load_antrean():
    if not os.path.exists(ANTREAN_PATH):
        with open(ANTREAN_PATH, 'w') as f:
            json.dump([], f)
    with open(ANTREAN_PATH, 'r') as f:
        return json.load(f)
    
# -------------------- PILIH RENTANG WAKTU --------------------
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
        elif pilihan == "1":  
            return today_start, today_start + timedelta(days=1)
        elif pilihan == "2":  
            yesterday = today_start - timedelta(days=1)
            return yesterday, today_start
        elif pilihan == "3":  
            return today_start - timedelta(days=7), today_start + timedelta(days=1)
        elif pilihan == "4":  
            return today_start - timedelta(days=30), today_start + timedelta(days=1)
        elif pilihan == "5":  
            start_of_month = datetime(today.year, today.month, 1)
            return start_of_month, today_start + timedelta(days=1)
        elif pilihan == "6":  
            if today.month == 1:
                start_of_last_month = datetime(today.year - 1, 12, 1)
                end_of_last_month = datetime(today.year, 1, 1)
            else:
                start_of_last_month = datetime(today.year, today.month - 1, 1)
                end_of_last_month = datetime(today.year, today.month, 1)
            return start_of_last_month, end_of_last_month
        elif pilihan == "7":  
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
        elif pilihan == "8":  
            return None, None
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

# -------------------- FILTER PESANAN BERDASARKAN RENTANG TANGGAL --------------------
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
            continue  
    return filtered_pesanan

# -------------------- FUNGSI LAPORAN PENJUALAN (DENGAN KEUNTUNGAN) --------------------
def lihat_laporan_penjualan():
    print("\n=== LAPORAN PENJUALAN ===")
    start_date, end_date = pilih_rentang_waktu()
    if start_date is None and end_date is None and not isinstance(start_date, datetime):
        print("Kembali ke menu utama.")
        return

    if start_date is None and end_date is None:
        print("\nMenampilkan laporan untuk: SEMUA WAKTU")
    else:
        print(f"\nMenampilkan laporan untuk periode: {start_date.strftime('%d-%m-%Y')} hingga {(end_date - timedelta(days=1)).strftime('%d-%m-%Y')}")

    antrean = load_antrean()
    antrean_confirmed = [p for p in antrean if p['status'] == "confirmed"]
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
            harga_diskon = item['harga_satuan'] * (1 - item['diskon'] / 100)
            subtotal = harga_diskon * item['jumlah']
            total_harga += subtotal
            print(f"   - {item['produk']} | Jumlah: {item['jumlah']} | "
                  f"Harga: {item['harga_satuan']} | Diskon: {item['diskon']}% | "
                  f"Subtotal: {subtotal}")
        print(f"   Total Harga: {total_harga:,.2f}")

    pilihan = input("\nApakah Anda ingin melihat ringkasan penjualan? (y/n): ").strip().lower()
    if pilihan != "y":
        return

    print("\n\nB. RINGKASAN TOTAL PENJUALAN")
    print("----------------------------------")
    print(f"Jumlah Transaksi: {len(filtered_pesanan)}")

    total_per_produk = {}
    total_per_kategori = {}
    untung_per_produk = {}
    total_keseluruhan = 0
    total_untung = 0

    data = load_data()
    produk_toko = data.get("toko", {})

    for pesanan in filtered_pesanan:
        subtotal_transaksi = 0
        for item in pesanan['pesanan']:
            nama_produk = item['produk']
            jumlah = item['jumlah']
            harga_satuan = item['harga_satuan']
            diskon = item['diskon']
            harga_diskon = harga_satuan * (1 - diskon / 100)
            subtotal = jumlah * harga_diskon
            subtotal_transaksi += subtotal

            # Total per produk
            if nama_produk not in total_per_produk:
                total_per_produk[nama_produk] = {'jumlah': 0, 'total_harga': 0}
            total_per_produk[nama_produk]['jumlah'] += jumlah
            total_per_produk[nama_produk]['total_harga'] += subtotal

            # Dapatkan kategori
            kategori = "Tidak terkategori"
            nama_asli = dapatkan_nama_asli(produk_toko, nama_produk)
            if nama_asli and 'kategori' in produk_toko.get(nama_asli, {}):
                kategori = produk_toko[nama_asli]['kategori']
            if kategori not in total_per_kategori:
                total_per_kategori[kategori] = {'jumlah': 0, 'total_harga': 0}
            total_per_kategori[kategori]['jumlah'] += jumlah
            total_per_kategori[kategori]['total_harga'] += subtotal

            # Hitung keuntungan
            harga_beli = produk_toko.get(nama_asli, {}).get('harga_beli', 0)
            untung = (harga_diskon - harga_beli) * jumlah
            total_untung += untung
            if nama_produk not in untung_per_produk:
                untung_per_produk[nama_produk] = 0
            untung_per_produk[nama_produk] += untung

        total_keseluruhan += subtotal_transaksi

    # Tampilkan ringkasan per produk
    print("\nRINGKASAN PENJUALAN PER PRODUK:")
    header = ["Produk", "Jumlah Terjual", "Total Penjualan", "Keuntungan"]
    table_data = []
    for produk in total_per_produk:
        jumlah = total_per_produk[produk]['jumlah']
        total_harga = total_per_produk[produk]['total_harga']
        untung = untung_per_produk.get(produk, 0)
        table_data.append([produk, jumlah, f"Rp {total_harga:,.2f}", f"Rp {untung:,.2f}"])
    print(tabulate(table_data, headers=header, tablefmt="grid"))

    # Tampilkan ringkasan per kategori
    print("\nRINGKASAN PENJUALAN PER KATEGORI:")
    header = ["Kategori", "Jumlah Terjual", "Total Penjualan", "Persentase"]
    table_data = []
    for kategori, info in total_per_kategori.items():
        persentase = (info['total_harga'] / total_keseluruhan * 100) if total_keseluruhan > 0 else 0
        table_data.append([
            kategori,
            info['jumlah'],
            f"Rp {info['total_harga']:,.2f}",
            f"{persentase:.2f}%"
        ])
    print(tabulate(table_data, headers=header, tablefmt="grid"))

    # Total dan rata-rata
    print(f"\nTOTAL PENJUALAN KESELURUHAN: Rp {total_keseluruhan:,.2f}")
    print(f"TOTAL KEUNTUNGAN: Rp {total_untung:,.2f}")
    if start_date and end_date:
        jumlah_hari = (end_date - start_date).days
        if jumlah_hari > 0:
            rata_rata_per_hari = total_keseluruhan / jumlah_hari
            print(f"RATA-RATA PENJUALAN PER HARI: Rp {rata_rata_per_hari:,.2f}")

    # Export opsional
    pilihan = input("\nApakah Anda ingin mengekspor laporan ini sebagai CSV? (y/n): ").strip().lower()
    if pilihan == "y":
        export_laporan_to_csv(
            filtered_pesanan,
            total_per_produk,
            total_per_kategori,
            total_keseluruhan,
            start_date,
            end_date,
            untung_per_produk,
            total_untung
        )
# -------------------- EKSPORT LAPORAN KE CSV --------------------
def export_laporan_to_csv(pesanan_list, total_per_produk, total_per_kategori, total_keseluruhan, start_date, end_date, produk_dict):
    import csv
    from datetime import datetime, timedelta
    import os

    def format_number(value):
        if isinstance(value, (int, float)):
            formatted = f"{value:,.1f}".replace(',', '_').replace('.', ',').replace('_', '.')
            if formatted.endswith(',0'):
                formatted = formatted[:-2]
            return f'"{formatted}"'
        return f'"{value}"' if value else ""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if start_date and end_date:
        period = f"{start_date.strftime('%Y%m%d')}_to_{(end_date - timedelta(days=1)).strftime('%Y%m%d')}"
    else:
        period = "all_time"
    filename = f"laporan_penjualan_{period}_{timestamp}.csv"

    total_laba = 0  # TAMBAHAN: untuk menghitung total laba

    try:
        try:
            import xlsxwriter
            excel_available = True
        except ImportError:
            excel_available = False

        if excel_available:
            try:
                excel_filename = f"laporan_penjualan_{period}_{timestamp}.xlsx"
                workbook = xlsxwriter.Workbook(excel_filename)
                worksheet = workbook.add_worksheet('Laporan Penjualan')
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

                worksheet.set_column('A:I', 15)
                row = 0
                worksheet.write(row, 0, 'LAPORAN PENJUALAN', title_format)
                row += 1
                if start_date and end_date:
                    worksheet.write(row, 0, f"Periode: {start_date.strftime('%d-%m-%Y')} hingga {(end_date - timedelta(days=1)).strftime('%d-%m-%Y')}")
                else:
                    worksheet.write(row, 0, 'Periode: SEMUA WAKTU')
                row += 2
                worksheet.write(row, 0, 'DAFTAR TRANSAKSI', subheader_format)
                row += 1

                col_headers = ['No.', 'Nama Pembeli', 'Waktu', 'Produk', 'Jumlah', 'Harga Satuan', 'Diskon', 'Subtotal', 'Laba']
                for col, header in enumerate(col_headers):
                    worksheet.write(row, col, header, header_format)
                row += 1
                transaction_idx = 1
                for pesanan in pesanan_list:
                    for item in pesanan['pesanan']:
                        harga_diskon = item['harga_satuan'] * (1 - item['diskon']/100)
                        subtotal = harga_diskon * item['jumlah']
                        modal_satuan = produk_dict.get(item['produk'], {}).get('harga_modal', 0)
                        laba = (harga_diskon - modal_satuan) * item['jumlah']
                        total_laba += laba
                        waktu = pesanan['waktu']
                        if isinstance(waktu, str):
                            try:
                                waktu = datetime.strptime(waktu, "%Y-%m-%d %H:%M:%S")
                            except:
                                pass
                        worksheet.write(row, 0, transaction_idx, text_format)
                        worksheet.write(row, 1, pesanan['nama_pembeli'], text_format)
                        if isinstance(waktu, datetime):
                            worksheet.write_datetime(row, 2, waktu, date_format)
                        else:
                            worksheet.write(row, 2, str(waktu), text_format)
                        worksheet.write(row, 3, item['produk'], text_format)
                        worksheet.write(row, 4, item['jumlah'], number_format)
                        worksheet.write(row, 5, item['harga_satuan'], currency_format)
                        worksheet.write(row, 6, f"{item['diskon']}%", text_format)
                        worksheet.write(row, 7, subtotal, currency_format)
                        worksheet.write(row, 8, laba, currency_format)
                        row += 1
                        transaction_idx += 1
                row += 1
                worksheet.write(row, 0, 'RINGKASAN PER PRODUK', subheader_format)
                row += 1
                prod_headers = ['Produk', 'Jumlah Terjual', 'Total Penjualan']
                for col, header in enumerate(prod_headers):
                    worksheet.write(row, col, header, header_format)
                row += 1
                for produk, info in total_per_produk.items():
                    worksheet.write(row, 0, produk, text_format)
                    worksheet.write(row, 1, info['jumlah'], number_format)
                    worksheet.write(row, 2, info['total_harga'], currency_format)
                    row += 1
                row += 1
                worksheet.write(row, 0, 'RINGKASAN PER KATEGORI', subheader_format)
                row += 1
                cat_headers = ['Kategori', 'Jumlah Terjual', 'Total Penjualan', 'Persentase']
                for col, header in enumerate(cat_headers):
                    worksheet.write(row, col, header, header_format)
                row += 1
                for kategori, info in total_per_kategori.items():
                    persentase = (info['total_harga'] / total_keseluruhan) if total_keseluruhan > 0 else 0
                    worksheet.write(row, 0, kategori, text_format)
                    worksheet.write(row, 1, info['jumlah'], number_format)
                    worksheet.write(row, 2, info['total_harga'], currency_format)
                    worksheet.write(row, 3, persentase, percentage_format)
                    row += 1
                row += 1
                worksheet.write(row, 0, 'TOTAL KESELURUHAN', subheader_format)
                worksheet.write(row, 2, total_keseluruhan, currency_format)
                worksheet.write(row, 3, 'TOTAL LABA', subheader_format)
                worksheet.write(row, 4, total_laba, currency_format)
                row += 1
                if start_date and end_date:
                    jumlah_hari = (end_date - start_date).days
                    if jumlah_hari > 0:
                        rata_rata_per_hari = total_keseluruhan / jumlah_hari
                        rata_rata_laba_per_hari = total_laba / jumlah_hari
                        worksheet.write(row, 0, 'RATA-RATA PER HARI', subheader_format)
                        worksheet.write(row, 2, rata_rata_per_hari, currency_format)
                        worksheet.write(row, 4, rata_rata_laba_per_hari, currency_format)
                workbook.close()
                try:
                    if os.name == 'nt':
                        os.system(f'start excel "{excel_filename}"')
                    elif os.name == 'posix':
                        if os.system('which open > /dev/null') == 0:
                            os.system(f'open "{excel_filename}"')
                        else:
                            os.system(f'xdg-open "{excel_filename}"')
                except:
                    pass
                print(f"\nLaporan berhasil diekspor ke file Excel '{excel_filename}'")
                return True, excel_filename
            except Exception as excel_error:
                print(f"Gagal membuat file Excel: {excel_error}")
                pass

        # CSV BAGIAN:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["LAPORAN PENJUALAN", "", "", "", "", "", "", "", ""])
            if start_date and end_date:
                writer.writerow([f"Periode: {start_date.strftime('%d-%m-%Y')} hingga {(end_date - timedelta(days=1)).strftime('%d-%m-%Y')}", "", "", "", "", "", "", "", ""])
            else:
                writer.writerow(["Periode: SEMUA WAKTU", "", "", "", "", "", "", "", ""])
            writer.writerow([])
            writer.writerow(["DAFTAR TRANSAKSI", "", "", "", "", "", "", "", ""])
            writer.writerow(["No.", "Nama Pembeli", "Waktu", "Produk", "Jumlah", "Harga Satuan", "Diskon", "Subtotal", "Laba"])
            transaction_idx = 1
            for pesanan in pesanan_list:
                for item in pesanan['pesanan']:
                    harga_diskon = item['harga_satuan'] * (1 - item['diskon']/100)
                    subtotal = harga_diskon * item['jumlah']
                    modal_satuan = produk_dict.get(item['produk'], {}).get('harga_modal', 0)
                    laba = (harga_diskon - modal_satuan) * item['jumlah']
                    total_laba += laba
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
                        format_number(subtotal),
                        format_number(laba)
                    ])
                    transaction_idx += 1
            writer.writerow([])
            writer.writerow(["RINGKASAN PER PRODUK", "", "", "", "", "", "", "", ""])
            writer.writerow(["Produk", "Jumlah Terjual", "Total Penjualan", "", "", "", "", "", ""])
            for produk, info in total_per_produk.items():
                writer.writerow([
                    produk,
                    info['jumlah'],
                    format_number(info['total_harga']),
                    "", "", "", "", "", ""
                ])
            writer.writerow([])
            writer.writerow(["RINGKASAN PER KATEGORI", "", "", "", "", "", "", "", ""])
            writer.writerow(["Kategori", "Jumlah Terjual", "Total Penjualan", "Persentase", "", "", "", "", ""])
            for kategori, info in total_per_kategori.items():
                persentase = (info['total_harga'] / total_keseluruhan * 100) if total_keseluruhan > 0 else 0
                writer.writerow([
                    kategori,
                    info['jumlah'],
                    format_number(info['total_harga']),
                    f'"{persentase:.2f}%"',
                    "", "", "", "", ""
                ])
            writer.writerow([])
            writer.writerow(["TOTAL KESELURUHAN", "", format_number(total_keseluruhan), "", "", "", "", "", ""])
            writer.writerow(["TOTAL LABA", "", format_number(total_laba), "", "", "", "", "", ""])
            if start_date and end_date:
                jumlah_hari = (end_date - start_date).days
                if jumlah_hari > 0:
                    rata_rata_per_hari = total_keseluruhan / jumlah_hari
                    rata_rata_laba_per_hari = total_laba / jumlah_hari
                    writer.writerow(["RATA-RATA PER HARI", "", format_number(rata_rata_per_hari), "", "", "", "", "", ""])
                    writer.writerow(["RATA-RATA LABA PER HARI", "", format_number(rata_rata_laba_per_hari), "", "", "", "", "", ""])
        if not excel_available:
            try:
                if os.name == 'nt':
                    os.system(f'start excel "{filename}"')
                elif os.name == 'posix':
                    if os.system('which open > /dev/null') == 0:
                        os.system(f'open "{filename}"')
                    else:
                        os.system(f'xdg-open "{filename}"')
            except:
                pass
            print(f"\nLaporan berhasil diekspor ke file CSV '{filename}'")
            return True, filename
    except Exception as e:
        print(f"\nTerjadi kesalahan saat mengekspor laporan: {e}")
        return False, str(e)

# -------------------- SUPER ADMIN MENU --------------------
def super_admin_menu():
    if cek_dan_bersihkan_kadaluarsa():
        print("Pemeriksaan kadaluarsa selesai.")
        
    while True:
        print("\n=== SUPER ADMIN MENU ===")
        print("1. Tambah produk ke gudang")
        print("2. Tampilkan produk")
        print("3. Cetak total stok produk (gudang + toko)")
        print("4. Cari produk di gudang")
        print("5. Edit produk di gudang")
        print("6. Hapus produk dari gudang")
        print("7. Lihat laporan penjualan")
        print("8. Periksa produk kadaluarsa")
        print("0. Kembali ke menu utama")
        pilihan = input("Pilih menu (0-8): ").strip()
        
        if pilihan == "0":
            break
        elif pilihan == "1":
            nama = input("Nama produk: ").strip()
            data = load_data()
            try:
                stok = int(input("Stok awal: "))    
                if cari_nama_produk(data["gudang"], nama):
                    tambah_produk_ke_gudang(nama, stok)
                else:
                    harga_modal = float(input("Harga Modal: "))
                    harga_jual = float(input("Harga Jual: "))
                    print("Pilih kategori:")
                    for i, kategori in enumerate(KATEGORI_OPSI):
                        print(f"{i+1}. {kategori}")
                    idx = int(input("Masukkan nomor kategori: ")) - 1
                    if idx < 0 or idx >= len(KATEGORI_OPSI):
                        print("Kategori tidak valid.")
                        return
                    kategori = KATEGORI_OPSI[idx]
                    tambah_produk_ke_gudang(nama, stok, harga_modal, harga_jual, kategori)
            except (ValueError, IndexError):
                print("Input tidak valid. Pastikan semua data benar.")
        elif pilihan == "2":
            menu_tampilan_produk_utama()
        elif pilihan == "3":
            cetak_total_stok()
        elif pilihan == "4":
            cari_produk_di_gudang()
        elif pilihan == "5":
            edit_produk_di_gudang()
        elif pilihan == "6":
            nama_produk = input("Masukkan nama produk yang ingin dihapus dari gudang: ").strip()
            hapus_produk_dari_gudang(nama_produk)
        elif pilihan == "7":
            lihat_laporan_penjualan() 
        elif pilihan == "8":
            if cek_dan_bersihkan_kadaluarsa():
                print("Pemeriksaan kadaluarsa selesai.")
            else:
                print("Tidak ada produk yang kadaluarsa.")
        else:
            print("Pilihan tidak valid. Coba lagi.")

if __name__ == "__main__":
    super_admin_menu()