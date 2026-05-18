# SESSION HANDOFF — CPakage

## این فایل برای سشن بعدی است — اول بخوان

---

## وضعیت پروژه (تاریخ: 2026-05-18)

### ریپو: `kamrannajafi/cpakage`
### Branch فعال: `claude/cpakage-cli-implementation-ugeah`

---

## آنچه در این سشن انجام شد

### ۱. پیاده‌سازی دستورات جدید در `cpakage/main.py`

#### Extract tar.gz بعد از دانلود
- در `install_package()` بعد از ذخیره فایل، با `tarfile.extractall()` extract می‌شود
- مسیر: `~/.cpakage/installed_packages/<pkg>/<pkg>-v<ver>/`
- در `uninstall_package()` هم دایرکتوری extracted پاک می‌شود

#### `cpakage login`
- ورودی: username + password (با getpass)
- ارسال به: `POST https://cpakage.ir/api/v1/auth/login`
- ذخیره JWT در: `~/.cpakage/token`

#### `cpakage register`
- ورودی: username + email + password + confirm
- ارسال به: `POST https://cpakage.ir/api/v1/auth/register`
- ذخیره JWT در: `~/.cpakage/token`

#### `cpakage publish`
- خواندن `cpakage.toml` از دایرکتوری جاری
- خواندن JWT از `~/.cpakage/token`
- ساخت tar.gz (با فیلتر .git)
- آپلود به: `POST https://cpakage.ir/api/v1/packages/upload`
- بعد از آپلود، فایل tar.gz محلی حذف می‌شود

#### `cpakage list`
- خواندن `installed_packages.json` و نمایش جدولی

#### `cpakage info <pkg>`
- `GET https://cpakage.ir/api/v1/packages/<pkg>`
- نمایش: name, description, license, homepage, latest, versions

#### `cpakage search <query>`
- `GET https://cpakage.ir/api/v1/search?q=<query>`
- نمایش جدولی: name, latest_version, total_downloads, description

### ۲. انتقال کد سرور به `kamrannajafi/CPakage-Registry`
- تمام فایل‌های `server/` از CPakage به CPakage-Registry منتقل شدند
- فایل‌های اضافه: `.gitignore`, `docker-compose.yml`, `CLAUDE.md`
- branch: `claude/cpakage-cli-implementation-ugeah`

---

## وضعیت فایل‌های پروژه

| فایل | وضعیت | توضیح |
|------|--------|-------|
| `cpakage/main.py` | ✅ کامل | همه دستورات پیاده‌سازی شدند |
| `cpakage.py` | ⚠️ Legacy | دست نزن |
| `cpakage-ok.py` | ⚠️ Legacy | دست نزن |
| `cpakage-00.py` | ⚠️ Legacy | دست نزن |
| `server/` | 🔀 منتقل شد | به CPakage-Registry |

---

## قدم‌های بعدی (به ترتیب اولویت)

```
Phase 2:
  ⬜ [HIGH] cpakage init — ایجاد cpakage.toml تعاملی
  ⬜ [HIGH] deploy سرور روی cpakage.ir (docker-compose up)
  ⬜ [MED]  CMake integration (FindCPakage.cmake)
  ⬜ [MED]  dependency resolution در install
  ⬜ [LOW]  web registry UI
```

---

## معماری — مسیرهای کلیدی

```python
# ثابت‌ها در cpakage/main.py
BASE_DIR       = os.path.expanduser("~/.cpakage")
CONFIG_FILE    = os.path.join(BASE_DIR, "config.ini")
TOKEN_FILE     = os.path.join(BASE_DIR, "token")
DEFAULT_INSTALL_PATH = os.path.join(BASE_DIR, "installed_packages")

API_URL      = "https://cpakage.testlink.ir/api/pakage_request_respons.php?name="
REGISTRY_URL = "https://cpakage.ir/api/v1"
```
