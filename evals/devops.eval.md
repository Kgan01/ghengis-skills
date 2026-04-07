# DevOps -- Evaluation

## TC-1: Dockerfile for Python/FastAPI
- **prompt:** "Write a Dockerfile for my FastAPI app that uses requirements.txt"
- **context:** User has a standard FastAPI project with a requirements.txt. Expects production-ready Docker practices.
- **assertions:**
  - Uses a slim base image (e.g., `python:3.11-slim`)
  - Copies `requirements.txt` and runs `pip install` BEFORE copying application code (cache layer optimization)
  - Creates and switches to a non-root user
  - Includes a HEALTHCHECK directive
  - Exposes the correct port and uses `uvicorn` or equivalent in the CMD
  - Does not install unnecessary packages or leave apt cache behind
- **passing_grade:** 5/6 assertions must pass

## TC-2: GitHub Actions CI/CD Pipeline
- **prompt:** "Set up a GitHub Actions workflow that lints, tests, and deploys my Python app to a VPS on push to main"
- **context:** Solo developer with a VPS. Needs a complete CI/CD pipeline with test gate before deploy.
- **assertions:**
  - Workflow triggers on push to `main`
  - Includes lint step (ruff, flake8, or equivalent)
  - Includes test step (pytest or equivalent) that runs before deploy
  - Deploy job has `needs: test` (or equivalent dependency) so it only runs after tests pass
  - Deploy uses SSH action or equivalent to connect to VPS
  - Includes a health check step after deployment
  - Secrets are referenced via `${{ secrets.* }}` -- not hardcoded
- **passing_grade:** 5/7 assertions must pass

## TC-3: Secret Found in Repo
- **prompt:** "I accidentally committed an API key to my repo. What do I do?"
- **context:** User has a committed secret. Needs immediate remediation guidance.
- **assertions:**
  - First action: rotate the compromised key immediately (it is already compromised)
  - Recommends removing the secret from git history (filter-branch, BFG, or git-filter-repo)
  - Advises moving secrets to `.env` files with `.gitignore` protection
  - Recommends using environment variables in CI (GitHub Secrets or equivalent)
  - Does not suggest simply deleting the file and committing again (secret remains in history)
- **passing_grade:** 4/5 assertions must pass

## TC-4: Docker Compose Multi-Service Setup
- **prompt:** "I need a docker-compose setup with my FastAPI server, a React frontend, and Redis"
- **context:** Local development multi-service environment.
- **assertions:**
  - Defines three services (server, web/frontend, redis)
  - Uses `env_file` or environment variables for configuration
  - Redis uses an official image (e.g., `redis:7-alpine`) with a named volume for persistence
  - Server has `depends_on` for Redis
  - Frontend has `depends_on` for server
  - Ports are mapped correctly for each service
- **passing_grade:** 5/6 assertions must pass

## TC-5: Rollback Procedure
- **prompt:** "My deploy just broke production. How do I roll back?"
- **context:** Deployment health check failed. User needs to recover quickly.
- **assertions:**
  - Provides immediate rollback steps (not "investigate first")
  - Includes stopping the current broken deployment (`docker compose down` or equivalent)
  - Restores from backup or previous version (git checkout, backup copy, or container tag)
  - Restarts the previous known-good version
  - Includes a verification step (health check after rollback)
  - Recommends investigating the failure after recovery (not before)
- **passing_grade:** 4/6 assertions must pass
