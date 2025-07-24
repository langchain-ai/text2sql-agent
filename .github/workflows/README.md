# GitHub Actions Workflows

This directory contains the CI/CD workflows for the text2sql-agent project. The workflows are designed to provide comprehensive quality assurance and automated testing.

## Workflow Overview

### 1. Quality Checks (`quality-checks.yml`)
**Triggers:** Push to main/develop, Pull Requests
**Purpose:** Code quality and style enforcement

- **Linting:** Runs `ruff`, `black`, and `isort` checks
- **Type Checking:** Runs `mypy` for static type analysis
- **Pre-commit Hooks:** Ensures code meets pre-commit standards
- **PR Comments:** Automatically comments on PRs with results

### 2. Test Coverage (`test-coverage.yml`)
**Triggers:** Push to main/develop, Pull Requests
**Purpose:** Test execution with coverage reporting

- **Test Execution:** Runs all tests with coverage
- **Coverage Upload:** Uploads coverage reports to Codecov
- **PR Comments:** Reports test results on PRs

### 3. Comprehensive Tests (`test-with-results.yml`)
**Triggers:** Push to main/develop, Pull Requests
**Purpose:** Detailed test execution with result artifacts

- **Unit Tests:** Tests individual components
- **Integration Tests:** Tests with external dependencies
- **Evaluation Tests:** LLM-based evaluation tests
- **E2E Tests:** End-to-end workflow tests
- **LangSmith Integration:** Automated evaluation reporting

### 4. Docker Deployment (`new-lgp-deployment.yml`)
**Triggers:** Push to main, Merged PRs to main
**Purpose:** Docker image building and deployment

- **Docker Build:** Builds multi-platform Docker image
- **Docker Push:** Pushes to Docker Hub registry
- **LangChain Deployment:** Deploys to LangChain hosted platform
- **Automated Tagging:** Creates semantic versioning tags



## Usage

### Local Development
Use the Makefile targets that correspond to the CI workflows:

```bash
# Quality checks (equivalent to quality-checks.yml)
make lint
make type-check
make pre-commit

# Test coverage (equivalent to test-coverage.yml)
make test

# Format code (auto-fix)
make format
```

### CI/CD Pipeline
The workflows run automatically on:
- **Every PR:** Quality checks, test coverage, comprehensive tests
- **Every push to main/develop:** All checks and tests
- **Push to main/Merged PRs:** Docker deployment to LangChain

### Required Secrets
The following secrets must be configured in your GitHub repository:

- `OPENAI_API_KEY`: For OpenAI API access in tests
- `LANGSMITH_API_KEY`: For LangSmith integration
- `LANGSMITH_TRACING`: For LangSmith tracing
- `CODECOV_TOKEN`: For coverage reporting
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub access token

## Workflow Benefits

1. **Parallel Execution:** Different test types run in parallel for faster feedback
2. **Caching:** UV dependencies are cached to speed up builds
3. **Artifact Management:** Test results and reports are preserved as artifacts
4. **PR Integration:** Automatic commenting and status reporting
5. **Quality Gates:** Multiple layers of quality assurance
6. **Automated Deployment:** Docker images built and deployed automatically

## Troubleshooting

### Common Issues

1. **Cache Misses:** If builds are slow, check that cache keys are consistent
2. **Secret Errors:** Ensure all required secrets are properly configured
3. **Test Failures:** Check the specific test job logs for detailed error information
4. **Coverage Issues:** Verify Codecov token and repository configuration

### Manual Workflow Execution
You can manually trigger workflows using the GitHub Actions UI or by dispatching workflow events via the GitHub API.

## Contributing

When adding new workflows or modifying existing ones:

1. Follow the established naming conventions
2. Use the Makefile targets when possible for consistency
3. Include appropriate error handling and reporting
4. Update this README with any changes
5. Test workflows locally using the Makefile targets
