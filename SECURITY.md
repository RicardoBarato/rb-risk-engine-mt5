# Security Policy

## Public repository policy

Never publish:

- credentials;
- API keys or tokens;
- account numbers;
- broker login details;
- real broker server identifiers;
- `.env` files;
- real `.set` presets;
- MT5 logs;
- Strategy Tester reports;
- optimization outputs;
- real account statements;
- local machine paths;
- proprietary strategy parameters.

## Recommended workflow

- Use demo accounts for public examples.
- Keep real data in ignored local folders or protected non-public storage.
- Review `.gitignore` before adding new artifact types.
- Run a sensitive-term search before pushing.
- Rotate credentials immediately if they are exposed.

## Reporting a security issue

Open a GitHub issue only for non-sensitive security concerns.

If a report contains credentials, account identifiers or sensitive trading details, contact the repository owner privately instead of posting the data publicly.
