<?php

return [
    'db' => [
        'host'     => getenv('DB_HOST')     ?: 'localhost',
        'name'     => getenv('DB_NAME')     ?: 'cpakage',
        'user'     => getenv('DB_USER')     ?: 'root',
        'password' => getenv('DB_PASS')     ?: '',
        'charset'  => 'utf8mb4',
    ],
    'jwt' => [
        'secret'     => getenv('JWT_SECRET') ?: 'change-this-in-production',
        'algorithm'  => 'HS256',
        'expires_in' => 60 * 60 * 24 * 30, // 30 days
    ],
    'storage' => [
        'path' => getenv('STORAGE_PATH') ?: __DIR__ . '/storage',
    ],
];
