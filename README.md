# MedAppoint

A patient appointment management API, deployed to Azure with a fully automated CI/CD pipeline.

## Stack

- **App**: Python/Flask + SQLAlchemy, containerized with Docker (`app/`)
- **Infrastructure**: Terraform on Azure (`terraform/`) — resource group, Azure Container Registry, AKS cluster, Postgres Flexible Server, remote state in Azure Blob Storage
- **Runtime**: Kubernetes manifests for AKS (`k8s/`) — Deployment + LoadBalancer Service
- **CI/CD**: Azure DevOps Pipeline (`azure-pipelines.yml`), source hosted on GitHub

## Pipeline

Triggered on every push/PR to `main`, three stages:

1. **Terraform** — `init` / `validate` / `plan` always; `apply` only when running on `main`. Publishes DB connection details and the ACR login server as pipeline outputs for later stages.
2. **Build & Push** — `az acr build` builds the Docker image directly in ACR and tags it with both `latest` and the build ID. Runs only on `main`.
3. **Deploy to AKS** — fetches AKS credentials, creates/updates the `medappoint-db-secret` from the Terraform DB outputs, injects the freshly built image tag into `k8s/deployment.yaml`, applies the manifests, and waits for rollout.

## Local development

```bash
cd app
python -m venv .venv && . .venv/Scripts/activate
pip install -r requirements.txt
python app.py   # serves on :5000 against sqlite:///local_dev.db by default
```

## Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

State is stored remotely in the `medappoint-tfstate-rg` / `medappointtfstate123` storage account — never commit `*.tfstate` (already gitignored).

## Prerequisites for the pipeline

- Azure DevOps service connection `moath-sp-new` (Azure Resource Manager, scoped to the target subscription)
- GitHub service connection authorizing the Azure DevOps project to read this repo
- Environment `medappoint-production` (auto-created on first deploy; add an approval check on it to require manual sign-off before deploys)
