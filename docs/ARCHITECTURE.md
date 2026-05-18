# CPakage — معماری فنی

## Client (cpakage CLI)

### ساختار ماژول‌ها (هدف)

```
cpakage/
├── __init__.py
├── main.py          ← entry point + arg parsing (فعلاً همه چیز اینجاست)
├── installer.py     ← download + extract + install
├── publisher.py     ← login + publish
├── registry.py      ← ارتباط با API سرور
├── manifest.py      ← خواندن/نوشتن cpakage.toml
├── config.py        ← مدیریت ~/.cpakage/config.ini
├── local_repo.py    ← مدیریت installed_packages.json
└── cmake.py         ← تولید FindCPakage.cmake
```

### جریان دستور install

```
cpakage install <pkg>
        │
        ▼
registry.get_package_info(pkg)   ← GET /api/v1/packages/<pkg>
        │ { url, latest_version, dependencies, build_type }
        ▼
dependency_resolver(pkg, deps)   ← بررسی deps و نصب آن‌ها اول
        │
        ▼
installer.download(url)          ← دانلود tar.gz
        │
        ▼
installer.extract(tar.gz)        ← extract به ~/.cpakage/installed_packages/<pkg>/
        │
        ├── header-only → کپی headers به include/
        ├── cmake       → cmake --build و install
        └── make        → make && make install
        │
        ▼
local_repo.register(pkg, ver)    ← ثبت در installed_packages.json
        │
        ▼
cmake.update_config()            ← به‌روزرسانی CPakageConfig.cmake
```

### جریان دستور publish

```
cpakage publish
        │
        ▼
manifest.read("cpakage.toml")    ← خواندن اطلاعات پکیج
        │
        ▼
validation:
  - name منحصربه‌فرد است؟
  - version معتبر است؟ (SemVer)
  - فایل‌های مورد نیاز وجود دارند؟
        │
        ▼
auth.get_token()                 ← از ~/.cpakage/token
        │
        ▼
publisher.pack()                 ← ساخت tar.gz از پروژه
        │
        ▼
POST /api/v1/packages/upload     ← آپلود به registry
```

---

## Server (CPakage-Registry)

### Stack

```
FastAPI (Python 3.11+)
├── SQLAlchemy + PostgreSQL   ← metadata
├── Alembic                   ← database migrations
├── JWT (python-jose)         ← authentication
├── python-multipart          ← file upload
└── aiofiles                  ← async file I/O
```

### Database Schema

```sql
-- کاربران
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    username    VARCHAR(50) UNIQUE NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,  -- bcrypt hash
    created_at  TIMESTAMP DEFAULT NOW()
);

-- پکیج‌ها
CREATE TABLE packages (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,  -- normalized: lowercase, hyphen
    owner_id    INTEGER REFERENCES users(id),
    description TEXT,
    homepage    VARCHAR(500),
    license     VARCHAR(50),
    keywords    TEXT[],
    created_at  TIMESTAMP DEFAULT NOW()
);

-- نسخه‌های پکیج
CREATE TABLE package_versions (
    id           SERIAL PRIMARY KEY,
    package_id   INTEGER REFERENCES packages(id),
    version      VARCHAR(50) NOT NULL,   -- SemVer: 1.2.3
    build_type   VARCHAR(20),            -- header-only | cmake | make
    file_path    VARCHAR(500),           -- مسیر فایل tar.gz روی سرور
    file_size    BIGINT,
    checksum     VARCHAR(64),            -- SHA-256
    manifest     JSONB,                  -- محتوای cpakage.toml
    downloads    INTEGER DEFAULT 0,
    published_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(package_id, version)
);

-- وابستگی‌ها
CREATE TABLE dependencies (
    id                  SERIAL PRIMARY KEY,
    package_version_id  INTEGER REFERENCES package_versions(id),
    dep_name            VARCHAR(100) NOT NULL,
    dep_version_range   VARCHAR(50)             -- مثلاً: >=7.68.0
);
```

### API Endpoints

```
AUTH:
POST /api/v1/auth/register        → { username, email, password }
POST /api/v1/auth/login           → { username, password } → { token }

PACKAGES:
GET  /api/v1/packages/{name}                  → اطلاعات پکیج + آخرین نسخه
GET  /api/v1/packages/{name}/versions         → لیست همه نسخه‌ها
GET  /api/v1/packages/{name}/{version}        → اطلاعات نسخه خاص
GET  /api/v1/packages/{name}/{version}/download → دانلود فایل tar.gz

POST /api/v1/packages/upload                  → آپلود (auth required)
  Body: multipart/form-data
    - file: tar.gz
    - manifest: JSON (محتوای cpakage.toml)

SEARCH:
GET  /api/v1/search?q=query&page=1&limit=20  → جستجوی full-text

STATS:
GET  /api/v1/packages/{name}/stats            → تعداد دانلود، نسخه‌ها
```

### ساختار پوشه‌های سرور

```
CPakage-Registry/
├── app/
│   ├── main.py               ← FastAPI app
│   ├── database.py           ← SQLAlchemy engine + session
│   ├── models.py             ← ORM models
│   ├── schemas.py            ← Pydantic schemas
│   ├── auth.py               ← JWT + password hashing
│   ├── storage.py            ← مدیریت فایل‌ها
│   └── routes/
│       ├── auth.py
│       ├── packages.py
│       └── search.py
├── migrations/               ← Alembic
├── storage/                  ← فایل‌های tar.gz پکیج‌ها
├── web/                      ← frontend ساده (HTML/CSS/JS)
├── tests/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## فرمت آرشیو پکیج

هر پکیج یک `tar.gz` است با این ساختار:

```
<pkg>-<version>/
├── cpakage.toml          ← manifest (اجباری)
├── README.md             ← توضیحات
├── LICENSE
├── include/              ← header files (برای header-only)
│   └── *.h / *.hpp
├── src/                  ← source files (برای cmake/make)
│   └── *.cpp / *.c
└── CMakeLists.txt        ← برای cmake type
```

---

## Security

- آپلود فقط با JWT token معتبر
- هر کاربر فقط پکیج‌های خودش را می‌تواند منتشر کند
- checksum SHA-256 برای integrity verification دانلود
- rate limiting روی API
- اعتبارسنجی `cpakage.toml` قبل از پذیرش آپلود
- SemVer validation برای نسخه‌ها
