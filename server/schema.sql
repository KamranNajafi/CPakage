-- CPakage Registry — Database Schema (MySQL)
-- اجرا کن: mysql -u root -p cpakage < schema.sql

CREATE DATABASE IF NOT EXISTS cpakage CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cpakage;

CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50)  UNIQUE NOT NULL,
    email      VARCHAR(255) UNIQUE NOT NULL,
    password   VARCHAR(255)        NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS packages (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    owner_id    INT NOT NULL,
    description TEXT,
    homepage    VARCHAR(500),
    license     VARCHAR(50),
    keywords    JSON,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS package_versions (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    package_id   INT         NOT NULL,
    version      VARCHAR(50) NOT NULL,
    build_type   VARCHAR(20),
    file_path    VARCHAR(500),
    file_size    BIGINT,
    checksum     CHAR(64),
    manifest     JSON,
    downloads    INT DEFAULT 0,
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_pkg_ver (package_id, version),
    FOREIGN KEY (package_id) REFERENCES packages(id)
);

CREATE TABLE IF NOT EXISTS dependencies (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    package_version_id INT         NOT NULL,
    dep_name           VARCHAR(100) NOT NULL,
    dep_version_range  VARCHAR(50),
    FOREIGN KEY (package_version_id) REFERENCES package_versions(id)
);

CREATE FULLTEXT INDEX idx_pkg_search ON packages(name, description);
