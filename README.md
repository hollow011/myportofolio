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

Bagian ini menjelaskan kondisi saat Tugas 2. Perubahan alur untuk Tutorial 3
dijelaskan pada bagian Tutorial 3 di bawah.

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

## Tutorial 3: Form dan Data Delivery

Implementasi ini melanjutkan model `Project` dari Tugas 2, bukan menggantinya
dengan model contoh Burhan. Field `technology` dipakai sebagai padanan
`tech_stack`, dan `repository_url` tetap khusus untuk tautan source code.
Field `is_featured`, UUID, halaman detail, serta data lama dipertahankan.
Satu field baru `project_image_url` bersifat opsional (maksimal 500 karakter),
ditambahkan lewat migrasi `0003_project_project_image_url`.

### Fitur dan endpoint

| URL                        | Metode    | Fungsi                                              |
| -------------------------- | --------- | --------------------------------------------------- |
| `/projects/`               | GET       | Daftar proyek dan pencarian judul                   |
| `/projects/add/`           | GET, POST | Form dan penyimpanan proyek valid                   |
| `/projects/<uuid>/`        | GET       | Detail proyek dari Tugas 2                          |
| `/projects/<uuid>/delete/` | POST      | Menghapus satu proyek setelah konfirmasi di halaman |
| `/api/projects/`           | GET       | Serialisasi JSON Django                             |
| `/api/projects/xml/`       | GET       | Serialisasi XML Django                              |

Daftar, JSON, dan XML menerima parameter `?title=portfolio`. Spasi di awal/akhir
dipangkas dan pencarian memakai `title__icontains`. Query kosong mengembalikan
seluruh proyek; tidak ada hasil ditampilkan sebagai empty state atau koleksi kosong.
Format JSON berisi `model`, `pk`, dan `fields`, bukan daftar judul saja.
XML dipisahkan ke endpoint sendiri agar eksperimen XML tidak merusak pembacaan JSON.

Sesuai latihan tutorial, `show_projects` memanggil `get_projects_json`, lalu
melakukan deserialisasi menjadi objek model untuk template. Ini **bukan request
HTTP** ke server lain: keduanya berjalan dalam proses Django yang sama. Alur
ORM -> JSON -> objek model ini sengaja dipakai untuk belajar data delivery;
pada aplikasi server-rendered biasa, QuerySet langsung lebih sederhana dan efisien.

`ProjectForm` menggunakan daftar field eksplisit. POST valid menyimpan data lalu
redirect ke daftar (Post/Redirect/Get); POST tidak valid menampilkan error dan
mempertahankan input. Form kosong juga divalidasi, bukan dianggap GET. Gambar
ditampilkan dari URL publik, bukan diunggah atau diunduh oleh server Django.
Template mewarisi `base.html`, yang menampilkan pesan sukses dan menyediakan
block `title`, `meta`, dan `content`.

### Batas keamanan yang perlu dipahami

- Sesuai pilihan pengguna untuk mengikuti tutorial, tambah dan hapus **tanpa
  login**. Setiap pengunjung dapat menambah atau menghapus proyek jika fitur
  dipublikasikan. Ini belum merupakan pengaturan portofolio produksi yang aman.
- POST menggunakan CSRF token. Origin PWS terdaftar secara spesifik di
  `CSRF_TRUSTED_ORIGINS`. CSRF mencegah pemalsuan request lintas situs; CSRF
  **bukan** autentikasi atau pembatasan hak akses.
- GET ke URL hapus menghasilkan HTTP 405 dan tidak mengubah database. UUID
  yang tidak ditemukan pada POST hapus menghasilkan HTTP 404.
- Konfirmasi menggunakan HTML Popover API (browser modern), dengan tombol
  Cancel sebagai fokus awal. Tombol Cancel, Escape, atau klik di luar menutup
  popover. Konfirmasi UI bukan pengamanan server; POST valid dapat dikirim langsung.
- Penghapusan bersifat permanen. Batasi fitur pengubahan data ke pemilik saat
  autentikasi/otorisasi ditambahkan pada tahap berikutnya.

### Menjalankan dan memeriksa

```bash
cd /Users/adzka/Collage/S3/PBP/myportofolio
source env/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test main
python manage.py runserver
```

Buka `http://127.0.0.1:8000/projects/`, tambah proyek yang benar-benar dibuat,
coba pencarian, buka endpoint JSON/XML, lalu coba Cancel pada konfirmasi hapus.
Untuk mencoba penghapusan, gunakan data percobaan milik sendiri, bukan data utama.
Database lokal tidak otomatis ikut terunggah ke PWS; migrasi juga harus diterapkan
pada lingkungan deployment.

`requirements.txt` tetap `django~=5.0`, sesuai permintaan sebelumnya. Rentang ini
mengizinkan Django 5.x (`>=5.0,<6.0`), **bukan** khusus 5.0.x. Lingkungan lokal
yang diuji menggunakan Django 5.2.17. Jika dosen mewajibkan tepat seri 5.0.x,
konfirmasikan ketentuan itu sebelum mengganti versi dan lingkungan Python.

