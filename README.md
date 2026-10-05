# idcheck-qa — QA automation exercise (candidate brief)

## Context

This is a small, self-contained identity-verification ("camera / document
check") service, similar in shape to real KYC/video-ident products. **No
real client, customer data, or third-party endpoint is involved** — a
tiny mock Flask backend plays the role of the verification API and its
web UI, so it runs fully offline and deterministically. Nothing here
needs a network connection, an API key, or any credentials.

## Use case

1. A client app creates a **verification session** via the API.
2. The end user is sent to a web page and **captures/uploads an ID
   document** (a file input stands in for a real camera widget — same
   contract as a real capture flow, but deterministic and CI-friendly).
3. The backend evaluates the document and moves the session to
   `VERIFIED` or `REJECTED`.
4. The result is available both via the **API** (`GET /api/sessions/{id}`)
   and on a **result web page** (`GET /result/{id}`).

Your job is to design and implement an automated test suite that gives
confidence in this flow, at both the API level and the full end-to-end
(browser) level.

## What's already given

The app under test is complete and working — you should not need to
modify it:

- `mock_server/app.py` — the mock identity-verification API + HTML pages.
  Read it; it's short and tells you exactly how the backend behaves
  (including how VERIFIED vs REJECTED is decided).

A starter client/automation layer is also given, partially built:

```
src/idcheck_qa/
├── config.py                       # env-var based runtime config — given, working
├── api/
│   ├── base_client.py              # generic requests.Session wrapper + error mapping — given, working
│   ├── models.py                    # typed response models (dataclasses) — given, working
│   └── identity_api_client.py       # domain client — TODO: implement the 3 methods
└── ui/
    ├── driver_factory.py           # Selenium/WebDriver setup — given, working
    └── pages/
        ├── base_page.py             # shared explicit-wait helpers — given, working
        ├── upload_document_page.py  # Page Object for the capture step — TODO: implement the 4 methods
        └── result_page.py           # Page Object for the result screen — TODO: implement the 2 methods
```

`tests/fixtures/valid_id.jpg` and `tests/fixtures/invalid_id.jpg` are
sample upload files provided for your tests (see `mock_server/app.py` for
why their names matter).

## What you need to build

**This exercise must be completed using pytest, with Selenium for the
browser-driven parts.** It's already wired up as a dev dependency (see
"How to run the app under test" below) — no separate install step needed.

1. **Implement the TODOs.** Each stubbed method in
   [`identity_api_client.py`](src/idcheck_qa/api/identity_api_client.py),
   [`upload_document_page.py`](src/idcheck_qa/ui/pages/upload_document_page.py),
   and [`result_page.py`](src/idcheck_qa/ui/pages/result_page.py)
   has a docstring describing exactly what it should do and which
   endpoint/element it should use. Read `base_client.py` and
   `base_page.py` first — the helpers you need already exist there.
2. **Design and build the test suite itself, in pytest**, on top of that
   client/Page Object layer: test modules, fixtures, markers. There are
   deliberately no test files pre-built — how you organize the suite
   (fixtures, `conftest.py`, markers, directory layout) is part of what's
   being assessed. Your tests can call the domain API client directly for
   the API side, and the Page Objects (backed by Selenium) for the
   browser side.
3. **Write test cases covering, at minimum:**
   - The happy path: create a session, submit a valid document, confirm
     `VERIFIED` via both the API and the result page.
   - The rejection path: submit an invalid document, confirm `REJECTED`.
   - At least one API-level edge case (e.g. an unknown/invalid session
     id).
   - Whatever else you judge worth covering (missing upload, calling
     endpoints out of order, response-shape checks, etc.) — use your own
     judgment about what a real QA suite for this kind of product should
     check.

## How to run the app under test

```bash
poetry install
cp .env.example .env          # optional, defaults already work
poetry run python -m mock_server.app
```

The app listens on `http://127.0.0.1:5005` (configurable via
`IDCHECK_MOCK_PORT` / `.env`). While it's running you can explore it
manually, e.g.:

```bash
curl -X POST http://127.0.0.1:5005/api/sessions
# {"session_id": "...", "status": "PENDING"}

curl -X POST http://127.0.0.1:5005/api/sessions/<session_id>/document \
  -F "document=@tests/fixtures/valid_id.jpg"
# {"session_id": "...", "status": "VERIFIED", "reason": null}

curl http://127.0.0.1:5005/api/sessions/<session_id>
```

Or open `http://127.0.0.1:5005/verify/<session_id>` in a browser to walk
through the capture UI by hand. Stop the server with `Ctrl+C`.

`pytest` is already installed by `poetry install` above, so
`poetry run pytest` works out of the box once you've added test files
under `tests/`. If you need an additional pytest plugin or other
tooling, add it to `pyproject.toml`'s dev dependency group and run
`poetry install` again.

## What will be evaluated

- **Python & automation fundamentals** — correctness of the client/Page
  Object implementations, and quality of the automation code around them.
- **pytest & Selenium** — idiomatic, well-organized use of pytest
  (fixtures, markers, `conftest.py`, parametrization) and Selenium Page
  Objects for the test suite itself; this is required and directly
  assessed, not a bonus.
- **Manual testing sense** — evidence you understand the flow well
  enough to reason about edge cases beyond the two obvious happy/rejected
  paths.
- **How the test project itself is built** — reuse of variables/fixtures
  and test data, cleanliness, and how easily the suite could scale to
  more scenarios or a second environment without rewrites.
- **Working with APIs and layered architectures for E2E testing** —
  whether your E2E tests combine the API and browser layers sensibly
  (e.g. use the API to set up state instead of always going through the
  UI), and whether your test code respects the same transport/domain/test
  separation the starter code uses.
