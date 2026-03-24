# bookstore.ps1 — Windows PowerShell equivalent of the Makefile
# Usage: .\bookstore.ps1 <command> [service-name]
# Example: .\bookstore.ps1 seed
#          .\bookstore.ps1 logs order-service
#          .\bookstore.ps1 shell book-service

param(
    [Parameter(Position=0)]
    [string]$Command = "help",

    [Parameter(Position=1)]
    [string]$Service = ""
)

$BASE = "http://localhost:8000"

$SERVICES = @(
    "auth-service", "customer-service", "staff-service", "manager-service",
    "catalog-service", "book-service", "cart-service", "order-service",
    "ship-service", "pay-service", "comment-rate-service", "recommender-ai-service"
)

function Write-Header($text) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Step($text) {
    Write-Host ""
    Write-Host "[>>] $text" -ForegroundColor Yellow
}

function Write-OK($text) {
    Write-Host "[OK] $text" -ForegroundColor Green
}

function Write-Fail($text) {
    Write-Host "[!!] $text" -ForegroundColor Red
}

switch ($Command) {

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    "up" {
        Write-Step "Starting all services (detached)..."
        docker compose up -d
    }

    "build" {
        Write-Step "Building and starting all services..."
        docker compose up --build -d
    }

    "down" {
        Write-Step "Stopping all services..."
        docker compose down
    }

    "clean" {
        Write-Step "Stopping and removing all containers + volumes..."
        docker compose down -v --remove-orphans
    }

    "restart" {
        if (-not $Service) { Write-Fail "Usage: .\bookstore.ps1 restart <service-name>"; exit 1 }
        Write-Step "Restarting $Service..."
        docker compose restart $Service
    }

    "rebuild" {
        if (-not $Service) { Write-Fail "Usage: .\bookstore.ps1 rebuild <service-name>"; exit 1 }
        Write-Step "Rebuilding $Service..."
        docker compose up --build -d $Service
    }

    # ── Logs ──────────────────────────────────────────────────────────────────

    "logs" {
        if ($Service) {
            docker compose logs -f $Service
        } else {
            docker compose logs -f
        }
    }

    # ── Shell ─────────────────────────────────────────────────────────────────

    "shell" {
        if (-not $Service) { Write-Fail "Usage: .\bookstore.ps1 shell <service-name>"; exit 1 }
        docker compose exec $Service bash
    }

    # ── Migrations ────────────────────────────────────────────────────────────

    "migrate" {
        if ($Service) {
            Write-Step "Migrating $Service..."
            docker compose exec $Service python manage.py migrate --noinput
        } else {
            foreach ($svc in $SERVICES) {
                Write-Step "Migrating $svc..."
                docker compose exec $svc python manage.py migrate --noinput
                if ($LASTEXITCODE -eq 0) { Write-OK "$svc done" } else { Write-Fail "$svc failed" }
            }
        }
    }

    # ── Health ────────────────────────────────────────────────────────────────

    "health" {
        Write-Header "Gateway Health Check"
        try {
            $response = Invoke-RestMethod -Uri "$BASE/gateway/health/" -Method Get
            $response | ConvertTo-Json -Depth 5
        } catch {
            Write-Fail "Gateway unreachable. Is it running? Try: .\bookstore.ps1 up"
        }
    }

    "ps" {
        docker compose ps
    }

    # ── Seed ──────────────────────────────────────────────────────────────────

    "seed" {
        Write-Header "Seeding Users"

        $headers = @{ "Content-Type" = "application/json" }

        # Admin
        Write-Step "Creating admin user (admin@bookstore.com / Admin123!)..."
        $body = @{
            email            = "admin@bookstore.com"
            username         = "admin"
            first_name       = "Admin"
            last_name        = "User"
            password         = "Admin123!"
            password_confirm = "Admin123!"
            role             = "admin"
        } | ConvertTo-Json
        try {
            $r = Invoke-RestMethod -Uri "$BASE/api/auth/register/" -Method Post -Body $body -Headers $headers
            Write-OK "Admin created. Token starts with: $($r.access.Substring(0,[Math]::Min(30,$r.access.Length)))..."
        } catch {
            $msg = $_.ErrorDetails.Message
            if ($msg -match "already exists" -or $msg -match "unique") {
                Write-Host "  Admin already exists — skipping" -ForegroundColor DarkYellow
            } else {
                Write-Fail "Admin error: $msg"
            }
        }

        # Staff
        Write-Step "Creating staff user (staff@bookstore.com / Staff123!)..."
        $body = @{
            email            = "staff@bookstore.com"
            username         = "staff1"
            first_name       = "Staff"
            last_name        = "Member"
            password         = "Staff123!"
            password_confirm = "Staff123!"
            role             = "staff"
        } | ConvertTo-Json
        try {
            $r = Invoke-RestMethod -Uri "$BASE/api/auth/register/" -Method Post -Body $body -Headers $headers
            Write-OK "Staff created."
        } catch {
            $msg = $_.ErrorDetails.Message
            if ($msg -match "already exists" -or $msg -match "unique") {
                Write-Host "  Staff already exists — skipping" -ForegroundColor DarkYellow
            } else {
                Write-Fail "Staff error: $msg"
            }
        }

        # Manager
        Write-Step "Creating manager user (manager@bookstore.com / Manager123!)..."
        $body = @{
            email            = "manager@bookstore.com"
            username         = "manager1"
            first_name       = "Store"
            last_name        = "Manager"
            password         = "Manager123!"
            password_confirm = "Manager123!"
            role             = "manager"
        } | ConvertTo-Json
        try {
            $r = Invoke-RestMethod -Uri "$BASE/api/auth/register/" -Method Post -Body $body -Headers $headers
            Write-OK "Manager created."
        } catch {
            $msg = $_.ErrorDetails.Message
            if ($msg -match "already exists" -or $msg -match "unique") {
                Write-Host "  Manager already exists — skipping" -ForegroundColor DarkYellow
            } else {
                Write-Fail "Manager error: $msg"
            }
        }

        # Customer
        Write-Step "Creating customer (alice@example.com / Alice123!)..."
        $body = @{
            email            = "alice@example.com"
            username         = "alice"
            first_name       = "Alice"
            last_name        = "Smith"
            password         = "Alice123!"
            password_confirm = "Alice123!"
            role             = "customer"
        } | ConvertTo-Json
        try {
            $r = Invoke-RestMethod -Uri "$BASE/api/auth/register/" -Method Post -Body $body -Headers $headers
            Write-OK "Customer created."
        } catch {
            $msg = $_.ErrorDetails.Message
            if ($msg -match "already exists" -or $msg -match "unique") {
                Write-Host "  Customer already exists — skipping" -ForegroundColor DarkYellow
            } else {
                Write-Fail "Customer error: $msg"
            }
        }

        Write-Header "Seed Complete"
        Write-Host ""
        Write-Host "Credentials:" -ForegroundColor White
        Write-Host "  Admin    — admin@bookstore.com    / Admin123!" -ForegroundColor Gray
        Write-Host "  Staff    — staff@bookstore.com    / Staff123!" -ForegroundColor Gray
        Write-Host "  Manager  — manager@bookstore.com  / Manager123!" -ForegroundColor Gray
        Write-Host "  Customer — alice@example.com      / Alice123!" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Login endpoint: POST $BASE/api/auth/login/" -ForegroundColor DarkCyan
    }

    # ── E2E Flow Test ─────────────────────────────────────────────────────────

    "test" {
        Write-Header "End-to-End Flow Test"
        $headers = @{ "Content-Type" = "application/json" }

        # Step 1: Login as customer
        Write-Step "1. Logging in as alice@example.com..."
        try {
            $login = Invoke-RestMethod -Uri "$BASE/api/auth/login/" -Method Post -Headers $headers `
                -Body (@{ email = "alice@example.com"; password = "Alice123!" } | ConvertTo-Json)
            $token = $login.access
            Write-OK "Got token: $($token.Substring(0,30))..."
        } catch {
            Write-Fail "Login failed: $($_.ErrorDetails.Message)"
            Write-Host "  Run '.\bookstore.ps1 seed' first." -ForegroundColor DarkYellow
            exit 1
        }

        $authHeaders = @{
            "Content-Type"  = "application/json"
            "Authorization" = "Bearer $token"
        }

        # Step 2: Browse catalog
        Write-Step "2. Browsing catalog..."
        try {
            $catalog = Invoke-RestMethod -Uri "$BASE/api/catalog/" -Method Get
            Write-OK "Catalog returned $($catalog.total) books"
        } catch {
            Write-Host "  Catalog empty (no books seeded yet)" -ForegroundColor DarkYellow
        }

        # Step 3: Trending recommendations
        Write-Step "3. Fetching trending recommendations..."
        try {
            $trending = Invoke-RestMethod -Uri "$BASE/api/recommendations/trending/" -Method Get -Headers $authHeaders
            Write-OK "Got $($trending.trending.Count) trending items"
        } catch {
            Write-Fail "Recommendations error: $($_.ErrorDetails.Message)"
        }

        # Step 4: Health check
        Write-Step "4. Gateway health..."
        try {
            $health = Invoke-RestMethod -Uri "$BASE/gateway/health/" -Method Get
            Write-OK "Overall: $($health.overall)"
            foreach ($svc in $health.services.PSObject.Properties) {
                $status = $svc.Value.status
                $color  = if ($status -eq "healthy") { "Green" } else { "Red" }
                Write-Host "    $($svc.Name): $status" -ForegroundColor $color
            }
        } catch {
            Write-Fail "Health check failed"
        }

        Write-Header "Test Complete"
    }

    # ── Book Seed (optional demo data) ────────────────────────────────────────

    "seed-books" {
        Write-Header "Seeding Demo Books"

        # Login as staff first
        $headers = @{ "Content-Type" = "application/json" }
        try {
            $login = Invoke-RestMethod -Uri "$BASE/api/auth/login/" -Method Post -Headers $headers `
                -Body (@{ email = "staff@bookstore.com"; password = "Staff123!" } | ConvertTo-Json)
            $token = $login.access
        } catch {
            Write-Fail "Staff login failed. Run '.\bookstore.ps1 seed' first."
            exit 1
        }

        $authHeaders = @{
            "Content-Type"  = "application/json"
            "Authorization" = "Bearer $token"
        }

        # Create a category first
        Write-Step "Creating category: Programming..."
        try {
            $cat = Invoke-RestMethod -Uri "$BASE/api/books/categories/" -Method Post -Headers $authHeaders `
                -Body (@{ name = "Programming"; slug = "programming"; description = "Software development books" } | ConvertTo-Json)
            $catId = $cat.id
            Write-OK "Category created: $catId"
        } catch {
            Write-Host "  Category may already exist, fetching..." -ForegroundColor DarkYellow
            $cats = Invoke-RestMethod -Uri "$BASE/api/books/categories/" -Method Get
            $catId = ($cats | Where-Object { $_.slug -eq "programming" })[0].id
            Write-OK "Using category: $catId"
        }

        # Create an author
        Write-Step "Creating author: Robert C. Martin..."
        try {
            $author = Invoke-RestMethod -Uri "$BASE/api/books/authors/" -Method Post -Headers $authHeaders `
                -Body (@{ name = "Robert C. Martin"; bio = "Author of Clean Code and Clean Architecture." } | ConvertTo-Json)
            $authorId = $author.id
            Write-OK "Author created: $authorId"
        } catch {
            $authors = Invoke-RestMethod -Uri "$BASE/api/books/authors/" -Method Get
            $authorId = ($authors | Where-Object { $_.name -like "*Martin*" })[0].id
            Write-OK "Using author: $authorId"
        }

        # Create books
        $books = @(
            @{ title="Clean Code"; isbn="9780132350884"; price=39.99; stock_quantity=50 },
            @{ title="Clean Architecture"; isbn="9780134494166"; price=44.99; stock_quantity=30 },
            @{ title="The Pragmatic Programmer"; isbn="9780135957059"; price=49.99; stock_quantity=25 }
        )

        foreach ($book in $books) {
            Write-Step "Creating: $($book.title)..."
            $body = $book + @{ author_ids = @($authorId); category = $catId; description = "A must-read for software engineers." }
            try {
                $r = Invoke-RestMethod -Uri "$BASE/api/books/" -Method Post -Headers $authHeaders `
                    -Body ($body | ConvertTo-Json)
                Write-OK "Created: $($r.title) [ID: $($r.id)]"
            } catch {
                Write-Fail "Failed: $($_.ErrorDetails.Message)"
            }
        }

        Write-Header "Books Seeded"
        Write-Host "Browse at: $BASE/api/catalog/" -ForegroundColor DarkCyan
    }

    # ── Help ──────────────────────────────────────────────────────────────────

    default {
        Write-Header "Bookstore PowerShell Helper"
        Write-Host ""
        Write-Host "Usage: .\bookstore.ps1 <command> [service]" -ForegroundColor White
        Write-Host ""
        Write-Host "Lifecycle:" -ForegroundColor Yellow
        Write-Host "  up                  Start all services (detached)"
        Write-Host "  build               Build images and start"
        Write-Host "  down                Stop all services"
        Write-Host "  clean               Stop and wipe all volumes"
        Write-Host "  restart <svc>       Restart one service"
        Write-Host "  rebuild <svc>       Rebuild and restart one service"
        Write-Host "  ps                  Show container status"
        Write-Host ""
        Write-Host "Data & Testing:" -ForegroundColor Yellow
        Write-Host "  seed                Create admin/staff/manager/customer users"
        Write-Host "  seed-books          Create demo categories, authors, and books"
        Write-Host "  test                Run end-to-end flow test"
        Write-Host "  health              Check all service health"
        Write-Host ""
        Write-Host "Debugging:" -ForegroundColor Yellow
        Write-Host "  logs [svc]          Tail logs (all or one service)"
        Write-Host "  shell <svc>         Open bash shell in a container"
        Write-Host "  migrate [svc]       Run migrations (all or one service)"
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor DarkCyan
        Write-Host "  .\bookstore.ps1 build"
        Write-Host "  .\bookstore.ps1 seed"
        Write-Host "  .\bookstore.ps1 seed-books"
        Write-Host "  .\bookstore.ps1 test"
        Write-Host "  .\bookstore.ps1 logs order-service"
        Write-Host "  .\bookstore.ps1 shell book-service"
        Write-Host "  .\bookstore.ps1 rebuild pay-service"
        Write-Host ""
    }
}
