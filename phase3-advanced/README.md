# Phase 3 — Advanced Docker and CI/CD Pipeline

A containerized FastAPI application with automated testing, Docker image publishing, and vulnerability scanning using GitHub Actions and Docker Hub.

## Project Overview

This phase focuses on building a repeatable containerization and CI/CD workflow for a Python application. The objective is to move beyond running an application locally and establish a pipeline that validates the code, builds a Docker image, publishes it to a container registry, and scans the published image for known vulnerabilities.

The application is built with FastAPI and served using Uvicorn. Docker packages the application and its dependencies into a portable image, while GitHub Actions automates the build and publishing process whenever code is pushed to the `main` branch.

The project is part of my hands-on learning journey in Docker, CI/CD automation, container security, and cloud-native deployment practices.

## Objectives

- Build a Docker image for a Python FastAPI application.
- Use a multi-stage Docker build to separate dependency installation from the runtime image.
- Keep application dependencies and development tools organized.
- Run automated tests with Pytest.
- Check code quality using Flake8.
- Automate the CI/CD process using GitHub Actions.
- Publish version-identifiable Docker images to Docker Hub.
- Scan the published image for HIGH and CRITICAL vulnerabilities using Trivy.
- Verify the published image by pulling and running it locally.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| FastAPI | REST API framework |
| Uvicorn | ASGI application server |
| Docker | Application containerization |
| Docker Buildx | Docker image build support |
| Git and GitHub | Version control and source hosting |
| GitHub Actions | CI/CD automation |
| Docker Hub | Container image registry |
| Pytest | Automated testing |
| Flake8 | Python code linting |
| Trivy | Container vulnerability scanning |
| WSL 2 and Docker Desktop | Local development and testing environment |

## Architecture

The pipeline follows a straightforward sequence:

```text
Developer
   |
   v
Git push to main
   |
   v
GitHub Actions
   |
   v
Lint and Automated Tests
   |
   v
Docker Build
   |
   v
Docker Hub Authentication
   |
   v
Publish Docker Image
   |
   +----------------------+
   |                      |
   v                      v
latest tag          commit-specific tag
   |                      |
   +-----------+----------+
               |
               v
      Trivy Vulnerability Scan
               |
               v
      Pull and Run the Image
               |
               v
      Verify Application Endpoints
```

The test job runs before the publishing job. If linting or testing fails, the dependent build-and-push job does not proceed.

## Repository Structure

The relevant project files are organized as follows:

```text
docker-mastery-project/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── phase3-ci-cd.yml
│
└── phase3-advanced/
    ├── app/
    │   └── main.py
    ├── Dockerfile
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── test_main.py
    └── README.md
```

**File responsibilities**

- `app/main.py` — contains the FastAPI application and its API endpoints.
- `Dockerfile` — defines the instructions used to build the application image.
- `requirements.txt` — lists the application's runtime dependencies.
- `requirements-dev.txt` — contains development and testing dependencies.
- `test_main.py` — contains automated tests for the application.
- `.github/workflows/phase3-ci-cd.yml` — defines the Phase 3 CI/CD workflow.
- `.github/workflows/ci.yml` — contains the separate CI workflow maintained in the repository.

## Application Endpoints

The application exposes three endpoints.

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Returns the application's main response |
| `/health` | GET | Provides a basic application health check |
| `/info` | GET | Returns application information, including its version and phase |

The application reports version `1.2.0` and identifies itself as Phase 3 — Advanced.

### Example health-check response

The health endpoint returns a JSON response indicating whether the application is healthy. A timestamp may also be included.

```json
{
  "status": "healthy",
  "timestamp": "..."
}
```

The exact timestamp changes with each request.

## Docker Implementation

The application is packaged using a Dockerfile that uses a multi-stage build.

The build stage prepares the Python environment and installs the required packages. The runtime stage contains the application and the dependencies needed to run it.

This approach helps separate build-time operations from runtime execution and keeps the container configuration more organized.

The image exposes port `8000` and starts the FastAPI application through Uvicorn, listening on `0.0.0.0:8000` inside the container.

### Build the image locally

Run the following commands from the repository root:

```bash
docker build -t docker-mastery-demo:local ./phase3-advanced
```

### Run the local image

```bash
docker run -d \
  --name phase3-local \
  -p 8000:8000 \
  docker-mastery-demo:local
```

