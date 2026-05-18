<?php

namespace App\Controllers;

use App\Database;
use Firebase\JWT\JWT;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class AuthController
{
    public function register(Request $request, Response $response): Response
    {
        $data = json_decode((string) $request->getBody(), true);
        $username = trim($data['username'] ?? '');
        $email    = trim($data['email']    ?? '');
        $password =       $data['password'] ?? '';

        if (!$username || !$email || !$password) {
            return $this->json($response, ['error' => 'username, email and password are required'], 400);
        }
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            return $this->json($response, ['error' => 'Invalid email address'], 400);
        }
        if (strlen($password) < 6) {
            return $this->json($response, ['error' => 'Password must be at least 6 characters'], 400);
        }

        $db = Database::get();

        $stmt = $db->prepare('SELECT id FROM users WHERE username = ? OR email = ?');
        $stmt->execute([$username, $email]);
        if ($stmt->fetch()) {
            return $this->json($response, ['error' => 'Username or email already taken'], 409);
        }

        $hash = password_hash($password, PASSWORD_BCRYPT);
        $db->prepare('INSERT INTO users (username, email, password) VALUES (?, ?, ?)')
           ->execute([$username, $email, $hash]);

        $userId = $db->lastInsertId();
        $token  = $this->generateToken((int) $userId, $username);

        return $this->json($response, ['access_token' => $token, 'token_type' => 'bearer'], 201);
    }

    public function login(Request $request, Response $response): Response
    {
        $data     = json_decode((string) $request->getBody(), true);
        $username = trim($data['username'] ?? '');
        $password =       $data['password'] ?? '';

        if (!$username || !$password) {
            return $this->json($response, ['error' => 'username and password are required'], 400);
        }

        $db   = Database::get();
        $stmt = $db->prepare('SELECT id, password FROM users WHERE username = ?');
        $stmt->execute([$username]);
        $user = $stmt->fetch();

        if (!$user || !password_verify($password, $user['password'])) {
            return $this->json($response, ['error' => 'Invalid username or password'], 401);
        }

        $token = $this->generateToken((int) $user['id'], $username);
        return $this->json($response, ['access_token' => $token, 'token_type' => 'bearer']);
    }

    private function generateToken(int $userId, string $username): string
    {
        $cfg = require __DIR__ . '/../../config.php';
        $payload = [
            'sub'      => $userId,
            'username' => $username,
            'iat'      => time(),
            'exp'      => time() + $cfg['jwt']['expires_in'],
        ];
        return JWT::encode($payload, $cfg['jwt']['secret'], $cfg['jwt']['algorithm']);
    }

    private function json(Response $response, array $data, int $status = 200): Response
    {
        $response->getBody()->write(json_encode($data));
        return $response->withStatus($status)->withHeader('Content-Type', 'application/json');
    }
}
