# Challenge: Lovely Forensic Suite

## Deskripsi Challenge
MEMORANDUM

UNTUK: Konsultan Keamanan Eksternal
DARI: Kepala Divisi Respons Insiden, Pan-Global Consultants
SUBJEK: Audit Mendesak pada Prototipe Internal - "Lovely Forensic Suite"

Selamat datang, tim audit.

Menyusul insiden keamanan baru-baru ini, tim kami mengembangkan sebuah prototipe alat analisis forensik berbasis web dengan tergesa-gesa. Alat yang diberi nama "Lovely Forensic Suite" ini dirancang untuk melakukan triase cepat terhadap artefak digital yang mencurigakan.

Mengingat sifat pengembangannya yang dipercepat, kami memiliki kekhawatiran signifikan mengenai potensi kelemahan dalam implementasinya. Tugas Anda adalah melakukan audit keamanan penuh pada instance yang telah disediakan.

Intelijen awal kami menunjukkan bahwa suite ini memiliki tiga gerbang analisis utama, masing-masing dengan logika pemrosesan yang unik. Namun, tampaknya hanya ada sa-

---

## Fitur Layanan
Lovely Forensic Suite menyediakan tiga alat analisis utama:

### 1. PNG Analyzer
- **Fungsi:** Mengunggah file gambar PNG untuk mengekstrak metadata menggunakan `exiftool` dan `pngcheck`.  
- **Fitur Khusus:** Membaca custom chunk bernama `LFTD` yang berfungsi sebagai *"catatan analis"* yang disematkan dalam gambar.  
- **Petunjuk:** Data dari chunk `LFTD` dievaluasi secara dinamis oleh sistem. *Apa yang terjadi jika "catatan" tersebut bukan sekadar teks biasa?*

### 2. PDF Analyzer
- **Fungsi:** Menganalisis file PDF untuk mengekstrak metadata, mengidentifikasi objek-objek di dalamnya, dan mengonversi konten PDF menjadi file HTML yang dapat diunduh.  
- **Fitur Khusus:** Kemampuan untuk menjalankan *"plugin"* yang disematkan dalam format `/PyScript` di dalam objek PDF.  
- **Petunjuk:** `"/PyScript"` dijalankan dalam sandbox untuk fungsionalitas tambahan. *Seberapa amankah sandbox tersebut?*

### 3. Disk Analyzer
- **Fungsi:** Mengunggah file disk image (`.dd`) berformat NTFS untuk di-`mount` dan dianalisis. Alat ini akan menampilkan informasi partisi dan **mendaftar semua file** yang ada di dalam root directory image tersebut.  
- **Petunjuk:** Daftar nama file ditampilkan menggunakan template engine di sisi server. *Bagaimana engine tersebut merender nama file yang tidak biasa atau mengandung karakter khusus?*

---

## Mekanisme Permainan

### Fase Serangan (Attack)
1. **Analisis & Eksploitasi:** Analisis setiap fitur pada web service untuk menemukan kerentanan.  
2. **Pembuatan Payload:** Buat file (PNG, PDF, atau `.dd`) yang berisi payload untuk mengeksploitasi kerentanan yang telah ditemukan. Tujuan utama payload adalah **membaca flag** yang berada di `/flag.txt`.  
3. **Eksekusi:** Unggah file payload Anda ke layanan tim lawan. Jika berhasil, server mereka akan mengeksekusi payload Anda dan membocorkan flag.  
4. **Submit Flag:** Kirimkan flag yang Anda dapatkan ke scoring server untuk mendapatkan poin serangan.

### Fase Pertahanan (Defense)
1. **Mendapatkan Akses:** Setelah tim Anda berhasil melakukan satu serangan pertama kali, Anda akan diberikan akses SSH ke container service Anda.  
2. **Analisis Kode:** Lakukan analisis terhadap kode sumber aplikasi yang berada di direktori `/app`. Pahami bagaimana setiap fitur bekerja dan di mana letak kerentanannya.  
3. **Hardening:** Fokus pertahanan adalah dengan melakukan **blacklisting**. Di dalam direktori `/app/blacklists/`, Anda akan menemukan tiga file:
   - `eval_blacklist.txt` (untuk PNG Analyzer)  
   - `exec_blacklist.txt` (untuk PDF Analyzer)  
   - `template_blacklist.txt` (untuk Disk Analyzer)  
   Isi file-file ini untuk memblokir keyword atau karakter berbahaya yang digunakan oleh penyerang.

#### Dinamika Blacklist
- Setiap file blacklist **dibatasi 5 baris**, dan **setiap baris maksimal 10 karakter**.  
- **Panjang payload serangan** yang diterima oleh service Anda akan **berbanding terbalik** dengan kepadatan blacklist. Semakin pendek dan sedikit kata kunci yang Anda masukkan ke blacklist, semakin pendek pula payload yang harus dibuat oleh penyerang. Gunakan strategi ini untuk menyulitkan lawan!

---

## Akses SSH
- **Host:** Alamat IP publik yang diberikan untuk tim Anda.  
- **Port:** Port SSH yang ditentukan (misal: `22022`).  
- **User:** `ctfuser`  
- **Password:** Akan diberikan oleh panitia.

Dengan akses SSH, Anda dapat:
- Melihat dan menganalisis semua file di `/app`.  
- Mengedit file-file di `/app/blacklists/` menggunakan `nano`.

**PENTING:** Anda **tidak memiliki izin** untuk mengubah file kode sumber lainnya atau mematikan layanan. Setiap perubahan di luar direktori `blacklists` akan dideteksi oleh SLA checker dan mengakibatkan penalti.

---

## Catatan Tambahan / Tips
- Fokuskan eksploitasi pada bagaimana input dari file (chunk `LFTD`, objek `/PyScript`, nama file NTFS) diproses dan dirender oleh server.  
- Perhatikan batasan blacklist (5 baris × 10 karakter) saat merancang mitigasi — pendekatan kreatif sering kali diperlukan.  
- Selalu uji payload di environment yang aman sebelum meluncurkan ke permainan kompetitif.
