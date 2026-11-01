# Pocket Journal — intentionally vulnerable Django lab

**For local coursework use only. Do not deploy publicly or use real passwords/data.**

## Setup

Requires Python 3.10+ and internet access to install Django.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/ and register **two separate accounts** with disposable passwords. Each can create, edit, delete, and search journal entries. Use a private browser window for the second account.

## Five OWASP Top 10:2021 flaws

All vulnerable lines and their fixes are in **the same codebase**. Search for `A01 VULNERABILITY` etc. **To fix a flaw, comment out the vulnerable line(s) and uncomment the matching `FIX` lines.** Keep the server running before and after each change. Python source changes are automatically reloaded by Django's development server.

| Category | File | Real vulnerability | Fix and test |
|---|---|---|---|
| A01 Broken Access Control | `journal/views.py` (`edit_entry`, `delete_entry`) | Logged-in member B can change another member's entry by requesting `/entries/<id>/edit/` or posting to its delete URL. | Scope `get_object_or_404` to `owner=member` in BOTH functions. Repeat request: now 404. |
| A02 Cryptographic Failures | `journal/views.py` (`register`, `login_view`); `journal/models.py` | Raw passwords stored in `journal_member.password` and compared directly. | Run migration command below, then enable `make_password` at registration and `check_password` at login. Verify existing and new users can log in. |
| A03 Injection | `journal/views.py` (`search`) | Search text is interpolated into raw SQL; attacker can modify query syntax and read records beyond the logged-in user's entries. | Replace string-built SQL and `cursor.execute(sql)` with SQL placeholders and bound parameters. Test a quote in the search input: no SQL exception. |
| A07 Identification and Authentication Failures | `journal/views.py` (`login_view`) | No attempt limit; repeated wrong passwords accepted without throttling. | Enable cache-based 5-attempt/15-minute throttling lines, then confirm the sixth failed login returns HTTP 429. |
| A09 Security Logging and Monitoring Failures | `journal/views.py` (`login_view`), `pocket_journal/settings.py` | Failed authentication produces no security log or repeated-attempt alert. | Enable `LOGGING` and both logging calls. Test wrong credentials and check `security.log`; after 5 failures an ERROR-level event is generated. |

### Important: A02 password migration order

Existing users have plaintext passwords in the initial database. **Before** enabling the A02 code changes, run:

```bash
python manage.py hash_legacy_passwords
```

Then comment out both A02 vulnerable lines in `register` and `login_view` and uncomment the two A02 fixes. Otherwise old users cannot log in. This command should only run on a trusted copy of the lab database. Never use real passwords in this lab.

### A07 / A09 integration

A07 rate limiting uses Django's default local-memory cache, suitable for a single-process development server, **not** a production multi-worker deployment. In a real deployment use a shared atomic backend (e.g. Redis), plus throttling at the edge. The A09 alert relies on the A07 counter, so enable A07 before enabling the repeated-failures alert. For A09 alone, the `login_failed` warning can be enabled independently.

### A03 safety note

The vulnerable search uses a single SQL statement (Django SQLite cursor), but SQL injection is still possible without stacked statements. For a controlled test, search for a single apostrophe (`'`) to observe the unsafe SQL behavior; after fixing, the same input is treated as literal text. Avoid probing databases you do not own.

### Testing each category

1. A01: Create an entry as Alice; sign in as Bob and directly visit `/entries/1/edit/` (assuming Alice's entry ID is 1). Before the fix Bob can edit it; after the fix he gets 404.
2. A02: Register with a disposable password, inspect `journal_member.password` in SQLite (e.g. with `python -m sqlite3 db.sqlite3` if supported). Before fix plaintext; after fix a Django password-hash encoding.
3. A03: As a logged-in user search for `'`. Before fix SQLite returns a query error; after fix normal no-results response.
4. A07: Submit wrong password six times. Before fix always regular login response; after fix sixth attempt is 429.
5. A09: Submit wrong password. Before fix no dedicated security log; after fix `security.log` records a WARNING, and with A07 enabled a threshold alert at ERROR level.

## Design notes

- Django CSRF middleware and template autoescaping remain enabled. These are not the intended vulnerabilities.
- The app uses a custom Member model solely to demonstrate plaintext password storage; real Django projects should use `django.contrib.auth` and Django's built-in User model.
- The example `SECRET_KEY` and `DEBUG=True` are **local lab settings**, not additional OWASP examples. Never deploy them.
- A01 changes both editing and deletion so the authorization flaw is completely fixed.
- For A09, logging is accompanied by a threshold-based alert event; operational alert delivery would require a real monitoring service.
- The five OWASP categories are distinct, though some mitigations work together.

## Official references

- https://top10.owasp.org/2021/A01_2021-Broken_Access_Control/
- https://top10.owasp.org/2021/A02_2021-Cryptographic_Failures/
- https://top10.owasp.org/2021/A03_2021-Injection/
- https://top10.owasp.org/2021/A07_2021-Identification_and_Authentication_Failures/
- https://top10.owasp.org/2021/A09_2021-Security_Logging_and_Monitoring_Failures/
