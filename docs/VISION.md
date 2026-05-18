# CPakage — چشم‌انداز کامل پروژه

## هدف

CPakage می‌خواهد برای C/C++ همان کاری را انجام دهد که `pip` برای Python انجام داده:
یک دستور ساده در ترمینال → کتابخانه آماده استفاده.

```bash
cpakage install openssl
# → دانلود، extract، آماده برای CMake
```

---

## مشکل فعلی C/C++

توسعه‌دهندگان C/C++ برای مدیریت کتابخانه‌ها باید:
- دستی از GitHub دانلود کنند
- خودشان compile کنند
- include path و linker flag را تنظیم کنند
- برای هر سیستم‌عامل جداگانه این کار را انجام دهند

ابزارهای موجود (vcpkg, Conan, CMake FetchContent) پیچیده، سنگین، یا وابسته به IDE خاص هستند.

---

## راه‌حل CPakage

### از دید developer (مصرف‌کننده)

```bash
# نصب کتابخانه
cpakage install nlohmann-json

# نصب نسخه خاص
cpakage install openssl --version 3.2.0

# نصب همه dependencies پروژه
cpakage install -f cpakage.toml

# به‌روزرسانی
cpakage update nlohmann-json

# حذف
cpakage uninstall nlohmann-json

# جستجو
cpakage search "http client"

# اطلاعات پکیج
cpakage info curl

# لیست نصب‌شده‌ها
cpakage list
```

### از دید developer (ناشر پکیج)

```bash
# ثبت‌نام
cpakage register

# ورود
cpakage login

# ایجاد manifest در پروژه
cpakage init

# آپلود پکیج به registry
cpakage publish
```

---

## فرمت پکیج — cpakage.toml

هر پکیج یک فایل `cpakage.toml` دارد (مانند `pyproject.toml` پایتون):

```toml
[package]
name        = "curl-downloader"
version     = "1.2.0"
description = "A simple HTTP downloader using libcurl"
authors     = ["Kamran Najafi <kamran@example.com>"]
license     = "MIT"
readme      = "README.md"
homepage    = "https://github.com/kamrannajafi/curl-downloader"
keywords    = ["http", "curl", "download", "network"]

[dependencies]
libcurl = ">=7.68.0"
openssl = ">=1.1.0"

[build]
type    = "header-only"   # header-only | cmake | make | meson
headers = ["include/"]

# اگر cmake:
# cmake_minimum = "3.15"
# cmake_target  = "curl_downloader"
```

**نوع پکیج‌ها:**

| نوع | توضیح | مثال |
|-----|-------|------|
| `header-only` | فقط `.h` — کپی به include path | nlohmann/json, stb |
| `cmake` | compile با CMake | OpenSSL, Boost |
| `make` | compile با Makefile | zlib |
| `prebuilt` | binary آماده برای هر platform | |

---

## معماری کلی سیستم

```
┌─────────────────────────────────────────────────────┐
│                   Developer                          │
│           cpakage install <pkg>                     │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────┐
│              CPakage Registry Server                 │
│         (مانند PyPI — cpakage.ir)                   │
│                                                      │
│  ┌─────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  FastAPI    │  │PostgreSQL│  │ File Storage  │  │
│  │  REST API   │  │ metadata │  │ (tar.gz files)│  │
│  └─────────────┘  └──────────┘  └───────────────┘  │
│  ┌──────────────────────────────────────────────┐   │
│  │           Web UI (cpakage.ir)                │   │
│  │  جستجو · اطلاعات پکیج · مدیریت account       │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│                  سیستم کاربر                         │
│                                                      │
│  ~/.cpakage/                                         │
│  ├── config.ini                                      │
│  ├── installed_packages.json                         │
│  └── installed_packages/                             │
│      └── <pkg>/                                      │
│          ├── <pkg>-v<ver>.tar.gz   (archive)         │
│          ├── include/               (headers)        │
│          └── lib/                   (compiled libs)  │
│                                                      │
│  پروژه کاربر/                                        │
│  ├── main.cpp                                        │
│  ├── CMakeLists.txt                                  │
│  └── cpakage.toml   (dependencies)                   │
└─────────────────────────────────────────────────────┘
```

---

## CMake Integration (هدف نهایی)

بعد از نصب، developer فقط این را در CMakeLists.txt می‌نویسد:

```cmake
cmake_minimum_required(VERSION 3.15)
project(MyApp)

# CPakage
find_package(CPakage REQUIRED)
cpakage_add_packages()          # خواندن cpakage.toml

add_executable(myapp main.cpp)
target_link_libraries(myapp cpakage::nlohmann-json cpakage::openssl)
```

---

## نقشه راه (Roadmap)

### Phase 1 — MVP واقعی (الان)
- [x] CLI پایه: install / update / uninstall
- [x] فیکس باگ‌ها
- [ ] extract کردن tar.gz بعد از دانلود
- [ ] `cpakage list` و `cpakage info`
- [ ] `cpakage login` / `cpakage register`
- [ ] `cpakage publish`
- [ ] `cpakage init`
- [ ] `cpakage search`

### Phase 2 — اکوسیستم
- [ ] Web Registry UI (cpakage.ir)
- [ ] فرمت استاندارد `cpakage.toml`
- [ ] dependency resolution
- [ ] FindCPakage.cmake ماژول
- [ ] ساخت از source برای `cmake` type

### Phase 3 — بلوغ
- [ ] pre-built binaries (Windows/Linux/macOS)
- [ ] package signing و verification
- [ ] mirror servers
- [ ] CI/CD integration
