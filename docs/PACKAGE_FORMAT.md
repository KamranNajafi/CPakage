# فرمت استاندارد پکیج CPakage

## فایل Manifest: cpakage.toml

هر پکیج باید یک فایل `cpakage.toml` در root پروژه داشته باشد.

### نمونه کامل

```toml
[package]
name        = "nlohmann-json"
version     = "3.11.2"
description = "JSON for Modern C++"
authors     = ["Niels Lohmann <mail@nlohmann.me>"]
license     = "MIT"
readme      = "README.md"
homepage    = "https://github.com/nlohmann/json"
repository  = "https://github.com/nlohmann/json"
keywords    = ["json", "serialization", "header-only"]

[dependencies]
# نام = "بازه نسخه"
# اگر dependency ندارد این بخش را بنویس:
# (خالی)

[build]
type    = "header-only"
headers = ["include/"]
```

### نمونه با dependency و cmake

```toml
[package]
name        = "curl-downloader"
version     = "1.2.0"
description = "HTTP downloader using libcurl"
authors     = ["Kamran Najafi <kamran@example.com>"]
license     = "MIT"
readme      = "README.md"
keywords    = ["http", "curl", "download"]

[dependencies]
libcurl = ">=7.68.0"
openssl = ">=1.1.0"

[build]
type          = "cmake"
cmake_minimum = "3.15"
cmake_target  = "curl_downloader"
headers       = ["include/"]
sources       = ["src/"]
```

---

## توضیح فیلدها

### بخش [package]

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `name` | ✅ | نام پکیج — فقط lowercase، حروف، اعداد، hyphen |
| `version` | ✅ | نسخه SemVer: `MAJOR.MINOR.PATCH` |
| `description` | ✅ | توضیح کوتاه (حداکثر ۲۰۰ کاراکتر) |
| `authors` | ✅ | آرایه: `["نام <ایمیل>"]` |
| `license` | ✅ | SPDX identifier: MIT, Apache-2.0, GPL-3.0, ... |
| `readme` | ❌ | مسیر فایل README |
| `homepage` | ❌ | آدرس وب سایت |
| `repository` | ❌ | آدرس ریپو git |
| `keywords` | ❌ | آرایه کلیدواژه برای جستجو |

### بخش [dependencies]

```toml
[dependencies]
libcurl = ">=7.68.0"    # حداقل این نسخه
openssl = "=1.1.0"      # دقیقاً این نسخه
zlib    = "^1.2.0"      # compatible: 1.2.x
boost   = "~1.80.0"     # patch: 1.80.x
sqlite  = "*"           # هر نسخه‌ای
```

| عملگر | معنی |
|-------|------|
| `>=1.0.0` | این نسخه یا بالاتر |
| `=1.0.0` | دقیقاً این نسخه |
| `^1.0.0` | سازگار: 1.x.x |
| `~1.0.0` | patch: 1.0.x |
| `*` | هر نسخه |

### بخش [build]

| نوع | توضیح | فیلدهای اضافه |
|-----|-------|--------------|
| `header-only` | فقط header — کپی می‌شود | `headers` |
| `cmake` | compile با CMake | `cmake_minimum`, `cmake_target`, `headers`, `sources` |
| `make` | compile با Makefile | `headers`, `sources` |
| `prebuilt` | binary آماده | `headers`, `libs` |

---

## قوانین نام‌گذاری

- فقط حروف کوچک انگلیسی، اعداد، و hyphen (`-`)
- شروع با حرف
- حداکثر ۵۰ کاراکتر
- نمی‌تواند با hyphen شروع یا تمام شود
- مثال‌های معتبر: `nlohmann-json`, `openssl`, `boost-filesystem`
- مثال‌های غیرمعتبر: `MyLib`, `my_lib`, `-lib`, `lib-`

---

## ساختار آرشیو tar.gz

```
<name>-<version>/
├── cpakage.toml          (اجباری)
├── README.md
├── LICENSE
├── include/              (header files)
│   ├── mylib.h
│   └── mylib/
│       └── detail.hpp
├── src/                  (برای cmake/make)
│   └── mylib.cpp
└── CMakeLists.txt        (برای cmake type)
```

---

## نسخه‌بندی SemVer

```
MAJOR.MINOR.PATCH
  │     │     └── bug fix (عقب‌سازگار)
  │     └── feature جدید (عقب‌سازگار)
  └── تغییر breaking (ناسازگار با قبل)

مثال: 1.0.0 → 1.0.1 (bugfix) → 1.1.0 (feature) → 2.0.0 (breaking)
```

---

## دستور publish

```bash
# ۱. ورود به registry
cpakage login

# ۲. ایجاد cpakage.toml (اگر ندارید)
cpakage init

# ۳. اعتبارسنجی بدون آپلود
cpakage publish --dry-run

# ۴. آپلود واقعی
cpakage publish
```

**فرایند publish:**
1. خواندن `cpakage.toml`
2. اعتبارسنجی فیلدها
3. بررسی وجود نداشتن همان نسخه در registry
4. ساختن `<name>-<version>.tar.gz`
5. محاسبه SHA-256
6. آپلود به `POST /api/v1/packages/upload`
7. نمایش لینک صفحه پکیج
