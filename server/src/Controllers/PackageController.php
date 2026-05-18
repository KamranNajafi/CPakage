<?php

namespace App\Controllers;

use App\Database;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Psr7\Stream;

class PackageController
{
    private const NAME_PATTERN = '/^[a-z][a-z0-9-]{0,48}[a-z0-9]$/';

    // GET /api/v1/packages/{name}
    public function getPackage(Request $request, Response $response, array $args): Response
    {
        $db  = Database::get();
        $pkg = $this->findPackage($db, $args['name']);

        if (!$pkg) {
            return $this->json($response, ['error' => "Package '{$args['name']}' not found"], 404);
        }

        $versions = $this->getVersions($db, $pkg['id']);
        $pkg['keywords']       = json_decode($pkg['keywords'] ?? '[]', true);
        $pkg['latest_version'] = $versions[0]['version'] ?? null;
        $pkg['versions']       = $versions;

        return $this->json($response, $pkg);
    }

    // GET /api/v1/packages/{name}/versions
    public function listVersions(Request $request, Response $response, array $args): Response
    {
        $db  = Database::get();
        $pkg = $this->findPackage($db, $args['name']);

        if (!$pkg) {
            return $this->json($response, ['error' => "Package '{$args['name']}' not found"], 404);
        }

        $stmt = $db->prepare('SELECT version, published_at, downloads FROM package_versions WHERE package_id = ? ORDER BY published_at DESC');
        $stmt->execute([$pkg['id']]);

        return $this->json($response, $stmt->fetchAll());
    }

    // GET /api/v1/packages/{name}/{version}/download
    public function download(Request $request, Response $response, array $args): Response
    {
        $db  = Database::get();
        $pkg = $this->findPackage($db, $args['name']);

        if (!$pkg) {
            return $this->json($response, ['error' => "Package '{$args['name']}' not found"], 404);
        }

        $stmt = $db->prepare('SELECT * FROM package_versions WHERE package_id = ? AND version = ?');
        $stmt->execute([$pkg['id'], $args['version']]);
        $ver = $stmt->fetch();

        if (!$ver) {
            return $this->json($response, ['error' => "Version '{$args['version']}' not found"], 404);
        }

        if (!file_exists($ver['file_path'])) {
            return $this->json($response, ['error' => 'Package file not found on server'], 500);
        }

        // افزایش شمارنده دانلود
        $db->prepare('UPDATE package_versions SET downloads = downloads + 1 WHERE id = ?')
           ->execute([$ver['id']]);

        $filename = "{$args['name']}-{$args['version']}.tar.gz";
        $stream   = new Stream(fopen($ver['file_path'], 'rb'));

        return $response
            ->withBody($stream)
            ->withHeader('Content-Type', 'application/gzip')
            ->withHeader('Content-Disposition', "attachment; filename=\"$filename\"")
            ->withHeader('Content-Length', (string) filesize($ver['file_path']))
            ->withHeader('X-Checksum-SHA256', $ver['checksum'] ?? '');
    }

