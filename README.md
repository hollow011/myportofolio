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
4. Terapkan skema database dengan `python manage.py migrate`.
5. Jalankan aplikasi dengan `python manage.py runserver`.
6. Buka `http://127.0.0.1:8000/` di browser.

Aturan akses terbaru untuk Education ada di bagian **Tugas 4**. Bagian mingguan
sebelumnya merupakan catatan implementasi pada saat itu, bukan aturan terbaru.

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
- Log prompting ringkas di atas mencatat interaksi Tugas 3; tautan share pada
  bagian tugas sebelumnya tidak dianggap otomatis mencakup percakapan terbaru.

## Tutorial 4: Authentication, Session, dan Cookies

Tutorial 4 melanjutkan Tugas 3. Aturan Projects di bagian Tutorial 3 adalah
catatan historis: mulai Tutorial 4, tambah/hapus Projects **tidak lagi terbuka
tanpa login**. Education tetap memakai aturan admin aktif dari Tugas 3; fitur
peran tambahan dan star Education untuk Assignment 4 belum diimplementasikan.

### Fitur dan aturan akses terbaru

| Tindakan                                                 | Pengunjung        | Akun biasa | Staff aktif | Superuser aktif    |
| -------------------------------------------------------- | ----------------- | ---------- | ----------- | ------------------ |
| Melihat profil, Experience, Education, Projects, dan API | Ya                | Ya         | Ya          | Ya                 |
| Star/Unstar Projects                                     | Harus login       | Ya         | Ya          | Ya                 |
| Tambah/hapus Projects                                    | Harus login       | 403        | 403         | Ya                 |
| Tambah/edit/hapus Education                              | Harus login admin | Ditolak    | Ya          | Ya jika juga staff |