### Check the running container

```bash
docker ps
```

### Test the endpoints

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/info
```

### View container logs

```bash
docker logs phase3-local
```

### Stop and remove the container

```bash
docker rm -f phase3-local
```

If port `8000` is already occupied, use a different host port, such as `8001`:

```bash
docker run -d \
  --name phase3-local \
  -p 8001:8000 \
  docker-mastery-demo:local
```

The application can then be accessed at `http://localhost:8001`.

## Local Code Quality and Testing

The CI/CD workflow validates the Python application before publishing the Docker image.

### Install application dependencies

```bash
python -m pip install --upgrade pip
pip install -r phase3-advanced/requirements.txt
pip install -r phase3-advanced/requirements-dev.txt
```

Run these commands from the repository root with the appropriate Python environment activated.

### Run Flake8

```bash
python -m flake8 phase3-advanced/app phase3-advanced/test_main.py
```

Flake8 checks the application and test code for common style issues and potential errors.

### Run Pytest

```bash
python -m pytest -q phase3-advanced/test_main.py
```

Pytest executes the automated test cases. The pipeline proceeds to the image publishing job only when the test job completes successfully.

## GitHub Actions CI/CD Workflow

The Phase 3 workflow is defined in:

```text
.github/workflows/phase3-ci-cd.yml
```

It supports pushes to `main`, pull requests targeting `main`, and manual execution through GitHub Actions.

### Stage 1 — Checkout and environment setup

GitHub Actions checks out the source code and prepares the Python environment required to run the validation steps.

### Stage 2 — Lint and test

The workflow installs the application and development dependencies, runs Flake8, and executes Pytest.

This catches code-quality issues and test failures before attempting to publish a new image.

### Stage 3 — Docker build and publishing

After the test job succeeds, the workflow uses Docker Buildx and the Docker build-and-push action to build the image from `phase3-advanced/Dockerfile`.

The image is published to Docker Hub using two tags:

```text
srini9808/docker-mastery-demo:latest
srini9808/docker-mastery-demo:sha-<commit-sha>
```

The `latest` tag provides a convenient reference to the most recently published image. The commit-specific tag identifies the image associated with a particular source revision.

These are two tags for the published image, not two separate application projects.

### Stage 4 — Trivy vulnerability scan

After publishing, the workflow scans the `latest` image with Trivy for known operating-system and library vulnerabilities classified as HIGH or CRITICAL.

The current workflow is configured with `exit-code: '0'`. Therefore, the scan reports findings but does not fail the pipeline solely because those vulnerabilities are present.

This is an initial reporting configuration, not a strict security gate. A future improvement is to enforce a failure policy for vulnerabilities that meet defined severity and fixability criteria.

## GitHub Secrets Configuration

The workflow uses GitHub Actions secrets to authenticate to Docker Hub.

Open the GitHub repository and navigate to:

**Settings → Secrets and variables → Actions → Secrets**

Configure these repository secrets:

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub personal access token with Read & Write permissions |

The workflow references them as:

```yaml
username: ${{ secrets.DOCKERHUB_USERNAME }}
password: ${{ secrets.DOCKERHUB_TOKEN }}
```

The username and token must match the Docker Hub account that owns or has permission to publish to the repository.

Never hardcode the token in the workflow, commit it to Git, or include it in screenshots or logs.

## Docker Hub Repository

The published image is available here:

**Docker Hub repository:**  
https://hub.docker.com/r/srini9808/docker-mastery-demo

**Image tags:**  
https://hub.docker.com/r/srini9808/docker-mastery-demo/tags

### Pull the published image

```bash
docker pull srini9808/docker-mastery-demo:latest
```

If your local Docker credential helper has issues, a temporary Docker configuration can be used to test a public image:

```bash
mkdir -p /tmp/docker-config-clean

DOCKER_CONFIG=/tmp/docker-config-clean \
docker pull srini9808/docker-mastery-demo:latest
```

This bypasses the normal saved Docker credential configuration for that command. It does not modify your GitHub Actions credentials.

### Run the published image

```bash
DOCKER_CONFIG=/tmp/docker-config-clean \
docker run -d \
  --name docker-mastery-test \
  -p 8001:8000 \
  srini9808/docker-mastery-demo:latest
```

Port `8001` is used on the host to avoid conflicts with existing containers already publishing port `8000`.

