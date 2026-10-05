# AI prompts

Tool: Claude Code (Claude Opus 5.5), run as an agent in the project directory.

## Prompts used

1. > https://github.com/gregoire-cousin-idnow/identity-check-qa/tree/main/task
   > je veux que tu me cree un programme python en .venv
   > les librairies en bibliotheques seront installees dans le projet
   >
   > *(followed by the full exercise brief pasted from the README)*

2. > n'oublie pas le .venv

## What the tool did / what I checked

- Cloned the repo, read `mock_server/app.py` and the starter layer before
  writing code.
- Set `in-project = true` in `poetry.toml` so the virtualenv is created
  at `./.venv`.
- Implemented the API client and Page Objects, then designed the suite
  (fixtures, markers, data catalogue, in-process mock server).
- Ran the full suite, marker subsets, the `IDCHECK_START_MOCK=false` mode
  against a manually started server, and the UI tests several times in a
  row to check for flakiness. One race (asserting through the API before
  the browser's async upload had finished) was spotted and fixed by
  waiting for the result page first.
