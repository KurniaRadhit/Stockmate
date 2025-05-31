import os
import getpass
import time
import json
import hashlib
from datetime import datetime
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Import modules (assumed to exist in your project)
from user import menu_user
from admin import menu_admin
from superAdmin import super_admin_menu

# Main user data file
DATA_FOLDER = "Data"
USERS_DATA_FILE = os.path.join(DATA_FOLDER, "users.json")

# List of security questions
SECURITY_QUESTIONS = [
    "Apa nama hewan peliharaan pertama Anda?",
    "Di kota mana Anda dilahirkan?",
    "Apa nama sekolah dasar Anda?",
    "Apa makanan favorit Anda?",
    "Apa nama jalan tempat Anda tinggal saat kecil?",
    "Apa warna favorit Anda?",
    "Siapa nama guru favorit Anda?",
    "Apa hobi pertama Anda?"
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title, color=Fore.CYAN):
    width = 60
    print(color + "=" * width)
    print(color + f"{title.center(width)}")
    print(color + f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S').center(width)}")
    print(color + "=" * width)

def print_menu_item(number, text, highlight=False):
    if highlight:
        print(f"{Fore.BLACK}{Back.CYAN} {number} {Style.RESET_ALL} {Fore.CYAN}{text}")
    else:
        print(f"{Fore.WHITE}{Back.BLUE} {number} {Style.RESET_ALL} {text}")

def animated_loading(text="Loading", duration=1.5):
    chars = "|/-\\"
    for _ in range(int(duration * 10)):
        for char in chars:
            print(f"\r{text} {char}", end="", flush=True)
            time.sleep(0.025)
    print("\r" + " " * (len(text) + 2), end="\r")

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_user_file():
    """Pastikan folder Data ada"""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

def load_users():
    """Load users from JSON file"""
    init_user_file()
    try:
        with open(USERS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return create_default_users()
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: File {USERS_DATA_FILE} rusak. Membuat file baru...")
        return create_default_users()

def create_default_users():
    """Create default users file with super_admin and admin"""
    default_users = {
        "super_admin": {
            "password": hash_password("super123"),
            "role": "super_admin",
            "full_name": "Super Administrator",
            "email": "superadmin@tokoku.com",
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None,
            "permissions": [
                "manage_users",
                "manage_admins", 
                "manage_inventory",
                "view_reports",
                "system_settings",
                "backup_restore"
            ],
            "status": "active"
        },
        "admin": {
            "password": hash_password("admin123"),
            "role": "admin",
            "full_name": "Administrator Toko",
            "email": "admin@tokoku.com",
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None,
            "permissions": [
                "manage_inventory",
                "process_transactions",
                "view_sales_reports",
                "manage_customers"
            ],
            "status": "active",
            "created_by": "super_admin"
        }
    }
    
    if save_users(default_users):
        print(f"{Fore.GREEN}✓ File pengguna default berhasil dibuat!")
        print(f"{Fore.YELLOW}Login default:")
        print(f"  Super Admin - Username: super_admin, Password: super123")
        print(f"  Admin - Username: admin, Password: admin123")
        time.sleep(3)
    
    return default_users

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error menyimpan data user: {str(e)}")
        return False

def authenticate_user(username, password):
    """Authenticate user and return user data with role"""
    users = load_users()
    
    username = username.strip().lower()
    
    if username in users:
        user_data = users[username]
        
        # Check if account is active
        if user_data.get('status', 'active') != 'active':
            return None, "Akun Anda telah dinonaktifkan. Hubungi administrator."
        
        # Verify password
        if user_data['password'] == hash_password(password):
            # Update last login
            users[username]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_users(users)
            
            return user_data, None
        else:
            return None, "Password salah."
    else:
        return None, "Username tidak ditemukan."

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password harus minimal 6 karakter"
    return True, "Password valid"

def validate_username(username):
    """Validate username"""
    if len(username) < 3:
        return False, "Username harus minimal 3 karakter"
    if not username.replace('_', '').isalnum():
        return False, "Username hanya boleh huruf, angka, dan underscore"
    return True, "Username valid"

def select_security_question():
    """Allow user to select a security question"""
    print(f"\n{Fore.YELLOW}▶ Pilih pertanyaan keamanan:")
    for i, question in enumerate(SECURITY_QUESTIONS, 1):
        print(f"{Fore.WHITE}{i}. {question}")
    
    while True:
        try:
            choice = int(input(f"\n{Fore.GREEN}Pilih nomor pertanyaan (1-{len(SECURITY_QUESTIONS)}): ").strip())
            if 1 <= choice <= len(SECURITY_QUESTIONS):
                return SECURITY_QUESTIONS[choice - 1]
            else:
                print(f"{Fore.RED}Pilihan tidak valid! Pilih nomor 1-{len(SECURITY_QUESTIONS)}")
        except ValueError:
            print(f"{Fore.RED}Masukkan nomor yang valid!")

def register_user():
    """Register new user (customer only)"""
    clear_screen()
    print_header("REGISTRASI PENGGUNA BARU", Fore.GREEN)
    
    users = load_users()
    
    print(f"{Fore.YELLOW}▶ Silakan isi data registrasi:")
    
    # Input username
    while True:
        username = input(f"{Fore.WHITE}Username: {Fore.GREEN}").strip().lower()
        
        if not username:
            print(f"{Fore.RED}Username tidak boleh kosong!")
            continue
            
        is_valid, message = validate_username(username)
        if not is_valid:
            print(f"{Fore.RED}{message}")
            continue
            
        if username in users:
            print(f"{Fore.RED}Username sudah digunakan! Pilih username lain.")
            continue
            
        break
    
    # Input full name
    while True:
        full_name = input(f"{Fore.WHITE}Nama Lengkap: {Fore.GREEN}").strip()
        if full_name and len(full_name) >= 2:
            break
        print(f"{Fore.RED}Nama lengkap minimal 2 karakter!")
    
    # Input email
    while True:
        email = input(f"{Fore.WHITE}Email: {Fore.GREEN}").strip().lower()
        if email and "@" in email and "." in email:
            break
        print(f"{Fore.RED}Format email tidak valid!")
    
    # Input phone
    phone = input(f"{Fore.WHITE}No. Telepon: {Fore.GREEN}").strip()
    
    # Input address
    address = input(f"{Fore.WHITE}Alamat: {Fore.GREEN}").strip()
    
    # Input password
    while True:
        password = getpass.getpass(f"{Fore.WHITE}Password: ")
        
        if not password:
            print(f"{Fore.RED}Password tidak boleh kosong!")
            continue
            
        is_valid, message = validate_password(password)
        if not is_valid:
            print(f"{Fore.RED}{message}")
            continue
            
        # Confirm password
        confirm_password = getpass.getpass(f"{Fore.WHITE}Konfirmasi Password: ")
        if password != confirm_password:
            print(f"{Fore.RED}Password tidak cocok! Silakan coba lagi.")
            continue
            
        break
    
    # Select security question
    security_question = select_security_question()
    
    # Input security answer
    while True:
        security_answer = input(f"{Fore.WHITE}Jawaban pertanyaan keamanan: {Fore.GREEN}").strip()
        
        if not security_answer:
            print(f"{Fore.RED}Jawaban tidak boleh kosong!")
            continue
            
        if len(security_answer) < 2:
            print(f"{Fore.RED}Jawaban minimal 2 karakter!")
            continue
            
        break
    
    # Save user data
    users[username] = {
        "password": hash_password(password),
        "role": "user",
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "address": address,
        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": None,
        "security_question": security_question,
        "security_answer": hash_password(security_answer.lower()),
        "status": "active",
        "loyalty_points": 0,
        "total_purchases": 0,
        "preferred_categories": []
    }
    
    print(f"\n{Fore.CYAN}Menyimpan data registrasi...", end="", flush=True)
    animated_loading("Registrasi")
    
    if save_users(users):
        print(f"\n{Fore.GREEN}✓ Registrasi berhasil!")
        print(f"{Fore.CYAN}Username '{username}' telah terdaftar sebagai pelanggan.")
        print(f"{Fore.YELLOW}Sekarang Anda dapat login dengan akun tersebut.")
    else:
        print(f"\n{Fore.RED}✗ Gagal menyimpan data registrasi!")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali ke menu...")

def forgot_password():
    """Password reset function using security question (for users only)"""
    clear_screen()
    print_header("RESET PASSWORD", Fore.YELLOW)
    
    users = load_users()
    
    print(f"{Fore.YELLOW}▶ Reset password hanya tersedia untuk pelanggan.")
    print(f"{Fore.YELLOW}▶ Admin/Super Admin silakan hubungi administrator sistem.")
    print(f"\n{Fore.YELLOW}▶ Masukkan username untuk reset password:")
    username = input(f"{Fore.WHITE}Username: {Fore.GREEN}").strip().lower()
    
    if username not in users:
        print(f"\n{Fore.RED}✗ Username tidak ditemukan!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    user_data = users[username]
    
    # Only allow password reset for regular users
    if user_data.get('role') != 'user':
        print(f"\n{Fore.RED}✗ Reset password hanya tersedia untuk pelanggan!")
        print(f"{Fore.YELLOW}Silakan hubungi administrator sistem.")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    # Check if user has security question
    if 'security_question' not in user_data or 'security_answer' not in user_data:
        print(f"\n{Fore.RED}✗ Akun ini tidak memiliki pertanyaan keamanan!")
        print(f"{Fore.YELLOW}Silakan hubungi administrator untuk reset password.")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    print(f"\n{Fore.CYAN}User ditemukan: {username}")
    print(f"{Fore.YELLOW}▶ Jawab pertanyaan keamanan berikut:")
    print(f"{Fore.WHITE}Pertanyaan: {user_data['security_question']}")
    
    # Verify security answer
    security_answer = input(f"{Fore.WHITE}Jawaban: {Fore.GREEN}").strip()
    
    print(f"\n{Fore.CYAN}Memverifikasi jawaban...", end="", flush=True)
    animated_loading("Verifikasi")
    
    if hash_password(security_answer.lower()) != user_data['security_answer']:
        print(f"\n{Fore.RED}✗ Jawaban salah! Reset password gagal.")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    print(f"\n{Fore.GREEN}✓ Jawaban benar!")
    print(f"{Fore.YELLOW}▶ Masukkan password baru:")
    
    # Input new password
    while True:
        new_password = getpass.getpass(f"{Fore.WHITE}Password baru: ")
        
        if not new_password:
            print(f"{Fore.RED}Password tidak boleh kosong!")
            continue
            
        is_valid, message = validate_password(new_password)
        if not is_valid:
            print(f"{Fore.RED}{message}")
            continue
            
        # Confirm new password
        confirm_password = getpass.getpass(f"{Fore.WHITE}Konfirmasi Password baru: ")
        if new_password != confirm_password:
            print(f"{Fore.RED}Password tidak cocok! Silakan coba lagi.")
            continue
            
        break
    
    # Update password
    users[username]['password'] = hash_password(new_password)
    
    print(f"\n{Fore.CYAN}Menyimpan password baru...", end="", flush=True)
    animated_loading("Reset Password")
    
    if save_users(users):
        print(f"\n{Fore.GREEN}✓ Password berhasil direset!")
        print(f"{Fore.CYAN}Password untuk username '{username}' telah diperbarui.")
        print(f"{Fore.YELLOW}Sekarang Anda dapat login dengan password baru.")
    else:
        print(f"\n{Fore.RED}✗ Gagal menyimpan password baru!")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali ke menu...")

def login_system():
    """Main login system with role detection"""
    clear_screen()
    print_header("LOGIN SISTEM", Fore.BLUE)
    
    print(f"{Fore.YELLOW}▶ Silakan masukkan kredensial login:")
    username = input(f"{Fore.WHITE}Username: {Fore.GREEN}").strip()
    password = getpass.getpass(f"{Fore.WHITE}Password: ")
    
    print(f"\n{Fore.CYAN}Memverifikasi kredensial...", end="", flush=True)
    animated_loading("Autentikasi")
    
    user_data, error_message = authenticate_user(username, password)
    
    if user_data:
        role = user_data.get('role', 'user')
        full_name = user_data.get('full_name', username.title())
        
        print(f"\n{Fore.GREEN}✓ Login berhasil!")
        print(f"{Fore.CYAN}Selamat datang, {full_name}!")
        print(f"{Fore.YELLOW}Role: {role.replace('_', ' ').title()}")
        time.sleep(2)
        
        # Route to appropriate menu based on role
        if role == 'super_admin':
            animated_loading("Memuat modul super admin")
            super_admin_menu()
        elif role == 'admin':
            animated_loading("Memuat modul admin")
            menu_admin()
        elif role == 'user':
            animated_loading("Memuat modul pengguna")
            menu_user(username.lower())
        else:
            print(f"{Fore.RED}Role tidak dikenal: {role}")
            input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        
        return True
    else:
        print(f"\n{Fore.RED}✗ Login gagal: {error_message}")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return False

def display_welcome():
    clear_screen()
    print(f"{Fore.CYAN}")
    
    try:
        with open("banner.txt", "r", encoding="utf-8") as f:
            banner = f.read()
            print(banner)
    except FileNotFoundError:
        print("== SISTEM MANAJEMEN INVENTARIS TOKO ==")
    
    print(f"{Fore.YELLOW}\n                     Manajemen Toko Modern")
    print(f"{Fore.WHITE}\n                      Versi 2.0.0 (2025)")
    time.sleep(1.5)

def main_menu():
    """Simplified main menu without role selection"""
    display_welcome()
    
    while True:
        clear_screen()
        print_header("SISTEM MANAJEMEN INVENTARIS TOKO", Fore.CYAN)
        
        print(f"\n{Fore.YELLOW}Silakan pilih opsi:\n")
        print_menu_item("1", "Login ke Sistem")
        print_menu_item("2", "Registrasi Akun Baru (Pelanggan)")
        print_menu_item("3", "Lupa Password")
        print_menu_item("4", "Tentang Sistem")
        print_menu_item("5", "Keluar", highlight=True)
        
        print(f"\n{Fore.CYAN}{'=' * 60}")
        pilihan = input(f"\n{Fore.GREEN}Pilih opsi {Fore.YELLOW}(1-5){Fore.GREEN}: {Fore.WHITE}").strip()
        
        if pilihan == "1":
            if login_system():
                break  # Exit main menu after successful login and menu completion
            
        elif pilihan == "2":
            register_user()
            
        elif pilihan == "3":
            forgot_password()
            
        elif pilihan == "4":
            show_about_system()
            
        elif pilihan == "5":
            clear_screen()
            print_header("TERIMA KASIH", Fore.GREEN)
            print(f"\n{Fore.YELLOW}Terima kasih telah menggunakan Sistem Manajemen Inventaris Toko!")
            print(f"{Fore.CYAN}Aplikasi akan ditutup dalam beberapa saat...")
            time.sleep(2)
            break
            
        else:
            print(f"\n{Fore.RED}⚠ Pilihan tidak valid. Silakan pilih menu 1-5.")
            input(f"\n{Fore.YELLOW}Tekan Enter untuk melanjutkan...")

def show_about_system():
    """Show information about the system"""
    clear_screen()
    print_header("TENTANG SISTEM", Fore.MAGENTA)
    
    print(f"\n{Fore.CYAN}Sistem Manajemen Inventaris Toko v2.0.0")
    print(f"{Fore.WHITE}")
    print("Sistem ini dirancang untuk mengelola inventaris toko dengan")
    print("tiga tingkat akses pengguna:")
    print()
    print(f"{Fore.YELLOW}🔹 Super Admin:")
    print("  - Manajemen seluruh sistem")
    print("  - Kelola admin dan pengguna")
    print("  - Akses laporan lengkap")
    print("  - Pengaturan sistem")
    print()
    print(f"{Fore.YELLOW}🔹 Admin:")
    print("  - Kelola inventaris produk")
    print("  - Proses transaksi penjualan")
    print("  - Kelola data pelanggan")
    print("  - Lihat laporan penjualan")
    print()
    print(f"{Fore.YELLOW}🔹 Pelanggan:")
    print("  - Lihat katalog produk")
    print("  - Riwayat pembelian")
    print("  - Update profil")
    print("  - Sistem loyalitas")
    print()
    print(f"{Fore.GREEN}Fitur Keamanan:")
    print("- Autentikasi berbasis role")
    print("- Password terenkripsi")
    print("- Pertanyaan keamanan")
    print("- Log aktivitas pengguna")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{Fore.YELLOW}Program dihentikan oleh pengguna. Sampai jumpa kembali!")
    except Exception as e:
        print(f"\n{Fore.RED}Terjadi kesalahan: {str(e)}")
        input("Tekan Enter untuk keluar...")