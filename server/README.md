# CPakage Registry Server

PyPI-like package registry for C/C++ libraries.

## راه‌اندازی سریع با Docker

```bash
docker-compose up -d
```

API در `http://localhost:8000` در دسترس است.
مستندات: `http://localhost:8000/docs`

## راه‌اندازی دستی

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# تنظیم متغیرهای محیطی
export DATABASE_URL=postgresql://user:pass@localhost/cpakage
export SECRET_KEY=your-secret-key

# اجرا
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Path | توضیح |
|--------|------|-------|
| POST | `/api/v1/auth/register` | ثبت‌نام |
| POST | `/api/v1/auth/login` | ورود → JWT token |
| GET | `/api/v1/packages/{name}` | اطلاعات پکیج |
| GET | `/api/v1/packages/{name}/versions` | لیست نسخه‌ها |
| GET | `/api/v1/packages/{name}/{version}/download` | دانلود |
| POST | `/api/v1/packages/upload` | آپلود (نیاز به auth) |
| GET | `/api/v1/search?q=query` | جستجو |

## ساختار پوشه‌ها

```
server/
├── app/
│   ├── main.py        ← FastAPI app
│   ├── database.py    ← SQLAlchemy
│   ├── models.py      ← ORM models
│   ├── schemas.py     ← Pydantic schemas
│   ├── auth.py        ← JWT + bcrypt
│   ├── storage.py     ← مدیریت فایل‌ها
│   └── routes/
│       ├── auth.py
│       ├── packages.py
│       └── search.py
├── storage/           ← فایل‌های پکیج
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```
