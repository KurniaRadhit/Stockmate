import json
import os
import hashlib
import getpass
from datetime import datetime
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

DATA_FOLDER = "Data"
USERS_DATA_FILE = os.path.join(DATA_FOLDER, "users.json")

def clear_screen():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title, color=Fore.CYAN):
    width = 60
    print(color + "=" * width)
    print(color + f"{title.center(width)}")
    print(color + f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S').center(width)}")
    print(color + "=" * width)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_user_folder():
    """Buat folder Data jika belum ada"""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

def load_users():
    """Load users from JSON file"""
    init_user_folder()
    try:
        with open(USERS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: File users.json rusak!")
        return {}

def save_users(users):
    """Save users to JSON file"""
    init_user_folder()
    try:
        with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error menyimpan data user: {str(e)}")
        return False


def validate_username(username):
    """Validate username"""
    if len(username) < 3:
        return False, "Username harus minimal 3 karakter"
    if not username.replace('_', '').isalnum():
        return False, "Username hanya boleh huruf, angka, dan underscore"
    return True, "Username valid"

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password harus minimal 6 karakter"
    return True, "Password valid"

def view_all_users():
    """Display all users in the system"""
    clear_screen()
    print_header("DAFTAR SEMUA PENGGUNA", Fore.CYAN)
    
    users = load_users()
    
    if not users:
        print(f"{Fore.RED}Tidak ada pengguna dalam sistem!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    # Group users by role
    roles = {
        'super_admin': [],
        'admin': [],
        'user': []
    }
    
    for username, data in users.items():
        role = data.get('role', 'user')
        roles[role].append((username, data))
    
    # Display Super Admins
    if roles['super_admin']:
        print(f"\n{Fore.MAGENTA}🔸 SUPER ADMIN ({len(roles['super_admin'])} orang):")
        for username, data in roles['super_admin']:
            status_color = Fore.GREEN if data.get('status') == 'active' else Fore.RED
            print(f"  {Fore.WHITE}• {username} ({data.get('full_name', 'N/A')}) - {status_color}{data.get('status', 'unknown')}")
            print(f"    Email: {data.get('email', 'N/A')} | Last Login: {data.get('last_login', 'Never')}")
    
    # Display Admins
    if roles['admin']:
        print(f"\n{Fore.BLUE}🔸 ADMIN ({len(roles['admin'])} orang):")
        for username, data in roles['admin']:
            status_color = Fore.GREEN if data.get('status') == 'active' else Fore.RED
            print(f"  {Fore.WHITE}• {username} ({data.get('full_name', 'N/A')}) - {status_color}{data.get('status', 'unknown')}")
            print(f"    Email: {data.get('email', 'N/A')} | Last Login: {data.get('last_login', 'Never')}")
            print(f"    Dibuat oleh: {data.get('created_by', 'N/A')} | Tanggal: {data.get('created_date', 'N/A')}")
    
    # Display Users/Customers
    if roles['user']:
        print(f"\n{Fore.GREEN}🔸 PELANGGAN ({len(roles['user'])} orang):")
        for username, data in roles['user']:
            status_color = Fore.GREEN if data.get('status') == 'active' else Fore.RED
            loyalty_points = data.get('loyalty_points', 0)
            total_purchases = data.get('total_purchases', 0)
            print(f"  {Fore.WHITE}• {username} ({data.get('full_name', 'N/A')}) - {status_color}{data.get('status', 'unknown')}")
            print(f"    Email: {data.get('email', 'N/A')} | Points: {loyalty_points} | Pembelian: {total_purchases}x")
    
    print(f"\n{Fore.CYAN}Total Pengguna: {len(users)} orang")
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

def create_admin():
    """Create new admin account"""
    clear_screen()
    print_header("TAMBAH ADMIN BARU", Fore.GREEN)
    
    users = load_users()
    
    print(f"{Fore.YELLOW}▶ Silakan isi data admin baru:")
    
    # Input username
    while True:
        username = input(f"{Fore.WHITE}Username Admin: {Fore.GREEN}").strip().lower()
        
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
            # Check if email already exists
            email_exists = any(user_data.get('email') == email for user_data in users.values())
            if email_exists:
                print(f"{Fore.RED}Email sudah digunakan!")
                continue
            break
        print(f"{Fore.RED}Format email tidak valid!")
    
    # Input phone (optional)
    phone = input(f"{Fore.WHITE}No. Telepon (opsional): {Fore.GREEN}").strip()
    
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
    
    # Set admin permissions
    print(f"\n{Fore.YELLOW}▶ Pilih level admin:")
    print(f"{Fore.WHITE}1. Admin Standar (kelola inventaris & transaksi)")
    print(f"{Fore.WHITE}2. Admin Senior (+ kelola laporan & pelanggan)")
    
    while True:
        try:
            admin_level = int(input(f"\n{Fore.GREEN}Pilih level (1-2): ").strip())
            if admin_level in [1, 2]:
                break
            else:
                print(f"{Fore.RED}Pilihan tidak valid!")
        except ValueError:
            print(f"{Fore.RED}Masukkan angka 1 atau 2!")
    
    # Set permissions based on level
    if admin_level == 1:
        permissions = [
            "manage_inventory",
            "process_transactions"
        ]
    else:  # admin_level == 2
        permissions = [
            "manage_inventory",
            "process_transactions",
            "view_sales_reports",
            "manage_customers",
            "view_analytics"
        ]
    
    # Confirmation
    print(f"\n{Fore.CYAN}▶ Konfirmasi data admin baru:")
    print(f"{Fore.WHITE}Username: {username}")
    print(f"{Fore.WHITE}Nama: {full_name}")
    print(f"{Fore.WHITE}Email: {email}")
    print(f"{Fore.WHITE}Phone: {phone if phone else 'Tidak diisi'}")
    print(f"{Fore.WHITE}Level: {'Admin Senior' if admin_level == 2 else 'Admin Standar'}")
    print(f"{Fore.WHITE}Permissions: {', '.join(permissions)}")
    
    confirm = input(f"\n{Fore.YELLOW}Buat admin ini? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print(f"{Fore.YELLOW}Pembuatan admin dibatalkan.")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    # Save admin data
    users[username] = {
        "password": hash_password(password),
        "role": "admin",
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": None,
        "permissions": permissions,
        "status": "active",
        "created_by": "super_admin",
        "admin_level": admin_level
    }
    
    print(f"\n{Fore.CYAN}Menyimpan data admin...", end="", flush=True)
    import time
    time.sleep(1)
    
    if save_users(users):
        print(f"\n{Fore.GREEN}✓ Admin berhasil dibuat!")
        print(f"{Fore.CYAN}Username '{username}' telah terdaftar sebagai admin.")
        print(f"{Fore.YELLOW}Admin dapat langsung login menggunakan kredensial yang dibuat.")
    else:
        print(f"\n{Fore.RED}✗ Gagal menyimpan data admin!")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

def manage_admin_accounts():
    """Manage existing admin accounts"""
    clear_screen()
    print_header("KELOLA AKUN ADMIN", Fore.BLUE)
    
    users = load_users()
    
    # Get all admins
    admins = {username: data for username, data in users.items() if data.get('role') == 'admin'}
    
    if not admins:
        print(f"{Fore.RED}Tidak ada admin dalam sistem!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    print(f"{Fore.YELLOW}▶ Daftar Admin:")
    admin_list = list(admins.keys())
    
    for i, username in enumerate(admin_list, 1):
        data = admins[username]
        status_color = Fore.GREEN if data.get('status') == 'active' else Fore.RED
        level = 'Senior' if data.get('admin_level') == 2 else 'Standar'
        print(f"{Fore.WHITE}{i}. {username} ({data.get('full_name')}) - {status_color}{data.get('status')} {Fore.CYAN}[{level}]")
    
    print(f"\n{Fore.YELLOW}Pilih admin untuk dikelola:")
    
    while True:
        try:
            choice = int(input(f"\n{Fore.GREEN}Nomor admin (0 untuk kembali): ").strip())
            if choice == 0:
                return
            elif 1 <= choice <= len(admin_list):
                selected_admin = admin_list[choice - 1]
                break
            else:
                print(f"{Fore.RED}Pilihan tidak valid!")
        except ValueError:
            print(f"{Fore.RED}Masukkan nomor yang valid!")
    
    # Admin management submenu
    admin_management_menu(selected_admin, users)

def admin_management_menu(admin_username, users):
    """Submenu for managing specific admin"""
    while True:
        clear_screen()
        admin_data = users[admin_username]
        print_header(f"KELOLA ADMIN: {admin_username.upper()}", Fore.BLUE)
        
        print(f"\n{Fore.CYAN}▶ Info Admin:")
        print(f"{Fore.WHITE}Nama: {admin_data.get('full_name')}")
        print(f"{Fore.WHITE}Email: {admin_data.get('email')}")
        print(f"{Fore.WHITE}Status: {Fore.GREEN if admin_data.get('status') == 'active' else Fore.RED}{admin_data.get('status')}")
        print(f"{Fore.WHITE}Level: {'Senior' if admin_data.get('admin_level') == 2 else 'Standar'}")
        print(f"{Fore.WHITE}Last Login: {admin_data.get('last_login', 'Never')}")
        
        print(f"\n{Fore.YELLOW}▶ Pilihan aksi:")
        print(f"{Fore.WHITE}1. Reset Password")
        print(f"{Fore.WHITE}2. {'Nonaktifkan' if admin_data.get('status') == 'active' else 'Aktifkan'} Akun")
        print(f"{Fore.WHITE}3. Update Level Admin")
        print(f"{Fore.WHITE}4. Update Info Kontak")
        print(f"{Fore.WHITE}5. Hapus Admin")
        print(f"{Fore.WHITE}0. Kembali")
        
        choice = input(f"\n{Fore.GREEN}Pilih aksi (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            reset_admin_password(admin_username, users)
        elif choice == "2":
            toggle_admin_status(admin_username, users)
        elif choice == "3":
            update_admin_level(admin_username, users)
        elif choice == "4":
            update_admin_contact(admin_username, users)
        elif choice == "5":
            if delete_admin(admin_username, users):
                break  # Exit if admin was deleted
        else:
            print(f"\n{Fore.RED}Pilihan tidak valid!")
            input(f"\n{Fore.YELLOW}Tekan Enter untuk melanjutkan...")

def reset_admin_password(admin_username, users):
    """Reset admin password"""
    clear_screen()
    print_header(f"RESET PASSWORD: {admin_username.upper()}", Fore.YELLOW)
    
    print(f"{Fore.YELLOW}▶ Membuat password baru untuk admin {admin_username}")
    
    while True:
        new_password = getpass.getpass(f"{Fore.WHITE}Password baru: ")
        
        if not new_password:
            print(f"{Fore.RED}Password tidak boleh kosong!")
            continue
            
        is_valid, message = validate_password(new_password)
        if not is_valid:
            print(f"{Fore.RED}{message}")
            continue
            
        confirm_password = getpass.getpass(f"{Fore.WHITE}Konfirmasi Password: ")
        if new_password != confirm_password:
            print(f"{Fore.RED}Password tidak cocok!")
            continue
            
        break
    
    # Update password
    users[admin_username]['password'] = hash_password(new_password)
    
    if save_users(users):
        print(f"\n{Fore.GREEN}✓ Password admin berhasil direset!")
        print(f"{Fore.CYAN}Admin {admin_username} dapat login dengan password baru.")
    else:
        print(f"\n{Fore.RED}✗ Gagal menyimpan password baru!")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

def toggle_admin_status(admin_username, users):
    """Toggle admin active/inactive status"""
    current_status = users[admin_username].get('status', 'active')
    new_status = 'inactive' if current_status == 'active' else 'active'
    action = 'menonaktifkan' if new_status == 'inactive' else 'mengaktifkan'
    
    confirm = input(f"\n{Fore.YELLOW}Yakin ingin {action} admin {admin_username}? (y/n): ").strip().lower()
    
    if confirm == 'y':
        users[admin_username]['status'] = new_status
        
        if save_users(users):
            print(f"\n{Fore.GREEN}✓ Status admin berhasil diubah menjadi {new_status}!")
        else:
            print(f"\n{Fore.RED}✗ Gagal mengubah status admin!")
    else:
        print(f"{Fore.YELLOW}Perubahan status dibatalkan.")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

def update_admin_level(admin_username, users):
    """Update admin level"""
    current_level = users[admin_username].get('admin_level', 1)
    current_level_name = 'Senior' if current_level == 2 else 'Standar'
    
    print(f"\n{Fore.CYAN}Level saat ini: {current_level_name}")
    print(f"{Fore.YELLOW}▶ Pilih level baru:")
    print(f"{Fore.WHITE}1. Admin Standar")
    print(f"{Fore.WHITE}2. Admin Senior")
    
    while True:
        try:
            new_level = int(input(f"\n{Fore.GREEN}Pilih level (1-2): ").strip())
            if new_level in [1, 2]:
                break
            else:
                print(f"{Fore.RED}Pilihan tidak valid!")
        except ValueError:
            print(f"{Fore.RED}Masukkan angka 1 atau 2!")
    
    if new_level == current_level:
        print(f"{Fore.YELLOW}Level tidak berubah.")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    # Update permissions based on new level
    if new_level == 1:
        permissions = [
            "manage_inventory",
            "process_transactions"
        ]
    else:  # new_level == 2
        permissions = [
            "manage_inventory",
            "process_transactions",
            "view_sales_reports",
            "manage_customers",
            "view_analytics"
        ]
    
    users[admin_username]['admin_level'] = new_level
    users[admin_username]['permissions'] = permissions
    
    if save_users(users):
        level_name = 'Senior' if new_level == 2 else 'Standar'
        print(f"\n{Fore.GREEN}✓ Level admin berhasil diubah menjadi {level_name}!")
    else:
        print(f"\n{Fore.RED}✗ Gagal mengubah level admin!")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

def update_admin_contact(admin_username, users):
    """Update admin contact information"""
    admin_data = users[admin_username]
    
    print(f"\n{Fore.CYAN}▶ Info kontak saat ini:")
    print(f"{Fore.WHITE}Email: {admin_data.get('email', 'N/A')}")
    print(f"{Fore.WHITE}Phone: {admin_data.get('phone', 'N/A')}")
    
    # Update email
    update_email = input(f"\n{Fore.YELLOW}Update email? (y/n): ").strip().lower()
    if update_email == 'y':
        while True:
            new_email = input(f"{Fore.WHITE}Email baru: {Fore.GREEN}").strip().lower()
            if new_email and "@" in new_email and "." in new_email:
                users[admin_username]['email'] = new_email
                break
            elif not new_email:
                break
            else:
                print(f"{Fore.RED}Format email tidak valid!")
    
    # Update phone
    update_phone = input(f"{Fore.YELLOW}Update phone? (y/n): ").strip().lower()
    if update_phone == 'y':
        new_phone = input(f"{Fore.WHITE}Phone baru: {Fore.GREEN}").strip()
        users[admin_username]['phone'] = new_phone
    
    if save_users(users):
        print(f"\n{Fore.GREEN}✓ Info kontak berhasil diupdate!")
    else:
        print(f"\n{Fore.RED}✗ Gagal mengupdate info kontak!")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

def delete_admin(admin_username, users):
    """Delete admin account"""
    admin_data = users[admin_username]
    
    print(f"\n{Fore.RED}⚠ PERINGATAN: Menghapus admin akan menghilangkan semua data!")
    print(f"{Fore.YELLOW}Admin yang akan dihapus:")
    print(f"{Fore.WHITE}Username: {admin_username}")
    print(f"{Fore.WHITE}Nama: {admin_data.get('full_name')}")
    
    # Double confirmation
    confirm1 = input(f"\n{Fore.YELLOW}Yakin ingin menghapus admin ini? (ketik 'HAPUS' untuk konfirmasi): ").strip()
    
    if confirm1 != 'HAPUS':
        print(f"{Fore.YELLOW}Penghapusan dibatalkan.")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return False
    
    confirm2 = input(f"{Fore.RED}Konfirmasi terakhir - ketik username '{admin_username}' untuk menghapus: ").strip()
    
    if confirm2 != admin_username:
        print(f"{Fore.YELLOW}Penghapusan dibatalkan - username tidak cocok.")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return False
    
    # Delete admin
    del users[admin_username]
    
    if save_users(users):
        print(f"\n{Fore.GREEN}✓ Admin {admin_username} berhasil dihapus!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return True
    else:
        print(f"\n{Fore.RED}✗ Gagal menghapus admin!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return False

def user_management_menu():
    """Main user management menu for Super Admin"""
    while True:
        clear_screen()
        print_header("MANAJEMEN PENGGUNA", Fore.MAGENTA)
        
        users = load_users()
        
        # Count users by role
        role_counts = {'super_admin': 0, 'admin': 0, 'user': 0}
        for user_data in users.values():
            role = user_data.get('role', 'user')
            role_counts[role] += 1
        
        print(f"\n{Fore.CYAN}▶ Statistik Pengguna:")
        print(f"{Fore.WHITE}Super Admin: {role_counts['super_admin']} orang")
        print(f"{Fore.WHITE}Admin: {role_counts['admin']} orang") 
        print(f"{Fore.WHITE}Pelanggan: {role_counts['user']} orang")
        print(f"{Fore.WHITE}Total: {sum(role_counts.values())} pengguna")
        
        print(f"\n{Fore.YELLOW}▶ Menu Manajemen:")
        print(f"{Fore.WHITE}1. Lihat Semua Pengguna")
        print(f"{Fore.WHITE}2. Tambah Admin Baru")
        print(f"{Fore.WHITE}3. Kelola Akun Admin")
        print(f"{Fore.WHITE}4. Kelola Akun Pelanggan")
        print(f"{Fore.WHITE}5. Laporan Aktivitas Login")
        print(f"{Fore.WHITE}0. Kembali ke Menu Super Admin")
        
        choice = input(f"\n{Fore.GREEN}Pilih menu (0-5): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            view_all_users()
        elif choice == "2":
            create_admin()
        elif choice == "3":
            manage_admin_accounts()
        elif choice == "4":
            manage_customer_accounts()
        elif choice == "5":
            show_login_activity_report()
        else:
            print(f"\n{Fore.RED}Pilihan tidak valid!")
            input(f"\n{Fore.YELLOW}Tekan Enter untuk melanjutkan...")

def manage_customer_accounts():
    """Manage customer accounts"""
    clear_screen()
    print_header("KELOLA AKUN PELANGGAN", Fore.GREEN)
    
    users = load_users()
    
    # Get all customers
    customers = {username: data for username, data in users.items() if data.get('role') == 'user'}
    
    if not customers:
        print(f"{Fore.RED}Tidak ada pelanggan dalam sistem!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    print(f"{Fore.YELLOW}▶ Daftar Pelanggan ({len(customers)} orang):")
    
    # Sort customers by total purchases (descending)
    sorted_customers = sorted(customers.items(), key=lambda x: x[1].get('total_purchases', 0), reverse=True)
    
    for username, data in sorted_customers[:10]:  # Show top 10
        status_color = Fore.GREEN if data.get('status') == 'active' else Fore.RED
        loyalty_points = data.get('loyalty_points', 0)
        total_purchases = data.get('total_purchases', 0)
        print(f"  {Fore.WHITE}• {username} ({data.get('full_name', 'N/A')}) - {status_color}{data.get('status')}")
        print(f"    Points: {loyalty_points} | Pembelian: {total_purchases}x | Last Login: {data.get('last_login', 'Never')}")
    
    if len(customers) > 10:
        print(f"\n{Fore.CYAN}... dan {len(customers) - 10} pelanggan lainnya")
    
    print(f"\n{Fore.YELLOW}▶ Aksi:")
    print(f"{Fore.WHITE}1. Cari Pelanggan Spesifik")
    print(f"{Fore.WHITE}2. Reset Password Pelanggan")
    print(f"{Fore.WHITE}3. Toggle Status Pelanggan")
    print(f"{Fore.WHITE}4. Update Loyalty Points")
    print(f"{Fore.WHITE}0. Kembali")
    
    choice = input(f"\n{Fore.GREEN}Pilih aksi (0-4): ").strip()
    
    if choice == "1":
        search_customer(users)
    elif choice == "2":
        reset_customer_password(users)
    elif choice == "3":
        toggle_customer_status(users)
    elif choice == "4":
        update_loyalty_points(users)

def search_customer(users):
    """Search for specific customer"""
    search_term = input(f"\n{Fore.YELLOW}Masukkan username atau nama pelanggan: {Fore.GREEN}").strip().lower()
    
    if not search_term:
        return
    
    matches = []
    for username, data in users.items():
        if data.get('role') == 'user':
            if (search_term in username.lower() or 
                search_term in data.get('full_name', '').lower() or
                search_term in data.get('email', '').lower()):
                matches.append((username, data))
    
    if not matches:
        print(f"{Fore.RED}Tidak ada pelanggan yang cocok dengan pencarian.")
    else:
        print(f"\n{Fore.CYAN}▶ Hasil pencarian ({len(matches)} ditemukan):")
        for username, data in matches:
            status_color = Fore.GREEN if data.get('status') == 'active' else Fore.RED
            print(f"  {Fore.WHITE}• {username} ({data.get('full_name')})")
            print(f"    Email: {data.get('email')} | Status: {status_color}{data.get('status')}")
            print(f"    Points: {data.get('loyalty_points', 0)} | Pembelian: {data.get('total_purchases', 0)}x")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

# Kelanjutan dari fungsi reset_customer_password yang terpotong
def reset_customer_password(users):
    """Reset customer password"""
    username = input(f"\n{Fore.YELLOW}Username pelanggan: {Fore.GREEN}").strip().lower()
    
    if username not in users or users[username].get('role') != 'user':
        print(f"{Fore.RED}Pelanggan tidak ditemukan!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    print(f"\n{Fore.CYAN}Pelanggan: {users[username].get('full_name')} ({username})")
    
    # Generate new temporary password
    import random
    import string
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    print(f"\n{Fore.YELLOW}▶ Pilih metode reset password:")
    print(f"{Fore.WHITE}1. Generate password otomatis")
    print(f"{Fore.WHITE}2. Set password manual")
    
    while True:
        try:
            choice = int(input(f"\n{Fore.GREEN}Pilih metode (1-2): ").strip())
            if choice in [1, 2]:
                break
            else:
                print(f"{Fore.RED}Pilihan tidak valid!")
        except ValueError:
            print(f"{Fore.RED}Masukkan angka 1 atau 2!")
    
    if choice == 1:
        new_password = temp_password
        print(f"\n{Fore.CYAN}Password otomatis: {Fore.WHITE}{new_password}")
    else:
        while True:
            new_password = getpass.getpass(f"{Fore.WHITE}Password baru: ")
            
            if not new_password:
                print(f"{Fore.RED}Password tidak boleh kosong!")
                continue
                
            is_valid, message = validate_password(new_password)
            if not is_valid:
                print(f"{Fore.RED}{message}")
                continue
                
            confirm_password = getpass.getpass(f"{Fore.WHITE}Konfirmasi Password: ")
            if new_password != confirm_password:
                print(f"{Fore.RED}Password tidak cocok!")
                continue
                
            break
    
    confirm = input(f"\n{Fore.YELLOW}Reset password untuk {username}? (y/n): ").strip().lower()
    
    if confirm == 'y':
        users[username]['password'] = hash_password(new_password)
        
        if save_users(users):
            print(f"\n{Fore.GREEN}✓ Password pelanggan berhasil direset!")
            if choice == 1:
                print(f"{Fore.CYAN}Password sementara: {Fore.WHITE}{new_password}")
                print(f"{Fore.YELLOW}Sarankan pelanggan untuk mengganti password setelah login.")
        else:
            print(f"\n{Fore.RED}✗ Gagal menyimpan password baru!")
    else:
        print(f"{Fore.YELLOW}Reset password dibatalkan.")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

def toggle_customer_status(users):
    """Toggle customer active/inactive status"""
    username = input(f"\n{Fore.YELLOW}Username pelanggan: {Fore.GREEN}").strip().lower()
    
    if username not in users or users[username].get('role') != 'user':
        print(f"{Fore.RED}Pelanggan tidak ditemukan!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    customer_data = users[username]
    current_status = customer_data.get('status', 'active')
    new_status = 'inactive' if current_status == 'active' else 'active'
    action = 'menonaktifkan' if new_status == 'inactive' else 'mengaktifkan'
    
    print(f"\n{Fore.CYAN}Pelanggan: {customer_data.get('full_name')} ({username})")
    print(f"{Fore.WHITE}Status saat ini: {Fore.GREEN if current_status == 'active' else Fore.RED}{current_status}")
    print(f"{Fore.WHITE}Status baru: {Fore.GREEN if new_status == 'active' else Fore.RED}{new_status}")
    
    if new_status == 'inactive':
        print(f"\n{Fore.RED}⚠ Menonaktifkan pelanggan akan:")
        print(f"{Fore.YELLOW}• Mencegah login ke sistem")
        print(f"{Fore.YELLOW}• Tidak dapat melakukan transaksi")
        print(f"{Fore.YELLOW}• Loyalty points tetap tersimpan")
    
    confirm = input(f"\n{Fore.YELLOW}Yakin ingin {action} pelanggan {username}? (y/n): ").strip().lower()
    
    if confirm == 'y':
        users[username]['status'] = new_status
        users[username]['status_changed_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users[username]['status_changed_by'] = 'super_admin'
        
        if save_users(users):
            print(f"\n{Fore.GREEN}✓ Status pelanggan berhasil diubah menjadi {new_status}!")
        else:
            print(f"\n{Fore.RED}✗ Gagal mengubah status pelanggan!")
    else:
        print(f"{Fore.YELLOW}Perubahan status dibatalkan.")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

def update_loyalty_points(users):
    """Update customer loyalty points"""
    username = input(f"\n{Fore.YELLOW}Username pelanggan: {Fore.GREEN}").strip().lower()
    
    if username not in users or users[username].get('role') != 'user':
        print(f"{Fore.RED}Pelanggan tidak ditemukan!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    customer_data = users[username]
    current_points = customer_data.get('loyalty_points', 0)
    
    print(f"\n{Fore.CYAN}Pelanggan: {customer_data.get('full_name')} ({username})")
    print(f"{Fore.WHITE}Points saat ini: {Fore.GREEN}{current_points}")
    
    print(f"\n{Fore.YELLOW}▶ Pilih aksi:")
    print(f"{Fore.WHITE}1. Tambah Points")
    print(f"{Fore.WHITE}2. Kurangi Points")
    print(f"{Fore.WHITE}3. Set Points (override)")
    print(f"{Fore.WHITE}0. Kembali")
    
    while True:
        try:
            action = int(input(f"\n{Fore.GREEN}Pilih aksi (0-3): ").strip())
            if action in [0, 1, 2, 3]:
                break
            else:
                print(f"{Fore.RED}Pilihan tidak valid!")
        except ValueError:
            print(f"{Fore.RED}Masukkan angka 0-3!")
    
    if action == 0:
        return
    
    while True:
        try:
            if action == 3:
                points_value = int(input(f"{Fore.WHITE}Points baru: {Fore.GREEN}").strip())
            else:
                points_value = int(input(f"{Fore.WHITE}Jumlah points: {Fore.GREEN}").strip())
            
            if points_value < 0:
                print(f"{Fore.RED}Points tidak boleh negatif!")
                continue
            break
        except ValueError:
            print(f"{Fore.RED}Masukkan angka yang valid!")
    
    # Calculate new points
    if action == 1:  # Add points
        new_points = current_points + points_value
        action_text = f"menambah {points_value} points"
    elif action == 2:  # Subtract points
        new_points = max(0, current_points - points_value)  # Don't allow negative points
        action_text = f"mengurangi {points_value} points"
    else:  # Set points (action == 3)
        new_points = points_value
        action_text = f"mengset points menjadi {points_value}"
    
    reason = input(f"{Fore.YELLOW}Alasan perubahan (opsional): {Fore.GREEN}").strip()
    
    print(f"\n{Fore.CYAN}▶ Konfirmasi perubahan:")
    print(f"{Fore.WHITE}Pelanggan: {username}")
    print(f"{Fore.WHITE}Points lama: {current_points}")
    print(f"{Fore.WHITE}Points baru: {new_points}")
    print(f"{Fore.WHITE}Aksi: {action_text}")
    if reason:
        print(f"{Fore.WHITE}Alasan: {reason}")
    
    confirm = input(f"\n{Fore.YELLOW}Konfirmasi perubahan points? (y/n): ").strip().lower()
    
    if confirm == 'y':
        users[username]['loyalty_points'] = new_points
        
        # Log the points change
        if 'points_history' not in users[username]:
            users[username]['points_history'] = []
        
        users[username]['points_history'].append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': action_text,
            'old_points': current_points,
            'new_points': new_points,
            'reason': reason,
            'changed_by': 'super_admin'
        })
        
        if save_users(users):
            print(f"\n{Fore.GREEN}✓ Loyalty points berhasil diupdate!")
            print(f"{Fore.CYAN}Points {username}: {current_points} → {new_points}")
        else:
            print(f"\n{Fore.RED}✗ Gagal mengupdate loyalty points!")
    else:
        print(f"{Fore.YELLOW}Perubahan points dibatalkan.")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

def show_login_activity_report():
    """Show login activity report"""
    clear_screen()
    print_header("LAPORAN AKTIVITAS LOGIN", Fore.CYAN)
    
    users = load_users()
    
    if not users:
        print(f"{Fore.RED}Tidak ada data pengguna!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    print(f"\n{Fore.YELLOW}▶ Pilih periode laporan:")
    print(f"{Fore.WHITE}1. Semua aktivitas")
    print(f"{Fore.WHITE}2. 7 hari terakhir")
    print(f"{Fore.WHITE}3. 30 hari terakhir")
    print(f"{Fore.WHITE}4. Custom periode")
    
    while True:
        try:
            period_choice = int(input(f"\n{Fore.GREEN}Pilih periode (1-4): ").strip())
            if period_choice in [1, 2, 3, 4]:
                break
            else:
                print(f"{Fore.RED}Pilihan tidak valid!")
        except ValueError:
            print(f"{Fore.RED}Masukkan angka 1-4!")
    
    # Process login data
    login_data = []
    current_time = datetime.now()
    
    for username, user_data in users.items():
        last_login = user_data.get('last_login')
        if last_login and last_login != 'Never':
            try:
                login_time = datetime.strptime(last_login, "%Y-%m-%d %H:%M:%S")
                
                # Filter by period
                if period_choice == 1:  # All activities
                    include = True
                elif period_choice == 2:  # 7 days
                    include = (current_time - login_time).days <= 7
                elif period_choice == 3:  # 30 days
                    include = (current_time - login_time).days <= 30
                else:  # Custom period (simplified - last 14 days for example)
                    include = (current_time - login_time).days <= 14
                
                if include:
                    login_data.append({
                        'username': username,
                        'full_name': user_data.get('full_name', 'N/A'),
                        'role': user_data.get('role', 'user'),
                        'last_login': last_login,
                        'login_time': login_time,
                        'status': user_data.get('status', 'active')
                    })
            except ValueError:
                continue
    
    if not login_data:
        print(f"\n{Fore.RED}Tidak ada data login untuk periode yang dipilih!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    # Sort by login time (most recent first)
    login_data.sort(key=lambda x: x['login_time'], reverse=True)
    
    print(f"\n{Fore.CYAN}▶ Laporan Aktivitas Login ({len(login_data)} entries):")
    print(f"{Fore.WHITE}{'No':<3} {'Username':<15} {'Nama':<20} {'Role':<12} {'Last Login':<20} {'Status'}")
    print(f"{Fore.CYAN}{'-' * 80}")
    
    for i, data in enumerate(login_data[:20], 1):  # Show top 20
        role_color = Fore.MAGENTA if data['role'] == 'super_admin' else Fore.BLUE if data['role'] == 'admin' else Fore.GREEN
        status_color = Fore.GREEN if data['status'] == 'active' else Fore.RED
        
        print(f"{Fore.WHITE}{i:<3} {data['username']:<15} {data['full_name'][:18]:<20} "
              f"{role_color}{data['role']:<12} {Fore.WHITE}{data['last_login']:<20} "
              f"{status_color}{data['status']}")
    
    if len(login_data) > 20:
        print(f"\n{Fore.YELLOW}... dan {len(login_data) - 20} entries lainnya")
    
    # Statistics
    print(f"\n{Fore.CYAN}▶ Statistik:")
    role_stats = {}
    status_stats = {'active': 0, 'inactive': 0}
    
    for data in login_data:
        role = data['role']
        status = data['status']
        
        role_stats[role] = role_stats.get(role, 0) + 1
        status_stats[status] = status_stats.get(status, 0) + 1
    
    print(f"{Fore.WHITE}Login per Role:")
    for role, count in role_stats.items():
        print(f"  {role}: {count} login")
    
    print(f"{Fore.WHITE}Status Pengguna:")
    for status, count in status_stats.items():
        color = Fore.GREEN if status == 'active' else Fore.RED
        print(f"  {color}{status}: {count} pengguna")
    
    # Never logged in users
    never_logged_in = [username for username, data in users.items() 
                      if data.get('last_login') in [None, 'Never']]
    
    if never_logged_in:
        print(f"\n{Fore.YELLOW}▶ Pengguna yang belum pernah login ({len(never_logged_in)} orang):")
        for username in never_logged_in[:10]:  # Show first 10
            user_data = users[username]
            role_color = Fore.MAGENTA if user_data.get('role') == 'super_admin' else Fore.BLUE if user_data.get('role') == 'admin' else Fore.GREEN
            print(f"  {Fore.WHITE}• {username} ({user_data.get('full_name', 'N/A')}) - {role_color}{user_data.get('role', 'user')}")
        
        if len(never_logged_in) > 10:
            print(f"  {Fore.CYAN}... dan {len(never_logged_in) - 10} lainnya")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

# Fungsi tambahan untuk melengkapi sistem
def export_users_report():
    """Export users data to CSV report"""
    import csv
    
    clear_screen()
    print_header("EXPORT LAPORAN PENGGUNA", Fore.CYAN)
    
    users = load_users()
    
    if not users:
        print(f"{Fore.RED}Tidak ada data pengguna untuk diexport!")
        input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")
        return
    
    filename = f"users_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['username', 'full_name', 'email', 'role', 'status', 'loyalty_points', 
                         'total_purchases', 'last_login', 'created_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for username, data in users.items():
                writer.writerow({
                    'username': username,
                    'full_name': data.get('full_name', ''),
                    'email': data.get('email', ''),
                    'role': data.get('role', 'user'),
                    'status': data.get('status', 'active'),
                    'loyalty_points': data.get('loyalty_points', 0),
                    'total_purchases': data.get('total_purchases', 0),
                    'last_login': data.get('last_login', 'Never'),
                    'created_date': data.get('created_date', '')
                })
        
        print(f"\n{Fore.GREEN}✓ Laporan berhasil diexport ke: {filename}")
        print(f"{Fore.CYAN}Total {len(users)} pengguna telah diexport.")
        
    except Exception as e:
        print(f"\n{Fore.RED}✗ Gagal mengexport laporan: {str(e)}")
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")

def backup_users_data():
    """Create backup of users data"""
    import shutil

    backup_folder = os.path.join(DATA_FOLDER, "backup")
    os.makedirs(backup_folder, exist_ok=True)

    clear_screen()
    print_header("BACKUP DATA PENGGUNA", Fore.CYAN)

    try:
        backup_filename = f"users_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(backup_folder, backup_filename)

        shutil.copy2(USERS_DATA_FILE, backup_path)

        print(f"\n{Fore.GREEN}✓ Backup berhasil dibuat: {backup_path}")
        print(f"{Fore.CYAN}Data pengguna telah disimpan dengan aman.")

    except FileNotFoundError:
        print(f"\n{Fore.RED}✗ File {USERS_DATA_FILE} tidak ditemukan!")
    except Exception as e:
        print(f"\n{Fore.RED}✗ Gagal membuat backup: {str(e)}")

    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...")


# Update user_management_menu untuk menambahkan fitur baru
def user_management_menu():
    """Main user management menu for Super Admin"""
    while True:
        clear_screen()
        print_header("MANAJEMEN PENGGUNA", Fore.MAGENTA)
        
        users = load_users()
        
        # Count users by role
        role_counts = {'super_admin': 0, 'admin': 0, 'user': 0}
        for user_data in users.values():
            role = user_data.get('role', 'user')
            role_counts[role] += 1
        
        print(f"\n{Fore.CYAN}▶ Statistik Pengguna:")
        print(f"{Fore.WHITE}Super Admin: {role_counts['super_admin']} orang")
        print(f"{Fore.WHITE}Admin: {role_counts['admin']} orang") 
        print(f"{Fore.WHITE}Pelanggan: {role_counts['user']} orang")
        print(f"{Fore.WHITE}Total: {sum(role_counts.values())} pengguna")
        
        print(f"\n{Fore.YELLOW}▶ Menu Manajemen:")
        print(f"{Fore.WHITE}1. Lihat Semua Pengguna")
        print(f"{Fore.WHITE}2. Tambah Admin Baru")
        print(f"{Fore.WHITE}3. Kelola Akun Admin")
        print(f"{Fore.WHITE}4. Kelola Akun Pelanggan")
        print(f"{Fore.WHITE}5. Laporan Aktivitas Login")
        print(f"{Fore.WHITE}6. Export Laporan Pengguna")
        print(f"{Fore.WHITE}7. Backup Data Pengguna")
        print(f"{Fore.WHITE}0. Kembali ke Menu Super Admin")
        
        choice = input(f"\n{Fore.GREEN}Pilih menu (0-7): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            view_all_users()
        elif choice == "2":
            create_admin()
        elif choice == "3":
            manage_admin_accounts()
        elif choice == "4":
            manage_customer_accounts()
        elif choice == "5":
            show_login_activity_report()
        elif choice == "6":
            export_users_report()
        elif choice == "7":
            backup_users_data()
        else:
            print(f"\n{Fore.RED}Pilihan tidak valid!")
            input(f"\n{Fore.YELLOW}Tekan Enter untuk melanjutkan...")

# Fungsi untuk menjalankan sistem (contoh usage)
if __name__ == "__main__":
    # Contoh cara menjalankan menu manajemen pengguna
    user_management_menu()