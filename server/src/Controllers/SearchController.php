<?php

namespace App\Controllers;

use App\Database;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class SearchController
{
    // GET /api/v1/search?q=query&page=1&limit=20
    public function search(Request $request, Response $response): Response
    {
        $params = $request->getQueryParams();
        $query  = trim($params['q']     ?? '');
        $page   = max(1, (int) ($params['page']  ?? 1));
        $limit  = min(100, max(1, (int) ($params['limit'] ?? 20)));
        $offset = ($page - 1) * $limit;

        if ($query === '') {
            $response->getBody()->write(json_encode(['error' => 'Query parameter q is required']));
            return $response->withStatus(400)->withHeader('Content-Type', 'application/json');
        }

        $db   = Database::get();
        $like = "%$query%";

        $countStmt = $db->prepare(
            'SELECT COUNT(*) FROM packages WHERE name LIKE ? OR description LIKE ?'
        );
        $countStmt->execute([$like, $like]);
        $total = (int) $countStmt->fetchColumn();

        $stmt = $db->prepare(
            'SELECT p.name, p.description, p.keywords,
                    (SELECT version FROM package_versions WHERE package_id = p.id ORDER BY published_at DESC LIMIT 1) AS latest_version,
                    (SELECT COALESCE(SUM(downloads), 0) FROM package_versions WHERE package_id = p.id) AS total_downloads
             FROM packages p
             WHERE p.name LIKE ? OR p.description LIKE ?
             ORDER BY total_downloads DESC
             LIMIT ? OFFSET ?'
        );
        $stmt->execute([$like, $like, $limit, $offset]);
        $rows = $stmt->fetchAll();

        foreach ($rows as &$row) {
            $row['keywords'] = json_decode($row['keywords'] ?? '[]', true);
        }

        $result = [
            'total'   => $total,
            'page'    => $page,
            'limit'   => $limit,
            'results' => $rows,
        ];

        $response->getBody()->write(json_encode($result, JSON_UNESCAPED_UNICODE));
        return $response->withHeader('Content-Type', 'application/json');
    }
}
