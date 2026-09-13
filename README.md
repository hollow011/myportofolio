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
  - Setelah AI mengimplementasikan perubahan, saya melakukan testing manual dan
    memperbaiki skill serta bio yang sebelumnya diasumsikan oleh AI sebelum
    melakukan push ke Git.

### Strategi Prompting

- Memberikan context Tugas 1 dan file proyek portofolio.
- Meminta ringkasan perubahan dan implementasi dari AI.
- Meminta AI melakukan implementasi secara langsung.
- Menguji hasil implementasi dan memeriksa asumsi AI terhadap data pribadi.
- Melakukan modifikasi manual terhadap hasil implementasi AI.
- Melakukan push Git setelah implementasi dan dokumentasi dipastikan benar.

- Log pengerjaan AI: https://chatgpt.com/s/cx_6a997bb7d40c8191975f36872d959160

## Tutorial 2

Tutorial 2 mengubah halaman portofolio dari halaman statis menjadi struktur
Model-View-Template. Data profil sekarang dikirim oleh view melalui context,
sedangkan halaman `/experience/` menampilkan data `Experience` dari database
menggunakan Django Template Language.

Implementasi Tutorial 2 mencakup:

- aplikasi Django `main`;
- model `Experience` beserta migrasinya;
- view profil dan experience;
- routing dengan namespace `main`;
- template Experience yang menangani kondisi data kosong;
- enam unit test untuk model, view, template, dan routing.

Jalankan pengujian dengan:

```bash
python manage.py test main
```

AI digunakan untuk membaca spesifikasi Tutorial 2, membantu implementasi MVT,
dan menjalankan pemeriksaan serta unit test. Seluruh data pribadi dan pengalaman
tetap harus diperiksa dan disesuaikan secara manual sebelum dikumpulkan.

### Strategi prompting

- Strateginya masih sama dengan sebelumnya pada tugas 1.
- Memberikan context, akses file, meninjau solusi AI, melakukan implementasi,
  test manual, dan perbaikan.

- Log AI masih melanjutkan percakapan Tugas 1:
  https://chatgpt.com/s/cx_6a997bb7d40c8191975f36872d959160

## Tugas 2

### 1. Alur permintaan halaman Projects

Ketika pengguna membuka `/projects/`, `portofolio/urls.py` menerima request dan
meneruskannya ke `main/urls.py` menggunakan `include`. Named route
`main:show_projects` memilih fungsi `show_projects` di `main/views.py`. View
tersebut meminta seluruh data `Project` melalui Django ORM, memasukkan QuerySet
ke dalam context dengan nama `project_list`, lalu mengirimkannya ke
`projects.html`. Template melakukan perulangan terhadap `project_list` dan
Django mengembalikan HTML hasil render sebagai response kepada browser.

### 2. Alasan data disimpan dalam model

Data proyek disimpan dalam model agar struktur dan validasinya konsisten serta
tidak bercampur dengan kode tampilan. Jika data ditulis langsung di template,
setiap penambahan proyek mengharuskan perubahan HTML dan berisiko menimbulkan
duplikasi. Dengan model, view yang sama dapat menampilkan berapa pun jumlah
proyek, data dapat dikelola melalui ORM atau admin, dan template tetap fokus
pada presentasi. Pemisahan ini membuat aplikasi lebih mudah dirawat, diuji, dan
dikembangkan.

### 3. Perbedaan makemigrations dan migrate

`makemigrations` membaca perubahan definisi model dan membuat berkas migrasi
yang mendeskripsikan perubahan skema. `migrate` menerapkan instruksi dalam
berkas migrasi tersebut ke database. Contohnya, ketika model `Project`
ditambahkan dengan field `title`, `description`, `technology`, dan
`repository_url`, saya harus menjalankan `makemigrations` untuk menghasilkan
migrasi baru, lalu menjalankan `migrate` agar tabel proyek benar-benar dibuat
di database.

### Implementasi dan Penggunaan AI

Tugas 2 menambahkan model `Project`, halaman daftar `/projects/`, halaman detail
opsional, routing bernama, template berbasis perulangan, empty state, integrasi
admin, dan unit test. ChatGPT Codex digunakan untuk membaca spesifikasi,
menyusun implementasi MVT, merancang test, merapikan base template, dan
memverifikasi hasil. Saya tetap memeriksa bahwa data contoh proyek sesuai dengan
proyek yang benar-benar dibuat dan meninjau perubahan sebelum dikumpulkan.