Register di `/register/` memakai `UserCreationForm`; akun baru tidak menjadi
staff/superuser dan belum otomatis login. `/login/` memakai `AuthenticationForm`
dan membuat session Django. Navbar menampilkan username akun, sedangkan nama,
bio, NPM, dan informasi pemilik portofolio tidak berubah. Password di-hash oleh
Django, bukan disimpan sebagai teks biasa. Referensi:
[autentikasi Django](https://docs.djangoproject.com/en/5.2/topics/auth/default/).

Login mengarahkan pengguna ke halaman profil, sesuai tutorial. Parameter `next`
yang ditambahkan `login_required` belum diproses; pengguna kembali ke Projects
untuk menekan Star setelah login. Logout tersedia sebagai **form POST dengan
CSRF**, bukan GET seperti contoh PDF. GET `/logout/`, GET star, dan GET hapus
menghasilkan HTTP 405 tanpa mengubah data. Ini mencegah tautan/prefetch mengubah
sesi atau data. Semua form POST tetap memakai `{% csrf_token %}`. Referensi:
[CSRF Django](https://docs.djangoproject.com/en/5.2/ref/csrf/).

### Session dan cookie

- Django memakai cookie `sessionid` untuk mengenali session di server; password
  dan role tidak disalin ke cookie buatan aplikasi.
- Cookie `last_login` dibuat ketika login melalui `/login/` berhasil. Nilainya
  adalah waktu login tersebut dalam WIB, bukan riwayat login sebelumnya.
- Cookie ini tidak memiliki `max_age`, memakai `HttpOnly` dan `SameSite=Lax`;
  atribut `Secure` dipasang jika request dikenali Django sebagai HTTPS.
- Halaman profil membaca `request.COOKIES.get(...)` dengan nilai default bila
  cookie tidak tersedia. Nilainya hanya informasi browser, bukan bukti identitas
  atau dasar otorisasi; pengguna tetap bisa memodifikasi cookie melalui alatnya.
- Logout menghapus session dan meminta browser menghapus `last_login`. Akun dan
  star pengguna tetap tersimpan di database. Login melalui admin bawaan Django
  berbagi sistem session, tetapi tidak menjalankan kode cookie kustom `/login/`.

### Star dan data delivery

`Project.starred_by` adalah relasi many-to-many ke `settings.AUTH_USER_MODEL`,
dengan reverse relation `user.starred_projects`. Migrasi `0005_project_starred_by`
menambah tabel penghubung tanpa menghapus proyek lama. Field ini sengaja tidak
dimasukkan ke `ProjectForm`: pengguna hanya boleh mengubah star miliknya sendiri
melalui POST `/projects/<uuid>/star/`, bukan mengirim daftar ID pengguna.

Jumlah star selalu terlihat; tooltip menyebut username pemberi star. Halaman
registrasi memberi tahu bahwa username terlihat publik ketika memberi star.
JSON dan XML Projects memakai `use_natural_foreign_keys=True`, sehingga relasi
ditampilkan sebagai `[["username"]]`, bukan ID numerik akun. API tersebut tidak
menserialisasi objek User lengkap, email, atau hash password. Natural key bukan
mekanisme otorisasi dan tidak membuat username privat. Referensi:
[natural keys Django](https://docs.djangoproject.com/en/5.2/topics/serialization/#natural-keys).

Daftar Projects tetap melakukan deserialisasi JSON sebagaimana Tutorial 3.
Relasi star di-prefetch untuk rendering tombol; objek hasil deserialisasi tidak
disimpan ulang ke database. Kontrol tambah/hapus disembunyikan dari bukan
superuser, dan pemeriksaan server tetap dilakukan walaupun URL diketik langsung.

### Penggunaan AI

Prompt pengguna: **“lanjutan tutorial 4”**, dengan PDF Tutorial 04. AI membaca
spesifikasi, mempertahankan data pemilik dan aturan Education, mengimplementasi
auth/star, menulis serta menjalankan tes, memeriksa UI publik, dan menyusun
dokumentasi. Penyesuaian yang disengaja: logout memakai POST, POST kosong tetap
divalidasi, waktu cookie memakai timezone Django, serta XML memakai natural keys
agar konsisten dengan JSON. Tidak ada klaim pengguna sudah melakukan review
manual atau pengumpulan. Riwayat percakapan lama yang dibagikan belum tentu
mencakup pesan Tutorial 4; log prompt ringkas ini mencatat lingkup bantuannya.

### kritik untuk AI

AI mengasumsikan pemotongan syntax yang salah membuat rendering site /projects/ template syntax error.

## Tugas 4 - Authentication, Session, Cookies, dan Editor

Bagian yang dilanjutkan dari Tugas 3 adalah **Education**. Autentikasi bawaan
Django, session login, cookie `last_login`, dan logout POST memakai implementasi
Tutorial 4 yang sudah ada. Projects tidak diubah hak aksesnya oleh tugas ini.
Tidak ada pertanyaan reflektif wajib pada PDF Tugas 4.

### Hak akses Education yang berlaku sekarang

| Peran                           | Daftar/detail/JSON | Star/unstar  | Tambah       | Edit         | Hapus        |
| ------------------------------- | ------------------ | ------------ | ------------ | ------------ | ------------ |
| Pengunjung                      | Boleh              | Login dahulu | Login dahulu | Login dahulu | Login dahulu |
| Akun biasa                      | Boleh              | Boleh        | 403          | 403          | 403          |
| Editor (anggota Group `Editor`) | Boleh              | Boleh        | 403          | Boleh        | 403          |
| Superuser aktif                 | Boleh              | Boleh        | Boleh        | Boleh        | Boleh        |

`is_staff` saja **bukan** hak mengelola Education. Ini menggantikan aturan
Tugas 3 yang memberi staff akses tambah/edit/hapus. Superuser tidak perlu
`is_staff` untuk mengelola lewat halaman Education, tetapi tetap memerlukannya
untuk masuk Django Admin. Akun nonaktif tidak dapat login.

Pemeriksaan terpusat di `main/permissions.py` dipakai view, konteks template,
dan `EducationAdmin`. Pengunjung dialihkan ke `/login/?next=...`; pengguna
terautentikasi yang tidak berhak menerima 403, termasuk saat mengetik URL atau
mengirim POST langsung. Tombol yang tidak diizinkan tidak dirender. Django Admin
juga tidak dapat dipakai staff/Editor untuk melewati aturan tambah/hapus.
Seperti Tutorial 4, login kembali ke profil; setelah login, buka Education
kembali untuk melakukan aksi. Parameter `next` tidak diterima sebagai redirect
sebarang dan POST star tidak diputar ulang otomatis.

### Perubahan model, halaman, dan API

- `Education.starred_by`: ManyToMany ke `settings.AUTH_USER_MODEL`, melalui
  migrasi `0006_education_starred_by`. Constraint tabel relasi membatasi satu
  pasangan Education-pengguna; bintang tidak dapat diisi lewat EducationForm
  maupun form Django Admin.
- `POST /education/<uuid>/star/`: toggle untuk identitas dari session,
  bukan `user_id`/role kiriman form; wajib login dan CSRF. GET tidak mengubah data.
- Daftar Education menampilkan total star, status Star/Unstar dengan
  `aria-pressed`, dan label login bagi pengunjung. Komponen yang sama digunakan
  pada halaman detail publik baru `/education/<uuid>/`.
- `/api/education/` mempertahankan format serializer Django dan pencarian
  `?institution=...`. Field diizinkan secara eksplisit; `starred_by` memakai
  natural key berupa username publik, bukan password, email, session, maupun
  daftar permission. Identitas username pemberi star terlihat melalui API ini.
- Daftar tetap mengonsumsi JSON melalui deserialisasi sesuai Tugas 3. Relasi
  star di-prefetch lagi setelah deserialisasi untuk rendering kartu. Instance
  deserialisasi tidak disimpan ulang dan tidak mengubah relasi pengguna.
- Tes kompilasi seluruh template ditambahkan untuk menangkap tag Django rusak.
  `.prettierignore` yang sudah ada mencegah formatter HTML memotong tag Django.

### Setup dan pengaturan Editor

```bash
cd /Users/adzka/Collage/S3/PBP/myportofolio
source env/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test main
python manage.py runserver
```

Untuk instalasi baru, gunakan `.venv` dari instruksi di atas bila `env` belum ada.
Jangan menyalin database lokal atau virtual environment ke GitHub/PWS.
Migrasi di PWS harus dijalankan oleh deployment atau console PWS; menjalankan
migrasi lokal tidak mengubah database server.

1. Gunakan akun superuser sendiri; bila belum ada, jalankan
   `python manage.py createsuperuser` dan masukkan kredensial sendiri, bukan
   melalui kode/README/chat.
2. Masuk `/admin/` sebagai superuser. Di **Groups**, buat grup bernama persis
   `Editor` (huruf besar E). Group ini tidak memerlukan tambahan model permission
   karena aplikasi memeriksa keanggotaannya secara eksplisit.
3. Di **Users**, pilih akun yang ingin dipercaya, tambahkan Group `Editor`, lalu
   simpan. Jangan aktifkan `Superuser status`. `Staff status` tidak diperlukan
   untuk mengedit lewat `/education/`.
4. Login akun tersebut melalui `/login/`. Akun boleh edit Education dan star,
   tetapi tidak boleh tambah/hapus. Cabut keanggotaan grup untuk mencabut hak edit.

Grup dan penetapan anggota dikelola pemilik melalui Admin, bukan melalui
registrasi publik. Implementasi ini tidak otomatis membuat akun atau memberi
peran Editor ke akun yang sudah ada.

### Verifikasi dan batas pengujian

Hasil pengujian lokal Tugas 4: **103 tes lulus** (81 tes sebelumnya yang
disesuaikan + 22 tes tambahan). Tes otomatis mencakup empat peran, staff tanpa peran, akun nonaktif, pencabutan
Editor, akses URL langsung, penolakan eskalasi role dari registrasi/form,
CSRF/origin, metode HTTP, star milik sendiri, constraint satu star,
integritas/privasi JSON, escaping HTML, dan pembatasan Django Admin termasuk
bulk delete. Tes memakai database terpisah; bukan akun/data portofolio asli.

Migrasi `0006` sudah diterapkan pada database lokal. Server lokal berhasil
dijalankan, dan pemeriksaan browser mencakup daftar/detail Education sebagai
pengunjung serta pengalihan tombol star ke login. Alur terautentikasi diuji
dengan Django Test Client; tidak ada akun baru atau peran pengguna asli yang
diubah untuk pengujian browser. Deployment PWS Tugas 4 belum diverifikasi.

Cek manual sebelum pengumpulan: buka daftar/detail sebagai pengunjung; gunakan
akun biasa untuk star/unstar; gunakan Editor untuk edit dan pastikan tambah/hapus
ditolak; gunakan superuser untuk CRUD. Lakukan percobaan penghapusan hanya pada
data percobaan sendiri. Tidak ada klaim pengguna sudah menjalankan review ini.

Konfigurasi produksi bawaan (`DEBUG`, secret, cookie, proxy HTTPS, rate limiting)
tidak diubah pada tugas ini. Lulus tes tugas bukan audit keamanan produksi.

### AI disclosure dan log prompting Tugas 4

- Tool: ChatGPT Codex. Prompt pengguna: **“lanjutan tugas 4”**, disertai PDF
  Individual Assignment 4. Dokumen dipakai sebagai spesifikasi tugas, bukan
  izin untuk mengirim submisi atau mengubah akun pengguna.
- Strategi: baca PDF, cocokkan ketentuan dengan Tutorial 4/Tugas 3, implementasi
  pada Education, lalu uji akses server untuk semua peran dan regresi fitur lama.
- Bagian dibantu AI: model/migrasi star, fungsi pemeriksaan akses, view/URL,
  template daftar/detail/star, pengamanan EducationAdmin, tes, dan dokumentasi.
- Keterbatasan yang diperiksa: menyembunyikan tombol bukan otorisasi; staff tidak
  sama dengan pemilik; data star tidak boleh mengikuti user ID kiriman form;
  endpoint serializer tidak boleh mengekspor objek User secara penuh. Tes lama
  yang menganggap staff boleh CRUD diperbarui sesuai aturan tugas baru, bukan
  dihapus untuk menutupi kegagalan.

AI: mengasumskian berbagai hal dan masih harus diperbaiki secara manual karena berbeda dengan CRUD

## Tutorial 05 — Web Interactivity with JavaScript

Implementasi lokal 29 September 2026 mengikuti
[Tutorial 05](https://pbp.cs.ui.ac.id/tutorial/tutorial-5.html) yang diberikan.
Ini kelanjutan Tutorial 4/Tugas 4, **bukan implementasi Individual Assignment 5**.
Identitas, desain portfolio, autentikasi, cookie login, dan aturan Education
(pemilik/Editor/pengunjung) tidak diubah.

### Perubahan

- Halaman Projects menjadi kerangka HTML. Browser mengambil daftar melalui
  Fetch API dari `/api/projects/`, dengan status loading, kosong, gagal, dan Retry.
- Pencarian menunggu 300 ms setelah input terakhir; Enter/Search langsung
  menjalankannya. AbortController dan nomor permintaan mencegah hasil lama
  menimpa pencarian terbaru, termasuk selama jeda debounce.
- Pemilik (superuser) menambah proyek lewat popover form tanpa reload.
  `POST /projects/add-ajax/` mengembalikan JSON: 201 sukses, 400 validasi,
  403 tanpa hak akses, 405 metode selain POST. CSRF tetap diwajibkan.
  Form lama `/projects/add/` tetap tersedia.
- Toast global menampilkan sukses/gagal di atas popover. Kesalahan form juga
  tetap terlihat di dalam form setelah toast hilang. Tombol submit dinonaktifkan
  selama pengiriman untuk mencegah klik ganda.
- JSON dirakit manual menggunakan field proyek asli: `technology` dan
  `repository_url`, bukan mengganti model menjadi field contoh tutorial.
  Tambahan `star_count`, `is_starred`, dan `starred_by_names` mendukung kartu
  dinamis; respons personal tidak boleh di-cache. API ini bukan lagi keluaran
  serializer yang dapat langsung dideserialisasi menjadi model. Endpoint XML
  tetap memakai serializer dan natural keys seperti sebelumnya.
- Star/unstar serta hapus tetap POST biasa (dengan reload), sesuai cakupan
  tutorial. Kartu dinamis membawa token CSRF; hapus meminta konfirmasi browser.
  Otorisasi server tetap menentukan izin, bukan atribut HTML atau tombol.
- Semua teks JSON dirender dengan `createElement`/`textContent`, alternatif
  escaping yang diizinkan tutorial. Tautan/gambar hanya menerima HTTP/HTTPS.
  `ProjectForm` menghapus tag pada judul, deskripsi, teknologi dan menolak hasil
  kosong; berlaku pada form biasa maupun AJAX. `strip_tags` bukan pengganti
  escaping dan dapat memotong teks seperti `List<String>`.

### Verifikasi

- **117 tes Django lulus**: regresi tugas sebelumnya dan delapan tes Tutorial 5
  untuk hak akses, CSRF/origin, validasi, respons JSON, dan visibilitas form.
- **5 tes JavaScript lulus**: rendering teks/URL aman, kontrol peran, CSRF form,
  pembatalan hapus, debounce, respons terlambat, empty state, HTTP/network error
  dan pemulihan Retry. Tes ini memakai DOM double, bukan pengganti tes browser.
- Browser lokal dengan database sementara: daftar publik, pencarian, empty
  state, login akun uji pemilik, tambah AJAX, star, validasi spasi/tag HTML,
  dan toast di atas form diperiksa. Popover diperiksa pada desktop dan lebar
  390 px tanpa overflow horizontal. Data/akun asli tidak diubah.
- Tidak perlu migrasi model baru. Pemeriksaan sintaks JavaScript dan
  `git diff --check` lulus.
- Berkas `.env*`, database SQLite, dan virtual environment tidak dilacak Git.
  Konfigurasi keamanan produksi bawaan tidak diubah; ini bukan audit produksi.

### Pengumpulan dan disclosure

AI yang digunakan: ChatGPT Codex. Prompt: **“continue tutorial 5”** dengan
materi Tutorial 05. Bantuan meliputi penyesuaian view/form/URL, template, CSS,
JavaScript, tes, dan dokumentasi. Contoh tutorial disesuaikan ke field serta
desain proyek ini; Education dan aturan Tugas 4 tidak dirombak.
Pengguna tetap perlu mempelajari alur Fetch → view → ModelForm → JSON → DOM
dan memeriksa hasil sebelum mengumpulkan; tidak ada klaim review pengguna
atau pengumpulan sudah dilakukan.

### Tugas 5

1. **Debouncing pada pencarian AJAX**

   Debouncing menunda eksekusi sampai tidak ada input baru selama jeda tertentu.
   Di Education, setiap input membatalkan timer sebelumnya lalu menjadwalkan
   pencarian setelah **300 ms**. Mengetik sebuah nama institusi tidak langsung
   mengirim satu request untuk setiap karakter; jumlah request dan beban server
   berkurang. Tombol Search/Enter membatalkan timer dan langsung mencari.

   Debouncing saja tidak mengatasi respons yang datang tidak berurutan.
   Karena itu implementasi juga membatalkan request lama dengan AbortController
   dan memeriksa nomor request sebelum merender hasil. Hasil pencarian lama
   tidak boleh menimpa kata kunci terbaru, termasuk selama jeda debounce.
   Throttling berbeda: membatasi frekuensi eksekusi per interval, bukan
   menunggu pengguna selesai mengetik.

2. **Fungsi await bersama fetch()**

   `fetch(url)` mengembalikan Promise. `await fetch(url)` menunda kelanjutan
   fungsi async sampai Promise selesai, lalu menghasilkan objek Response.
   Penundaan ini tidak memblokir seluruh browser; event lain tetap dapat
   diproses. Membaca body JSON juga asinkron, sehingga digunakan
   `const data = await response.json()`.

   Tanpa await atau penanganan Promise yang setara seperti `.then()`,
   variabel berisi Promise, bukan Response/data yang siap dipakai.
   Memanggil `response.json()` pada Promise akan gagal, dan urutan pembaruan
   UI dapat menjadi salah. Menghapus await tidak membatalkan request jaringan.
   `response.ok` juga tetap harus diperiksa: HTTP 400/403/500 tidak otomatis
   membuat fetch menolak Promise. try/catch menangani kegagalan jaringan
   dan kesalahan yang dilempar setelah pemeriksaan status.

3. **XSS dan rendering data AJAX**

   XSS terjadi ketika data tidak tepercaya ditafsirkan sebagai kode aktif
   di halaman aplikasi. Contohnya nama institusi
   `<img src="x" onerror="alert('XSS!')">` yang disimpan lalu dimasukkan ke
   `innerHTML`: event handler gambar dapat berjalan sebagai kode situs.
   Dampaknya dapat berupa pembacaan data halaman atau tindakan memakai sesi
   korban. Token CSRF tidak menghentikan skrip yang sudah berjalan di situs.

   Template Django secara default meng-escape variabel, sedangkan interpolasi
   string ke innerHTML dari JSON tidak mendapat escaping Django. **AJAX sendiri
   bukan penyebab XSS**; penggunaan output yang tidak amanlah penyebabnya.
   Template dengan `safe` sembarangan juga rentan, sementara AJAX dengan
   rendering yang benar tetap aman.

   Education membentuk elemen dengan createElement dan mengisi setiap teks
   menggunakan textContent, termasuk judul, deskripsi, label gelar, nama
   pemberi star, serta pesan error. URL situs diperiksa agar hanya HTTP/HTTPS;
   escaping HTML saja tidak memblokir `javascript:`. EducationForm memakai
   clean_institution, clean_field_of_study, dan clean_description dengan
   strip_tags. Field wajib yang menjadi kosong ditolak; deskripsi opsional
   boleh kosong. Field degree memakai validasi pilihan, website memakai
   URLField. Pembersihan server berlaku untuk create biasa, AJAX, dan edit.
   strip_tags bukan sanitizer HTML yang menjamin keamanan, dapat mengubah
   teks seperti `List<String>`, dan tidak membersihkan data lama secara
   otomatis. Karena itu keamanan output tetap wajib.

#### Implementasi dan setup mingguan

Bagian yang dikerjakan adalah **Education** dari Tugas 3–4; Projects Tutorial 5
tidak diubah. Bagian README terdahulu merupakan catatan historis: sejak Tugas 5,
daftar Education tidak lagi melakukan deserialisasi JSON di dalam view.

- `GET /education/`: kerangka halaman, konfigurasi route, token CSRF,
  dan form kosong hanya ditampilkan bagi pemilik.
- `GET /api/education/?institution=...`: JsonResponse manual berisi
  `model`, `pk`, dan `fields`. Field asli dipertahankan kecuali representasi
  relasi `starred_by` diganti `star_count`, `is_starred`, dan
  `starred_by_names`; `degree_display` ditambahkan. Ini kontrak UI,
  bukan fixture serializer untuk diimpor kembali. Tidak ada password/email
  pengguna di JSON, dan respons personal memakai `no-store/private`.
- `POST /education/add-ajax/`: memakai EducationForm yang sama dengan
  jalur biasa, status 201 sukses, 400 error field, 403 tanpa izin.
  Metode selain POST menghasilkan 405. CSRF middleware tidak dinonaktifkan.
- `static/js/education.js`: fetching, rendering aman, debounce, modal
  dan pengiriman FormData. Loading/empty/error ditampilkan terpisah.
  Retry, Clear search, hitungan hasil yang diumumkan melalui live region,
  dan tautan JSON mengikuti filter aktif.
- Toast Tutorial 5 dipakai ulang melalui base.html. Tombol submit dinonaktifkan
  selama request. Kegagalan mempertahankan input/modal dan menampilkan pesan
  permanen di form selain toast; respons non-JSON/redirect tidak dianggap sukses.
- Pemilik aktif boleh tambah/edit/hapus, Editor aktif hanya edit, pengguna
  login boleh star, pengunjung tetap boleh membaca. Form/modal tidak dibuat
  untuk peran yang tidak berhak; skrip memeriksa keberadaannya.
  View tetap menjadi pengaman utama meskipun atribut UI dimanipulasi.
- Edit tetap memakai halaman form lama; star dan hapus tetap POST biasa
  dengan reload. Kartu AJAX memakai konfirmasi browser sebelum hapus.
  Komponen hapus pada halaman detail tetap dipertahankan.

#### Verifikasi dan disiplin Git

- **129 tes Django lulus**: 117 tes sebelumnya yang disesuaikan dengan alur
  AJAX dan 12 tes tambahan. Cakupan baru: lima jenis pengunjung termasuk
  staff tanpa izin, akun nonaktif, 201/400/403/405, CSRF/origin, strip_tags,
  field palsu, privasi JSON, status star personal, serta query prefetch
  konstan (dua query untuk daftar publik dengan banyak entri).
- **15 tes JavaScript lulus**: lima tes Projects dan sepuluh tes Education.
  Mencakup peran, XSS, URL berbahaya, token CSRF, debounce, respons terlambat,
  input kosong, Retry, pengiriman ganda, validasi server, HTML 403,
  redirect login, respons sukses tidak sesuai kontrak, dan kegagalan jaringan.
  Tes ini memakai DOM double; bukan bukti otomatis semua browser kompatibel.
- Browser lokal dengan database sementara: publik dapat membaca/mencari,
  pemilik dapat menambah tanpa reload dan mendapat toast, payload tag-only
  ditolak, Editor melihat edit tanpa tambah/hapus, dan pengguna biasa dapat
  unstar tanpa mendapat kontrol pengelolaan.
- Branch pekerjaan: `feature/assignment-5`, berangkat dari commit Tutorial 5
  `f70e059`. Belum commit/push/deploy untuk Tugas 5 pada tahap implementasi ini.
  Jangan mengubah timestamp atau mengarang riwayat progres.
  Kelompok perubahan yang dapat dicommit secara deskriptif: endpoint/validasi,
  UI AJAX/modal, lalu tes/refleksi/dokumentasi.

#### AI disclosure dan log prompting Tugas 5

- Tool: ChatGPT Codex. Prompt pengguna: **“continue”**, disertai isi halaman
  Individual Assignment 5. Materi dipakai sebagai spesifikasi, bukan izin
  untuk mengirim submisi, mengubah akun asli, push, atau deploy.
- Strategi: cocokkan checklist dengan Education dan helper izin Tugas 4;
  bangun endpoint/form lalu UI; uji akses langsung dan browser pada database
  sementara; sesuaikan tes historis yang mengharapkan HTML server-rendered.
- Bagian dibantu AI: view/URL JSON, cleaning EducationForm, template/modal,
  JavaScript Education, tes backend/frontend, dan draf jawaban reflektif ini.
- Analisis keterbatasan: menyalin Projects tanpa penyesuaian akan memakai
  field/peran yang salah; status staff bukan izin tambah. Menghapus tes lama
  tanpa pengganti dapat menyembunyikan regresi. Fetch yang mendapat HTML login
  berstatus 200 tidak berarti penyimpanan berhasil. Sanitasi server saja tidak
  menjamin data lama aman. Semua hal tersebut diperiksa melalui tes.