- **Security-minded testing** — e.g. not hard-coding config that belongs
  in environment variables, being deliberate about what test data
  looks like, and considering what an equivalent check against a real
  (non-mock) identity API would need to *not* do (log documents, commit
  secrets, etc.).
- **That it actually runs.** Whatever you submit should install and run
  from a clean checkout using the instructions in your own README update
  or notes.

## Using AI tools

You're welcome to use AI tools (Claude, Copilot, ChatGPT, etc.) while
working on this exercise. **If you do, include the prompts you used**
(a simple `AI_PROMPTS.md` alongside your code is fine) as part of your
submission. We're interested in how you directed the tool — the quality
of your prompts and technical judgement in using/adapting what it
produced — not in penalizing AI use itself.

## Submitting your work

Send back:

- Your completed copy of this project (implemented client/Page Objects +
  your test suite).
- A short note on how to install and run your tests, if it differs from
  what's already documented here.
- `AI_PROMPTS.md`, if you used any AI tooling (see above).

---

## Running the test suite (submission notes)

### Install

Poetry is configured (`poetry.toml`, `in-project = true`) to create the
virtualenv **inside the project** at `./.venv`, so every library lives
with the checkout.

```bash
pipx install poetry            # or: python3 -m pip install --user poetry
poetry install                 # creates ./.venv and installs app + dev deps
cp .env.example .env           # optional, defaults already work
```

Requirements: Python ≥ 3.11 and Google Chrome. The matching chromedriver
is resolved by `webdriver-manager` on first run (one network call, cached
afterwards).

### Run

There is **no need to start the server manually**: the suite boots
`mock_server.app` in-process on `IDCHECK_BASE_URL` for the duration of
the run.

```bash
poetry run pytest                          # everything (or .venv/bin/pytest)
poetry run pytest -m smoke                 # happy + rejection paths, API and UI
poetry run pytest -m api                   # API only, no browser
poetry run pytest -m "ui or e2e"           # browser tests
poetry run pytest -m "not known_defect"    # hide documented product defects
poetry run pytest --html=htmlreport.html --self-contained-html
IDCHECK_HEADLESS=false poetry run pytest -m e2e   # watch the browser
```

To target an already running server or another environment, set
`IDCHECK_START_MOCK=false` and `IDCHECK_BASE_URL=<url>`; no test code
changes.

Expected result: `37 passed, 5 xfailed`.

### Layout

```
tests/
├── conftest.py                    # settings, mock server lifecycle, api_client, session/data fixtures
├── support/documents.py           # test data catalogue (scenarios, statuses, reasons)
├── api/
│   ├── test_sessions.py           # session creation, contract/shape, unknown ids, wrong verbs
│   └── test_document_submission.py# outcome rules, persistence, isolation, out-of-order calls
└── ui/
    ├── conftest.py                # WebDriver + Page Object fixtures, auto `ui` marker
    ├── test_verification_flow.py  # E2E: API setup -> browser capture -> UI + API assertions
    └── test_upload_page.py        # capture page edge cases, HTML-injection check
```

Design choices:

- **Layering** – tests only use the domain client
  (`IdentityVerificationClient`) and Page Objects. Raw transport calls
  (`api_client.post(api_client.document_path(...))`) are used only for
  deliberately malformed requests that the domain API cannot express.
- **API for setup, UI for the journey** – E2E tests create sessions
  through the API; result-page tests set the state through the API and
  only check rendering in the browser. The API is also the oracle after
  a UI submission.
- **Data-driven** – document scenarios (file, expected status, expected
  reason) are declared once in `tests/support/documents.py` and
  parametrized across API and UI tests. Filename variants are generated
  into `tmp_path` by the `make_document` factory.
- **Isolation** – each test creates its own session; the browser is
  shared for speed but reset after each test; mock state is cleared
  after each test when the suite owns the server.
- **Known defects** are kept as `xfail(strict=True)` + `known_defect`
  marker: the suite stays green, the defects stay visible in the report,
  and a fix turns them into XPASS → failure, prompting removal of the
  marker.

### Defects found in the mock backend

| # | Finding | Test |
|---|---------|------|
| 1 | Submitting with **no document** returns `VERIFIED` | `test_submission_without_document_is_not_verified` |
| 2 | An **empty (0-byte) file** is `VERIFIED` | `test_empty_document_is_not_verified` |
| 3 | A `REJECTED` session can be **overturned** to `VERIFIED` by re-submitting | `test_rejected_session_cannot_be_overturned_by_resubmission` |
| 4 | In the UI, "Submit capture" without a file is accepted and `VERIFIED` | `test_submit_without_capture_does_not_verify` |
| 5 | The capture page renders for **any** session id, no error shown | `test_capture_page_for_unknown_session_shows_an_error` |

Also observed: the decision relies only on the filename (`"invalid"` in
the name), and session ids are 12 hex chars (48 bits). That is fine for a
mock but would be a finding against a real service.

### Security notes

- All config comes from env vars / `.env` (git-ignored); nothing
  environment-specific is hard-coded in tests.
- Test documents are synthetic placeholders plus the official public
  **specimen** of the French ID card (`tests/fixtures/specimen_cni_*.jpg`,
  marked "SPÉCIMEN", fictitious holder). They give the suite realistic
  JPEG uploads without any real person's data. Applicant references are
  random `qa-auto-xxxx` values.
- The client logs method + URL only, never request bodies or document
  bytes. Against a real KYC API you would also want to: inject API keys
  from a secret store (never `.env` in git), disable HTTP debug logging
  and failure screenshots of capture pages (they may contain identity
  documents), keep HTML reports out of public CI artifacts, use a
  dedicated sandbox tenant, and clean up the sessions you created.
