# My Portfolio

Website portofolio pribadi Mohammad Adzka Aulia untuk mata kuliah
Pemrograman Berbasis Platform (PBP). Halaman ini dibangun menggunakan Django,
HTML5, dan CSS3 untuk menampilkan profil serta kemampuan utama secara
responsif.

## Identitas

- Nama: Mohammad Adzka Aulia
- NPM: 2506657005
- Kelas: PBP F

## Menjalankan Proyek

1. Buat virtual environment dengan `python3 -m venv .venv`.
2. Aktifkan dengan `source .venv/bin/activate`.
3. Instal dependensi dengan `python -m pip install -r requirements.txt`.
4. Jalankan aplikasi dengan `python manage.py runserver`.
5. Buka `http://127.0.0.1:8000/` di browser.

## Tugas 1

### 1. Penggunaan elemen semantik HTML5

Saya menggunakan elemen semantik `header`, `nav`, `main`, `section`,
`article`, dan `footer`. Elemen tersebut memisahkan navigasi, profil, daftar
kemampuan, dan informasi penutup berdasarkan fungsi masing-masing, bukan hanya
berdasarkan tampilannya. Struktur ini membuat HTML lebih mudah dibaca dan
dirawat. Elemen semantik juga membantu browser serta teknologi bantu seperti
screen reader memahami hierarki halaman.

### 2. Tantangan membuat layout responsif

Tantangan utamanya adalah mempertahankan keterbacaan foto, informasi profil,
dan kartu skill saat lebar layar berkurang. Pada desktop, profil menggunakan
CSS Grid dua kolom dan bagian skill menggunakan tiga kolom. Pada layar maksimal
600px, foto dipindahkan ke bawah identitas dan kartu skill diubah menjadi satu
kolom. Saya memprioritaskan urutan identitas, foto, detail profil, lalu skills
agar informasi utama tetap muncul lebih dahulu pada perangkat mobile.

### 3. Batasan static web dan rencana fitur dinamis

Pada static web, perubahan informasi pengalaman, proyek, atau kemampuan harus
dilakukan langsung di HTML dan membutuhkan deployment ulang. Pengunjung juga
belum dapat memfilter proyek, mengirim pesan, atau melihat data yang diperbarui
secara dinamis. Pada iterasi berikutnya, saya ingin menyimpan data proyek dalam
database dan menambahkan formulir kontak agar konten dapat dikelola dengan lebih
efisien serta masukan pengunjung dapat diproses oleh aplikasi.

## Penggunaan AI

Saya menggunakan ChatGPT Codex untuk membantu mendiagnosis konfigurasi Django,
menjelaskan autentikasi Git ke PWS, menyusun draft section Skills dan CSS
responsif, serta menyusun struktur awal jawaban reflektif. Saya meninjau kembali
hasil tersebut dan menyesuaikan isi profil, kemampuan, dan penjelasan agar sesuai
dengan proyek yang saya kerjakan.

### Ringkasan Prompt

- “i have tried to run this but it gives error while running” untuk mencari
  penyebab aplikasi Django gagal berjalan.
- “fatal: Authentication failed ...” untuk mencari penyebab push ke PWS gagal.
- “ini adalah tugas satu lanjutan dari tutorial 1” untuk memeriksa persyaratan
  Individual Assignment 1.
- “implementasikan” untuk menambahkan section Skills, CSS responsif, dan
  dokumentasi tugas.
  -Setelah AI mengimplementasikan perubahan, melakukan testing manual dan perbaikan seperti skill dan bio dari skill/focus cards yang diasumsikan oleh AI, modifikasi manual sebelum melakukan push kepada git dan memastikan tidak ada kesalahan sebulumnya.

### Strategi Prompting

-Memberikan context dari tugas 1 dan file project portofolio agar memberi gambaran untuk tugas-tugasnya.
-Meminta ringkasan apa yang akan diubah dan apa yang akan diimplementasikan oleh AI.
-Melakukan impelementasi secara langsung dari AI.
-Memastikan dan melakukan testing hasil dari implemantasi AI dan memastikan bahwa hasil sesuai dengan kenyataan dan bukan hanya asumsi dari AI.
-Melakukan modifikasi manual dari hasil implementasi AI.
-Melanjutkan push git dan pengisian dokumentasi dan strategi promting setelah memastikan kebenaran tugas.

-https://chatgpt.com/s/cx_6a997bb7d40c8191975f36872d959160 ini adalah log chatGPT dalam pengerjaan tugas.