Pengujian otomatis berjumlah 31: 11 regresi Tugas 2 dan 20 pengujian Tutorial 3.
Cakupannya termasuk validasi form, field opsional, POST kosong, JSON/XML,
pencarian, escaping HTML, UUID tidak ditemukan, pembatasan metode HTTP, pesan
sukses, serta CSRF dengan token dan pemeriksaan origin. Django TestCase memakai
database pengujian terpisah, bukan menghapus data portofolio lokal.

### Git dan pencatatan pengerjaan

Implementasi dikerjakan pada branch `feature/tutorial-3`. Setelah meninjau hasil
dan menjalankan tes, catat satu commit yang jujur menggambarkan pekerjaan ini:

```bash
git status --short
git diff --check
git add main/forms.py main/models.py main/views.py main/urls.py main/tests.py main/migrations/0003_project_project_image_url.py
git add templates/base.html templates/projects.html templates/projects_form.html templates/project_detail.html templates/components/project_delete_modal.html
git add static/css/style.css portofolio/settings.py README.md
git commit -m "feat: implement tutorial 3 forms and data delivery"
git push -u origin feature/tutorial-3
```

Perintah di atas belum berarti merge ke master atau deployment ke PWS. Tinjau
branch terlebih dahulu sebelum menggabungkan dan deploy. Jangan menambah `.env`,
`env/`, atau `db.sqlite3` ke Git. Jangan memalsukan waktu atau memecah perubahan
secara artifisial hanya untuk memberi kesan pengerjaan bertahap. Untuk pekerjaan
berikutnya, buat commit setiap satu perubahan bermakna selesai dan sudah diuji.

### Penggunaan AI pada Tutorial 3

Pengguna memberikan PDF Tutorial 3 dan meminta kelanjutan Tugas 2. AI membantu
membaca spesifikasi, menyesuaikannya dengan field yang sudah ada, mengimplementasi
form/data delivery, menulis tes, memeriksa hasil lokal, dan menyusun dokumentasi.
Pengguna secara eksplisit memilih akses tambah/hapus tanpa login setelah risiko
dijelaskan. Dokumentasi ini tidak mengklaim pengguna telah melakukan review,
pengujian mandiri, commit, push, atau pengumpulan Tutorial 3; langkah tersebut
masih perlu dilakukan dan dicatat sesuai kegiatan sebenarnya.

### Tugas 3

