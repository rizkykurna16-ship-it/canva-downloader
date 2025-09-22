import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, SessionNotCreatedException

# --- KONFIGURASI PENTING ---
# Ganti dengan link share Canva yang ingin Anda download.
CANVA_SHARE_LINK = "https://www.canva.com/design/DAGoC6F-ioo/lLzJOZF_n_zqDs6jWtyE_A/view?utm_content=DAGoC6F-ioo&utm_campaign=designshare&utm_medium=link2&utm_source=uniquelinks&utlId=h268fd0ff77#8"

# Ganti dengan path folder tempat Anda ingin menyimpan file hasil download.
# Contoh untuk Windows: "C:\\Users\\NamaAnda\\Downloads\\Canva"
# Contoh untuk macOS/Linux: "/Users/NamaAnda/Downloads/Canva"
DOWNLOAD_DIRECTORY = os.path.join(os.path.expanduser('~'), 'Downloads', 'CanvaProject')

# Ganti dengan path ke profile Chrome Anda. Ini PENTING agar Anda tidak perlu login di dalam script.
# PENTING: Untuk Windows, gunakan format r"..." (raw string) untuk menghindari error pada path.
CHROME_PROFILE_PATH = r"C:\Users\rizky\AppData\Local\Google\Chrome\User Data"
# -------------------------

def setup_driver():
    """Menyiapkan driver Chrome dengan opsi yang diperlukan."""
    if not os.path.exists(DOWNLOAD_DIRECTORY):
        os.makedirs(DOWNLOAD_DIRECTORY)
        print(f"Folder download dibuat di: {DOWNLOAD_DIRECTORY}")

    chrome_options = Options()
    
    # Opsi-opsi ini dapat membantu menstabilkan startup Selenium.
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Menggunakan profil Chrome yang ada untuk menghindari login
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
    
    # Mengatur folder download default
    prefs = {"download.default_directory": DOWNLOAD_DIRECTORY}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Mencegah jendela browser tertutup secara otomatis (untuk debugging)
    chrome_options.add_experimental_option("detach", True)

    try:
        print("Menyiapkan driver Chrome secara otomatis...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Driver berhasil disiapkan.")
        return driver
    except SessionNotCreatedException as e:
        print("\n--- ERROR Kritis: SessionNotCreatedException ---")
        print("Gagal memulai sesi browser. Ini sering terjadi karena profil Chrome terkunci atau ada ketidakcocokan versi.")
        print("Silakan ikuti langkah-langkah di bagian 'Troubleshooting' pada file README.md.")
        print(f"Detail error: {e}")
        return None
    except Exception as e:
        print(f"Error saat inisialisasi driver: {e}")
        print("Pastikan Google Chrome sudah terinstal di komputer Anda.")
        return None

