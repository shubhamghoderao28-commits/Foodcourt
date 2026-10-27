# BiteBox — Flask Food Ordering App for Git Practice

A small, local-only food-ordering demo with a Flask backend, five HTML templates, and JSON API routes. It is designed for practicing Git branches, pull requests, merge conflicts, and merging feature work into `main`.

## 1. Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>. This is a demo: cart data is stored in the browser session, orders are stored in memory, and there are no real payments or database.

## 2. Pages

- `/` — Home / featured dishes
- `/menu` — Menu with search and category filter
- `/cart` — Cart quantity controls and demo checkout
- `/orders` — Order history

## 3. API endpoints to practise

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/menu` | List menu; optional `?q=pizza&category=Pizza` |
| GET | `/api/menu/1` | Get one menu item |
| GET | `/api/cart` | Get current cart and totals |
| POST | `/api/cart` | Add an item |
| PATCH | `/api/cart/1` | Set quantity; quantity `0` removes it |
| DELETE | `/api/cart/1` | Remove item |
| POST | `/api/checkout` | Create demo order |

Example PowerShell request:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/menu
Invoke-RestMethod -Method Post http://127.0.0.1:5000/api/cart `
  -ContentType "application/json" `
  -Body '{"item_id":1,"quantity":2}'
Invoke-RestMethod http://127.0.0.1:5000/api/cart
```

## 4. Practise branches and merge conflicts

First commit the starter project to GitHub as `main`.

```powershell
git init
git add .
git commit -m "Initial BiteBox food ordering app"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

### Exercise A — Feature branch, commit, merge

```powershell
git switch -c feature/menu-badges
```

Edit `templates/menu.html` to show a badge for each dish (for example, “Popular”). Then:

```powershell
git add templates/menu.html
git commit -m "Add menu badges"
git push -u origin feature/menu-badges
```

Open a GitHub Pull Request from `feature/menu-badges` into `main`, review it, and merge it.

### Exercise B — Create a real merge conflict

1. Make sure `main` is up to date: `git switch main` then `git pull`.
2. Create branch A: `git switch -c feature/delivery-message-a`.
3. In `templates/index.html`, change the hero paragraph text to: `Hot meals delivered in 25 minutes.` Commit it.
4. Return to main and create branch B from main: `git switch main` then `git switch -c feature/delivery-message-b`.
5. Edit that **same paragraph** in `templates/index.html` to: `Fresh food, right at your door.` Commit it.
6. Merge branch A into main first. Then try merging branch B:

```powershell
git switch main
git merge feature/delivery-message-a
git merge feature/delivery-message-b
```

Git should report a conflict because both branches changed the same line differently. Open `templates/index.html` and find markers similar to:

```text
<<<<<<< HEAD
Hot meals delivered in 25 minutes.
=======
Fresh food, right at your door.
>>>>>>> feature/delivery-message-b
```

Choose one message or combine them, and **remove all conflict marker lines**. Then:

```powershell
git add templates/index.html
git commit -m "Resolve conflict in home hero copy"
git push
```

### Exercise C — Simulate a GitHub conflict

1. Push a feature branch to GitHub and open a Pull Request.
2. In another branch or directly on GitHub, change the same lines in `templates/index.html` and merge that change into `main`.
3. Return to your feature branch and merge/rebase the updated `main`.
4. Resolve conflicts locally, run the app, commit, push, and update the Pull Request.

### Exercise D — Add a new feature end-to-end

Try adding a `favorites` feature:
- Add a new route in `app.py`.
- Create `templates/favorites.html`.
- Add a navigation link in `templates/base.html`.
- Add styling in `static/style.css`.
- Test the route and API, commit the feature branch, and merge it via a Pull Request.

## 5. Useful Git commands

```powershell
git status
git branch
git switch main
git pull
git log --oneline --graph --all
git diff main...feature/menu-badges
git merge feature/menu-badges
git merge --abort
```

**Tip:** Never commit unresolved conflict markers. Run the app and inspect `git diff` before committing the resolution.
