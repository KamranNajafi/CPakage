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
│   ├── VISION.md                 ← نقشه راه کامل
│   ├── ARCHITECTURE.md           ← معماری فنی
│   └── PACKAGE_FORMAT.md         ← فرمت cpakage.toml
├── CLAUDE.md                     ← این فایل
├── setup.py                      ← تنظیمات pip install
├── requirements.txt
└── config.ini                    ← (قدیمی، جایگزین شده با ~/.cpakage/config.ini)

فایل‌های legacy (دست نزن):
├── cpakage.py                    ← نسخه قدیمی
├── cpakage-ok.py                 ← نسخه قدیمی
└── cpakage-00.py                 ← نسخه اولیه
```

**ریپوی سرور جدا:** `kamrannajafi/CPakage-Registry`

## Tech Stack

| بخش | فناوری |
|-----|--------|
| Client CLI | Python 3.8+ |
| Package manifest | TOML (`cpakage.toml`) |
| Config | INI (`~/.cpakage/config.ini`) |
| Local repo DB | JSON (`~/.cpakage/installed_packages.json`) |
| Server API | FastAPI (Python) |
| Server DB | PostgreSQL |
| Server Storage | Filesystem / S3-compatible |
| Server Auth | JWT |
| Packaging | pip / setuptools |

## Branch فعال

```
claude/review-github-project-DLjNg
```

همه تغییرات روی این branch باشند. برای push:
```bash
git push -u origin claude/review-github-project-DLjNg
```

## دستورات CLI فعلی (پیاده‌سازی شده)

```bash
cpakage install <pkg>
cpakage install <pkg> --version 1.2.3
cpakage update <pkg>
cpakage uninstall <pkg>
cpakage uninstall <pkg> --version 1.2.3
cpakage -S -R -P <path>       # تغییر مسیر repo
cpakage -S -R -V TRUE/FALSE   # versioning
```

## دستورات CLI هدف (باید پیاده‌سازی شود)

```bash
cpakage init                   # ایجاد cpakage.toml
cpakage publish                # آپلود پکیج به registry
cpakage login                  # ورود به registry
cpakage search <query>         # جستجو در registry
cpakage list                   # لیست پکیج‌های نصب‌شده
cpakage info <pkg>             # اطلاعات پکیج
cpakage install -f cpakage.toml  # نصب از manifest
```

## مسیرهای ثابت (بعد از فیکس)

```python
BASE_DIR       = ~/.cpakage/
CONFIG_FILE    = ~/.cpakage/config.ini
INSTALL_PATH   = ~/.cpakage/installed_packages/<pkg>/<pkg>-v<ver>.tar.gz
REPO_JSON      = ~/.cpakage/installed_packages.json
```

## API سرور (فعلی)

```
Base URL: https://cpakage.testlink.ir/api/
Endpoint: pakage_request_respons.php?name=<pkg>
Response: { "url": "...", "latest_version": "...", "project_page": "..." }
```

## API سرور (هدف — CPakage-Registry)

```
GET  /api/v1/packages/{name}              → اطلاعات پکیج
GET  /api/v1/packages/{name}/{version}    → اطلاعات نسخه خاص
POST /api/v1/packages/upload              → آپلود پکیج (نیاز به auth)
GET  /api/v1/search?q=query               → جستجو
POST /api/v1/auth/register                → ثبت‌نام
POST /api/v1/auth/login                   → ورود → JWT token
GET  /api/v1/packages/{name}/versions     → لیست نسخه‌ها
```

## نکات مهم برای Claude

1. **فایل فعال فقط** `cpakage/main.py` است — بقیه legacy‌اند
2. **SSL verify=False** است — سرور testlink.ir گواهی self-signed دارد
3. **پکیج‌ها فعلاً فقط دانلود می‌شوند** — extract/compile هنوز پیاده‌سازی نشده
4. **مهم‌ترین feature بعدی:** extract + CMake integration
5. فرمت manifest: `cpakage.toml` (مانند pyproject.toml پایتون)
6. هدف نهایی: developer با `cpakage install boost` کتابخانه آماده استفاده داشته باشد

## اولویت‌بندی توسعه

```
Phase 1 (MVP واقعی):
  ✅ CLI پایه (install/uninstall/update)
  ✅ فیکس باگ‌ها
  ⬜ extract کردن tar.gz بعد از دانلود
  ⬜ cpakage init (ایجاد manifest)
  ⬜ cpakage publish (آپلود به سرور)
  ⬜ cpakage login/register
  ⬜ cpakage search و cpakage list و cpakage info

Phase 2 (اکوسیستم):
  ⬜ CMake integration (FindCPakage.cmake)
  ⬜ dependency resolution
  ⬜ web registry UI
  ⬜ فرمت استاندارد cpakage.toml

Phase 3 (بلوغ):
  ⬜ pre-built binaries برای platform‌های مختلف
  ⬜ build از source
  ⬜ signing و verification
```