    // POST /api/v1/packages/upload
    public function upload(Request $request, Response $response): Response
    {
        $userId   = $request->getAttribute('user_id');
        $username = $request->getAttribute('username');

        $uploadedFiles = $request->getUploadedFiles();
        $body          = $request->getParsedBody();

        if (empty($uploadedFiles['file'])) {
            return $this->json($response, ['error' => 'No file uploaded (field: file)'], 400);
        }
        if (empty($body['manifest'])) {
            return $this->json($response, ['error' => 'Missing manifest JSON (field: manifest)'], 400);
        }

        $manifest = json_decode($body['manifest'], true);
        if (!$manifest) {
            return $this->json($response, ['error' => 'Invalid manifest JSON'], 400);
        }

        $pkgInfo = $manifest['package'] ?? [];
        $name    = strtolower(trim($pkgInfo['name']    ?? ''));
        $version = trim($pkgInfo['version'] ?? '');

        if (!preg_match(self::NAME_PATTERN, $name)) {
            return $this->json($response, ['error' => 'Invalid package name. Use lowercase letters, numbers, and hyphens only.'], 400);
        }
        if (!$version || !preg_match('/^\d+\.\d+\.\d+/', $version)) {
            return $this->json($response, ['error' => 'Invalid version. Use SemVer format (e.g. 1.2.3)'], 400);
        }

        $db  = Database::get();
        $pkg = $this->findPackage($db, $name);

        // چک مالکیت
        if ($pkg && (int) $pkg['owner_id'] !== (int) $userId) {
            return $this->json($response, ['error' => "You don't own package '$name'"], 403);
        }

        // چک نسخه تکراری
        if ($pkg) {
            $stmt = $db->prepare('SELECT id FROM package_versions WHERE package_id = ? AND version = ?');
            $stmt->execute([$pkg['id'], $version]);
            if ($stmt->fetch()) {
                return $this->json($response, ['error' => "Version '$version' already exists for '$name'"], 409);
            }
        }

        // ذخیره فایل
        $file       = $uploadedFiles['file'];
        $cfg        = require __DIR__ . '/../../config.php';
        $storageDir = $cfg['storage']['path'] . '/' . $name;

        if (!is_dir($storageDir)) {
            mkdir($storageDir, 0755, true);
        }

        $filePath = $storageDir . "/$name-$version.tar.gz";
        $file->moveTo($filePath);

        $fileSize = filesize($filePath);
        $checksum = hash_file('sha256', $filePath);

        // ایجاد یا به‌روزرسانی پکیج
        if (!$pkg) {
            $db->prepare('INSERT INTO packages (name, owner_id, description, homepage, license, keywords) VALUES (?, ?, ?, ?, ?, ?)')
               ->execute([
                   $name,
                   $userId,
                   $pkgInfo['description'] ?? null,
                   $pkgInfo['homepage']    ?? null,
                   $pkgInfo['license']     ?? null,
                   json_encode($pkgInfo['keywords'] ?? []),
               ]);
            $packageId = (int) $db->lastInsertId();
        } else {
            $packageId = (int) $pkg['id'];
        }

        // ثبت نسخه
        $build = $manifest['build'] ?? [];
        $db->prepare('INSERT INTO package_versions (package_id, version, build_type, file_path, file_size, checksum, manifest) VALUES (?, ?, ?, ?, ?, ?, ?)')
           ->execute([
               $packageId,
               $version,
               $build['type'] ?? null,
               $filePath,
               $fileSize,
               $checksum,
               json_encode($manifest),
           ]);
        $versionId = (int) $db->lastInsertId();

        // ثبت dependencies
        foreach (($manifest['dependencies'] ?? []) as $depName => $depRange) {
            $db->prepare('INSERT INTO dependencies (package_version_id, dep_name, dep_version_range) VALUES (?, ?, ?)')
               ->execute([$versionId, $depName, $depRange]);
        }

        return $this->json($response, [
            'message'  => "Package '$name' version '$version' published successfully",
            'name'     => $name,
            'version'  => $version,
            'checksum' => $checksum,
        ], 201);
    }

    // ── helpers ──────────────────────────────────────────────────────────

    private function findPackage(\PDO $db, string $name): ?array
    {
        $stmt = $db->prepare('SELECT * FROM packages WHERE name = ?');
        $stmt->execute([$name]);
        $row = $stmt->fetch();
        return $row ?: null;
    }

    private function getVersions(\PDO $db, int $packageId): array
    {
        $stmt = $db->prepare('SELECT version, build_type, file_size, checksum, downloads, published_at FROM package_versions WHERE package_id = ? ORDER BY published_at DESC');
        $stmt->execute([$packageId]);
        return $stmt->fetchAll();
    }

    private function json(Response $response, array $data, int $status = 200): Response
    {
        $response->getBody()->write(json_encode($data, JSON_UNESCAPED_UNICODE));
        return $response->withStatus($status)->withHeader('Content-Type', 'application/json');
    }
}