1. **Mengapa ModelForm dan CSRF token?**

   `ModelForm` membentuk field dan validasi berdasarkan model, sehingga aturan
   seperti panjang teks, pilihan gelar, dan URL tidak perlu ditulis ulang.
   `EducationForm` menampilkan semua enam field yang dapat diedit, tanpa UUID
   dan timestamp. Form tetap dirender menjadi HTML; yang dihindari adalah
   duplikasi aturan dan penanganan input secara manual. `is_valid()` memeriksa
   input di server, lalu `save()` menyimpan data. Saat edit, `instance=education`
   mengikat form ke baris lama agar tidak membuat duplikat. Ini mengikuti
   [dokumentasi ModelForm](https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/).

   `{% csrf_token %}` menyertakan token pada form POST internal agar middleware
   Django dapat memeriksa bahwa request memenuhi mekanisme perlindungan CSRF.
   Ini membantu mencegah situs lain mengirim request perubahan data menggunakan
   sesi pengguna tanpa persetujuannya. Token bukan password dan bukan izin
   mengubah data. Karena itu Education juga memeriksa akun admin aktif melalui
   `staff_member_required`. GET tidak mengubah data; POST tanpa token yang valid
   ditolak. Lihat [perlindungan CSRF Django](https://docs.djangoproject.com/en/5.2/ref/csrf/).

2. **Mengapa JSON lebih sering dipilih daripada XML pada aplikasi web modern?**

   JSON merepresentasikan objek, array, string, angka, boolean, dan null dengan
   sintaks ringkas. Strukturnya cocok untuk data API yang dibaca JavaScript,
   seperti daftar Education dengan `is_current` berupa boolean. XML memakai
   elemen/tag dan atribut, sehingga payload sederhana cenderung lebih panjang
   dan pemetaan ke objek aplikasi membutuhkan langkah tambahan. JSON tidak
   otomatis selalu lebih cepat atau lebih aman: ukuran payload, parser, dan
   kebutuhan sistem tetap menentukan. XML tetap berguna pada sistem yang
   membutuhkan struktur dokumen, namespace, atau kontrak pertukaran berbasis XML.
   Proyek ini mempertahankan endpoint XML Projects untuk perbandingan, bukan
   mengubah endpoint JSON menjadi XML dan merusak konsumen JSON yang sudah ada.

3. **Alur JSON dan alasan serialization diperlukan.**

   Request GET `/api/education/` diarahkan oleh URLconf ke `get_education_json`.
   View mengambil QuerySet Education melalui ORM, menerapkan filter institusi
   jika ada, lalu `serializers.serialize("json", education)` menghasilkan teks
   JSON. `HttpResponse` mengirimkannya dengan `Content-Type: application/json`.
   Setiap item berisi `model`, `pk`, dan `fields`; UUID dan timestamp dikonversi
   ke representasi yang sesuai. Objek model/QuerySet Python tidak bisa langsung
   dikirim sebagai JSON karena memiliki tipe, metode, dan state internal yang
   bukan tipe JSON. Serialization mengubahnya menjadi format pertukaran data.

   Untuk halaman `/education/`, `show_education` memanggil fungsi JSON tersebut,
   mendekode response, melakukan `serializers.deserialize`, mengambil `.object`,
   lalu meneruskan daftar hasilnya ke template. Deserialisasi ini tidak memanggil
   `.save()` dan tidak mengubah database. Pemanggilan fungsi JSON di sini masih
   dalam proses Django yang sama, bukan HTTP ke server terpisah. Alur tambahan
   tersebut mengikuti latihan; halaman server-rendered biasa dapat langsung
   memakai QuerySet. Lihat [serialization Django](https://docs.djangoproject.com/en/5.2/topics/serialization/).

#### Implementasi dan pemetaan checklist

Bagian yang dipilih adalah **Education**, terpisah dari Projects Tutorial 3.
Tidak ada riwayat pendidikan pribadi yang diasumsikan atau dimasukkan otomatis.

| Field Education  | Tipe model               | Input                      |
| ---------------- | ------------------------ | -------------------------- |
| `institution`    | CharField                | Teks, wajib                |
| `degree`         | CharField dengan choices | Pilihan kualifikasi, wajib |
| `field_of_study` | CharField                | Teks, wajib                |
| `description`    | TextField                | Teks panjang, opsional     |
| `website`        | URLField                 | URL, opsional              |
| `is_current`     | BooleanField             | Checkbox                   |

UUID dan `created_at` ditentukan otomatis dan tidak dapat diubah melalui form.
Migrasi `0004_education` hanya menambah tabel baru. Model juga terdaftar di admin.

| URL                         | Metode    | Akses dan fungsi                              |
| --------------------------- | --------- | --------------------------------------------- |
| `/education/`               | GET       | Publik: daftar hasil deserialisasi JSON       |
| `/education/add/`           | GET, POST | Admin aktif: membuat data                     |
| `/education/<uuid>/edit/`   | GET, POST | Admin aktif: form terisi data lama dan update |
| `/education/<uuid>/delete/` | POST      | Admin aktif: hapus satu entri                 |
| `/api/education/`           | GET       | Publik: data Education dalam JSON             |
| `/api/experience/`          | GET       | Publik: tambahan JSON Experience              |

Daftar Education dan JSON mendukung `?institution=nama`, pencarian tidak
membedakan kapital ASCII dan memangkas spasi pinggir. Data yang sedang berjalan
ditampilkan lebih dahulu. Halaman menangani kondisi kosong, hasil pencarian
kosong, input tidak valid, pesan sukses, dan konfirmasi penghapusan.

Semua halaman portofolio memakai `extends "base.html"`; struktur header/footer
tidak disalin ke halaman baru. Form create dan update Education memakai satu
template. Bagian field form digunakan bersama Projects melalui
`components/form_fields.html`. Komponen potongan HTML memakai `include`, bukan
`extends`, karena bukan dokumen lengkap. Halaman admin bawaan Django tetap
memakai template admin bawaan, bukan template portofolio.

#### AI disclosure dan log prompting Tugas 3

- Tool: ChatGPT Codex, dengan PDF tugas dan kode proyek sebagai konteks.
- Prompt pengguna: **“lanjutan tugas 3”**, disertai PDF Individual Assignment 3.
- AI mengusulkan Education sebagai bagian lain, lalu meminta keputusan akses.
- Jawaban pengguna: **“Hanya admin yang login; pengunjung bisa melihat data.”**
- Bantuan AI: pemetaan checklist, model/migrasi, ModelForm, view CRUD dan JSON,
  refactoring template, tes otomatis, pemeriksaan browser publik, dan draft
  jawaban reflektif. Dokumentasi teknis diperiksa terhadap dokumentasi Django.
- Koreksi terhadap asumsi: tidak cukup menambah fitur Projects; tugas meminta
  bagian lain. Kontrol UI saja tidak cukup untuk otorisasi; view harus memeriksa
  staff aktif. Serialization/deserialization bukan pengganti akses database
  atau otomatis berarti request HTTP terpisah.
- Keterbatasan AI: tes tidak menjamin bebas semua bug, tidak membuktikan hasil
  penilaian, dan tidak menggantikan demonstrasi pengguna. AI tidak mengetahui
  seluruh riwayat pendidikan atau membuat kredensial pengguna.
- Review/pengujian/perbaikan manual pengguna untuk Tugas 3 belum diklaim telah
  dilakukan. Tambahkan catatan nyata setelah meninjau dan mencoba sendiri.
- Log prompting ringkas di atas mencatat interaksi Tugas 3; tautan share pada
  bagian tugas sebelumnya tidak dianggap otomatis mencakup percakapan terbaru.