### Verify the published container

```bash
docker ps
curl http://localhost:8001/health
curl http://localhost:8001/info
```

A successful health response confirms that the running container responds to the health endpoint. Testing the published image separately from the local build helps verify the artifact that was actually uploaded to Docker Hub.

## Running the CI/CD Workflow

To trigger the pipeline:

1. Make a change to the application, tests, Dockerfile, or workflow.
2. Commit the change to Git.
3. Push the commit to the `main` branch.
4. Open the repository's **Actions** tab.
5. Select the latest Phase 3 workflow run.
6. Review the linting, testing, build, publishing, and scanning results.

A manual run can also be started from the workflow's **Run workflow** option because `workflow_dispatch` is enabled.

Pull requests run the validation job without publishing the image. Publishing is restricted to non-pull-request events.

## Troubleshooting Notes

### Docker Hub login fails with `Username required`

Verify that `DOCKERHUB_USERNAME` exists as a repository secret and that the workflow references `secrets.DOCKERHUB_USERNAME`.

Check the spelling of both secret names.

### Docker Hub reports `access token has insufficient scopes`

Create a Docker Hub personal access token with Read & Write permissions and update `DOCKERHUB_TOKEN` in GitHub repository secrets.

Verify that the token belongs to the intended Docker Hub account and that the repository permissions are correct.

### Docker reports `port is already allocated`

Another container or process is already using the requested host port.

Check active containers:

```bash
docker ps
```

Either stop the container using the port, if it is no longer needed, or publish the new container on another host port:

```bash
-p 8001:8000
```

### Docker pull fails with a WSL credential-helper error

Restart Docker Desktop and WSL if necessary. For a public Docker Hub image, try pulling with a temporary Docker configuration as described earlier in this README.

### Application health check fails

Inspect the container status and logs:

```bash
docker ps -a
docker logs docker-mastery-test
```

Verify that the container is running, port mapping is correct, and the application starts successfully.

### Git push is rejected

Synchronize the local branch with the remote branch before pushing:

```bash
git pull --rebase origin main
git push origin main
```

Resolve any conflicts before continuing. Avoid force-pushing unless you fully understand the impact on the remote repository history.

## Security and Reliability Considerations

This project incorporates several useful DevOps practices:

- Automated validation before image publication.
- Externalized Docker Hub credentials using GitHub Secrets.
- Commit-specific image tags for traceability.
- Vulnerability reporting for operating-system and Python libraries.
- A health endpoint for basic runtime verification.
- Separation of application dependencies and development tools.
- Repeatable container builds and documented run commands.

The current pipeline is a learning implementation. Additional hardening opportunities include enforcing a strict vulnerability policy, pinning third-party GitHub Actions to verified commit SHAs, improving image provenance, using immutable deployment references, and adding automated deployment health checks.

## Future Enhancements

The next phase can extend this pipeline into a deployment workflow.

Planned improvements include:

1. Deploy the published Docker image to an AWS EC2 instance.
2. Automate deployment after a successful CI/CD run.
3. Configure application health checks on the deployment host.
4. Add rollback handling when a new deployment fails.
5. Introduce environment-specific configuration.
6. Improve image security policies and dependency management.
7. Add deployment status reporting and operational documentation.

These enhancements will build on the existing CI/CD workflow without requiring a complete redesign of the application.

## Key Learnings

Through this phase, I worked with Docker image builds, multi-stage containerization, automated testing, linting, GitHub Actions, Docker Hub authentication, image tagging, and vulnerability scanning.

I also practiced troubleshooting real pipeline and runtime issues, including Docker Hub token permissions, Git synchronization, local credential-helper errors, and host-port conflicts.

The main takeaway is that a successful CI/CD pipeline involves more than building an image. It also requires reliable credentials, traceable artifacts, automated validation, and verification that the published image runs as expected.

## Project Links

- **GitHub repository:** https://github.com/srinivasupolamuri/docker-mastery-project
- **Docker Hub image:** https://hub.docker.com/r/srini9808/docker-mastery-demo
- **Docker Hub tags:** https://hub.docker.com/r/srini9808/docker-mastery-demo/tags

---

*Phase 3 — Advanced Docker and CI/CD Pipeline*

*Project focus: Containerization, CI/CD automation, image publishing, and vulnerability reporting.*