def download_canva_project(driver, url):
    """Fungsi utama untuk membuka URL dan men-download proyek."""
    print(f"Membuka link Canva: {url}")
    driver.get(url)
    wait = WebDriverWait(driver, 45)

    try:
        # Menunggu halaman siap, misalnya dengan menunggu elemen judul muncul
        print("Menunggu halaman Canva dimuat sepenuhnya...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1, h2')))
        time.sleep(3) # Beri waktu ekstra 3 detik agar semua skrip halaman selesai berjalan
        print("Halaman berhasil dimuat.")
    except TimeoutException:
        print("Halaman Canva tidak dapat dimuat atau judul tidak ditemukan. Memeriksa kemungkinan adanya tombol 'Use template'...")
        # Terkadang ada tombol "Use template", coba klik jika ada
        try:
            use_template_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label*="Gunakan templat"], a[aria-label*="Use template"]')
            print("Tombol 'Gunakan templat' ditemukan. Mengklik...")
            use_template_button.click()
            time.sleep(5) # Tunggu editor dimuat
        except:
            print("Tombol 'Gunakan templat' tidak ditemukan. Melanjutkan proses...")

    # --- LANGKAH 1: Klik Tombol 'Bagikan' (Share) ---
    try:
        share_button_selector = "//button[@aria-label='Bagikan' or @aria-label='Share']"
        print("LANGKAH 1: Mencari tombol 'Bagikan'...")
        share_button = wait.until(EC.element_to_be_clickable((By.XPATH, share_button_selector)))
        print("Tombol 'Bagikan' ditemukan. Mengklik...")
        share_button.click()
    except TimeoutException:
        print("\n--- ERROR DI LANGKAH 1 ---")
        print("Gagal menemukan tombol 'Bagikan' (Share).")
        print("Kemungkinan Canva telah mengubah UI-nya. Cek file README.md untuk cara memperbaikinya.")
        return

    # --- LANGKAH 2: Klik Tombol 'Unduh' (Download) di Menu ---
    try:
        download_menu_selector = "//span[text()='Unduh' or text()='Download']"
        print("LANGKAH 2: Mencari tombol 'Unduh' di menu...")
        download_menu_button = wait.until(EC.element_to_be_clickable((By.XPATH, download_menu_selector)))
        print("Tombol 'Unduh' ditemukan. Mengklik...")
        download_menu_button.click()
    except TimeoutException:
        print("\n--- ERROR DI LANGKAH 2 ---")
        print("Gagal menemukan tombol 'Unduh' (Download) pada menu pop-up.")
        print("Pastikan tombol 'Bagikan' berhasil diklik dan menu pop-up muncul.")
        return

    # --- LANGKAH 3: Klik Tombol 'Unduh' Final di Panel Download ---
    try:
        final_download_button_selector = 'button[data-testid="download-button-new-download-experience"]'
        print("LANGKAH 3: Mencari tombol 'Unduh' final...")
        final_download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, final_download_button_selector)))
        print("Tombol 'Unduh' final ditemukan. Memulai proses download...")
        final_download_button.click()
    except TimeoutException:
        print("\n--- ERROR DI LANGKAH 3 ---")
        print("Gagal menemukan tombol 'Unduh' final di panel download.")
        print("Ini adalah tombol besar berwarna ungu yang memulai proses rendering.")
        return

    wait_for_download_completion(DOWNLOAD_DIRECTORY)

    print("\n--- Download Selesai! ---")
    print(f"File berhasil disimpan di folder: {DOWNLOAD_DIRECTORY}")


def wait_for_download_completion(directory, timeout=300):
    """Menunggu file selesai di-download di direktori yang ditentukan."""
    print("Menunggu file selesai di-download. Ini mungkin memakan waktu beberapa saat tergantung ukuran proyek...")
    seconds = 0
    downloading = True
    while downloading and seconds < timeout:
        time.sleep(1)
        downloading = False
        for fname in os.listdir(directory):
            if fname.endswith('.crdownload'):
                downloading = True
        seconds += 1
    if downloading:
        print("Proses download melebihi batas waktu.")
    else:
        print("File terdeteksi selesai di-download.")


if __name__ == '__main__':
    if "GANTI_DENGAN_PATH" in CHROME_PROFILE_PATH or not os.path.exists(CHROME_PROFILE_PATH):
        print("="*50)
        print("!! PERINGATAN: Konfigurasi Belum Lengkap !!")
        print(f"Path profil Chrome tidak valid: '{CHROME_PROFILE_PATH}'")
        print("Harap periksa kembali variabel CHROME_PROFILE_PATH di dalam skrip.")
        print("="*50)
    elif "your-design-id" in CANVA_SHARE_LINK:
        print("="*50)
        print("!! PERINGATAN: Konfigurasi Belum Lengkap !!")
        print("Harap isi variabel CANVA_SHARE_LINK dengan link Canva Anda.")
        print("="*50)
    else:
        driver = setup_driver()
        if driver:
            download_canva_project(driver, CANVA_SHARE_LINK)
            print("\nBrowser akan tetap terbuka. Anda bisa menutupnya secara manual.")

