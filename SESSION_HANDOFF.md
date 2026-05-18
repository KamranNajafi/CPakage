# SESSION HANDOFF — CPakage

## این فایل برای سشن بعدی است — اول بخوان

---

## وضعیت پروژه (تاریخ: 2026-05-18)

### ریپو: `kamrannajafi/cpakage`
### Branch فعال: `claude/review-github-project-DLjNg`

---

## آنچه در این سشن انجام شد

### ۱. فیکس باگ‌ها در `cpakage/main.py` (commit: d681e9a)
همه باگ‌های زیر برطرف شدند:
- ❌ `from cpakage import main` — circular self-import حذف شد (از main.py، cpakage.py، cpakage-ok.py)
- ❌ `update` بدون `--version` → TypeError — فیکس: حالا `latest_version` از API می‌گیرد
- ❌ بدون error handling برای شبکه/API — فیکس: ConnectionError، Timeout، HTTPError اضافه شد
- ❌ `uninstall` کل دایرکتوری را پاک می‌کرد — فیکس: فقط فایل نسخه مشخص حذف می‌شود
- ❌ `install/update/uninstall` بدون نام پکیج کرش — فیکس: validation اضافه شد
- ❌ مسیرهای relative — فیکس: همه مسیرها به `~/.cpakage/` تغییر کرد
- ❌ `edit_config` مسیر hardcode — فیکس: از `CONFIG_FILE` ثابت استفاده می‌کند
- ❌ `venv-os.py` source activate — فیکس: تبدیل به subprocess شد

### ۲. مستندات (commit: 28fb2c0)
- `CLAUDE.md` — context کامل پروژه برای سشن‌های Claude
- `docs/VISION.md` — نقشه راه کامل
- `docs/ARCHITECTURE.md` — طراحی فنی + Database Schema + API endpoints
- `docs/PACKAGE_FORMAT.md` — فرمت `cpakage.toml` با مثال‌های کامل

### ۳. Server Skeleton در `server/` (commit: 28fb2c0)
FastAPI registry server کامل، مانند PyPI:
```
server/
├── app/
│   ├── main.py          ← FastAPI app + CORS
│   ├── database.py      ← SQLAlchemy + PostgreSQL
│   ├── models.py        ← User, Package, PackageVersion, Dependency
│   ├── schemas.py       ← Pydantic schemas
│   ├── auth.py          ← JWT + bcrypt
│   ├── storage.py       ← مدیریت فایل tar.gz + SHA-256
│   └── routes/
│       ├── auth.py      ← register / login
│       ├── packages.py  ← get / versions / download / upload
│       └── search.py    ← full-text search
├── docker-compose.yml   ← PostgreSQL + API
├── Dockerfile
└── README.md
```

---

## وضعیت فایل‌های پروژه

| فایل | وضعیت | توضیح |
|------|--------|-------|
| `cpakage/main.py` | ✅ فعال | فایل اصلی — همه تغییرات اینجا |
| `cpakage/main.py` | ✅ فیکس‌شده | همه باگ‌ها برطرف شدند |
| `cpakage.py` | ⚠️ Legacy | دست نزن |
| `cpakage-ok.py` | ⚠️ Legacy | دست نزن |
| `cpakage-00.py` | ⚠️ Legacy | دست نزن |
| `server/` | 🆕 جدید | کد سرور — هنوز deploy نشده |

---

## قدم‌های بعدی (به ترتیب اولویت)

### سشن بعدی — کار روی Client (`cpakage/main.py`)

```
Phase 1 — MVP واقعی:
  ✅ CLI پایه (install/uninstall/update)
  ✅ فیکس باگ‌ها
  ⬜ [HIGH] extract کردن tar.gz بعد از دانلود
           → tarfile.extractall() بعد از download در install_package()
           → کپی headers به include path
  ⬜ [HIGH] cpakage login / cpakage register
           → ارسال به POST /api/v1/auth/login
           → ذخیره JWT token در ~/.cpakage/token
  ⬜ [HIGH] cpakage publish
           → خواندن cpakage.toml
           → tar.gz ساختن از پروژه
           → آپلود به POST /api/v1/packages/upload
  ⬜ [MED] cpakage init
           → ایجاد cpakage.toml تعاملی
  ⬜ [MED] cpakage list
           → خواندن installed_packages.json
  ⬜ [MED] cpakage info <pkg>
           → GET /api/v1/packages/<pkg>
  ⬜ [MED] cpakage search <query>
           → GET /api/v1/search?q=<query>
```

### سشن دیگر — کار روی Server (`server/`)
نیاز به ریپوی جداگانه `CPakage-Registry`:
```
  ⬜ ریپوی CPakage-Registry روی GitHub بساز
  ⬜ کد server/ را به آن ریپو منتقل کن
  ⬜ deploy روی سرور (docker-compose up)
  ⬜ تست API با Swagger UI
  ⬜ web UI ساده برای registry
```

---

## معماری — مسیرهای کلیدی

```python
# ثابت‌ها در cpakage/main.py
BASE_DIR       = os.path.expanduser("~/.cpakage")
CONFIG_FILE    = os.path.join(BASE_DIR, "config.ini")
DEFAULT_INSTALL_PATH = os.path.join(BASE_DIR, "installed_packages")

# API فعلی (سرور قدیمی)
API_URL = "https://cpakage.testlink.ir/api/pakage_request_respons.php?name="

# API هدف (سرور جدید)
REGISTRY_URL = "https://cpakage.ir/api/v1"
```

---

## نکته مهم برای سشن بعدی

وقتی روی `cpakage/main.py` کار می‌کنی:
1. `install_package()` را پیدا کن (خط ~90)
2. بعد از `open(package_file, "wb")` → extract اضافه کن
3. برای `cpakage login/publish` توابع جدید به انتهای فایل اضافه کن
4. در `main()` در بخش `if args.command` case جدید اضافه کن

---

## دستور push سشن بعدی

```bash
git push -u origin claude/review-github-project-DLjNg
```
