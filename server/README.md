# CPakage Registry Server

PyPI-like package registry for C/C++ libraries — built with PHP 8.1 + Slim 4 + MySQL.

## راه‌اندازی

### پیش‌نیازها
- PHP 8.1+
- MySQL 8.0+
- Composer

### نصب

```bash
# ۱. نصب وابستگی‌ها
composer install

# ۲. ساخت دیتابیس
mysql -u root -p < schema.sql

# ۳. تنظیم متغیرهای محیطی
export DB_HOST=localhost
export DB_NAME=cpakage
export DB_USER=root
export DB_PASS=yourpassword
export JWT_SECRET=your-secret-key
export STORAGE_PATH=/path/to/storage

# ۴. اجرا (dev)
php -S localhost:8000 -t public/
```

### روی Apache/Nginx

DocumentRoot را به پوشه `public/` تنظیم کن.
فایل `public/.htaccess` برای Apache آماده است.

برای Nginx:
```nginx
location / {
    try_files $uri $uri/ /index.php?$query_string;
}
```

---

## API Endpoints

| Method | Path | Auth | توضیح |
|--------|------|------|-------|
| POST | `/api/v1/auth/register` | ❌ | ثبت‌نام |
| POST | `/api/v1/auth/login` | ❌ | ورود → JWT token |
| GET | `/api/v1/packages/{name}` | ❌ | اطلاعات پکیج |
| GET | `/api/v1/packages/{name}/versions` | ❌ | لیست نسخه‌ها |
| GET | `/api/v1/packages/{name}/{version}/download` | ❌ | دانلود فایل |
| POST | `/api/v1/packages/upload` | ✅ | آپلود پکیج |
| GET | `/api/v1/search?q=query` | ❌ | جستجو |

### مثال‌ها

```bash
# ثبت‌نام
curl -X POST https://cpakage.ir/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"kamran","email":"k@example.com","password":"secret"}'

# ورود
curl -X POST https://cpakage.ir/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"kamran","password":"secret"}'

# اطلاعات پکیج
curl https://cpakage.ir/api/v1/packages/nlohmann-json

# دانلود
curl -O https://cpakage.ir/api/v1/packages/nlohmann-json/3.11.2/download

# آپلود
curl -X POST https://cpakage.ir/api/v1/packages/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@nlohmann-json-3.11.2.tar.gz" \
  -F 'manifest={"package":{"name":"nlohmann-json","version":"3.11.2",...}}'

# جستجو
curl "https://cpakage.ir/api/v1/search?q=json"
```

---

## ساختار پوشه‌ها

```
server/
├── public/
│   ├── index.php        ← entry point
│   └── .htaccess
├── src/
│   ├── Controllers/
│   │   ├── AuthController.php
│   │   ├── PackageController.php
│   │   └── SearchController.php
│   ├── Middleware/
│   │   └── AuthMiddleware.php
│   └── Database.php
├── storage/             ← فایل‌های tar.gz (خارج از public)
├── composer.json
├── config.php
├── schema.sql
└── README.md
```
