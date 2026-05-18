# CPakage — Claude Session Context

## پروژه چیست؟

CPakage یک package manager برای زبان‌های C/C++ است — هدف: تجربه‌ای مانند `pip` برای پایتون.
توسعه‌دهنده می‌تواند با `cpakage install <pkg>` کتابخانه نصب کند و با `cpakage publish` پکیج منتشر کند.
یک registry مرکزی (مانند PyPI) همه پکیج‌ها را نگه می‌دارد.

## ساختار پروژه

```
CPakage/                          ← این ریپو (Client CLI)
├── cpakage/
│   └── main.py                   ← فایل فعال اصلی (اینجا کار کن)
├── docs/
│   ├── VISION.md
│   ├── ARCHITECTURE.md
│   └── PACKAGE_FORMAT.md
├── CLAUDE.md                     ← این فایل
├── SESSION_HANDOFF.md            ← وضعیت سشن
├── setup.py
└── requirements.txt

فایل‌های legacy (دست نزن):
├── cpakage.py
├── cpakage-ok.py
└── cpakage-00.py
```

**ریپوی سرور جدا:** `kamrannajafi/CPakage-Registry`

## Tech Stack

| بخش | فناوری |
|-----|--------|
| Client CLI | Python 3.8+ |
| Package manifest | TOML (`cpakage.toml`) |
| Config | INI (`~/.cpakage/config.ini`) |
| Token | `~/.cpakage/token` (JWT) |
| Local repo DB | JSON (`~/.cpakage/installed_packages.json`) |
| Server API | PHP 8.1 + Slim 4 |
| Server DB | MySQL 8.0 |
| Server Auth | JWT (firebase/php-jwt) |

## Branch فعال

```
claude/cpakage-cli-implementation-ugeah
```

همه تغییرات روی این branch باشند.

## دستورات CLI (پیاده‌سازی شده)

```bash
cpakage install <pkg> [--version <ver>]   # دانلود + extract tar.gz
cpakage update  <pkg> [--version <ver>]   # نصب نسخه جدید
cpakage uninstall <pkg> [--version <ver>] # حذف فایل + دایرکتوری extracted
cpakage list                              # لیست پکیج‌های نصب‌شده
cpakage info <pkg>                        # اطلاعات از registry
cpakage search <query>                    # جستجو در registry
cpakage login                             # ورود به registry → ذخیره JWT
cpakage register                          # ثبت‌نام → ذخیره JWT
cpakage publish                           # خواندن cpakage.toml + ساخت tar.gz + آپلود
cpakage -S -R -P <path>                   # تغییر مسیر repo
cpakage -S -R -V TRUE/FALSE               # versioning
```

## مسیرهای ثابت

```python
BASE_DIR       = ~/.cpakage/
CONFIG_FILE    = ~/.cpakage/config.ini
TOKEN_FILE     = ~/.cpakage/token
INSTALL_PATH   = ~/.cpakage/installed_packages/<pkg>/<pkg>-v<ver>.tar.gz
EXTRACT_PATH   = ~/.cpakage/installed_packages/<pkg>/<pkg>-v<ver>/
REPO_JSON      = ~/.cpakage/installed_packages.json  (یا از config path)
```

## API سرور

```
# سرور قدیمی (برای install)
Base URL: https://cpakage.testlink.ir/api/
Endpoint: pakage_request_respons.php?name=<pkg>
Response: { "url": "...", "latest_version": "...", "project_page": "..." }

# سرور جدید (CPakage-Registry)
Base URL: https://cpakage.ir/api/v1
POST /auth/login       → JWT token
POST /auth/register    → JWT token
GET  /packages/{name}  → اطلاعات پکیج
POST /packages/upload  → آپلود (Bearer token)
GET  /search?q=query   → جستجو
```

## نکات مهم

1. **فایل فعال فقط** `cpakage/main.py` است — بقیه legacy‌اند
2. **SSL verify=False** است — سرور testlink.ir گواهی self-signed دارد
3. **tomllib** برای Python 3.11+ built-in است؛ برای قدیمی‌تر: `pip install tomli`
4. **ریپوی سرور:** `kamrannajafi/CPakage-Registry` — branch همین: `claude/cpakage-cli-implementation-ugeah`

## اولویت‌بندی توسعه

```
Phase 1 (MVP واقعی):
  ✅ CLI پایه (install/uninstall/update)
  ✅ فیکس باگ‌ها
  ✅ extract کردن tar.gz بعد از دانلود
  ✅ cpakage login / register
  ✅ cpakage publish
  ✅ cpakage list / info / search
  ✅ server skeleton (PHP + Slim 4 + MySQL) → CPakage-Registry

Phase 2 (اکوسیستم):
  ⬜ cpakage init (ایجاد cpakage.toml تعاملی)
  ⬜ CMake integration (FindCPakage.cmake)
  ⬜ dependency resolution
  ⬜ web registry UI
  ⬜ deploy روی سرور (docker-compose)

Phase 3 (بلوغ):
  ⬜ pre-built binaries برای platform‌های مختلف
  ⬜ build از source
  ⬜ signing و verification
```
