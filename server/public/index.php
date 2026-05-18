<?php

declare(strict_types=1);

use App\Controllers\AuthController;
use App\Controllers\PackageController;
use App\Controllers\SearchController;
use App\Middleware\AuthMiddleware;
use DI\Container;
use Slim\Factory\AppFactory;

require __DIR__ . '/../vendor/autoload.php';

$container = new Container();
AppFactory::setContainer($container);
$app = AppFactory::create();

$app->addBodyParsingMiddleware();
$app->addErrorMiddleware(false, true, true);

// ── Auth routes ──────────────────────────────────────────────────────────
$app->post('/api/v1/auth/register', [AuthController::class, 'register']);
$app->post('/api/v1/auth/login',    [AuthController::class, 'login']);

// ── Package routes (public) ──────────────────────────────────────────────
$app->get('/api/v1/packages/{name}',                   [PackageController::class, 'getPackage']);
$app->get('/api/v1/packages/{name}/versions',          [PackageController::class, 'listVersions']);
$app->get('/api/v1/packages/{name}/{version}/download',[PackageController::class, 'download']);

// ── Package routes (auth required) ──────────────────────────────────────
$app->post('/api/v1/packages/upload', [PackageController::class, 'upload'])
    ->add(new AuthMiddleware());

// ── Search ───────────────────────────────────────────────────────────────
$app->get('/api/v1/search', [SearchController::class, 'search']);

$app->run();
