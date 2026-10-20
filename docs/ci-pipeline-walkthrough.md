# CI/CD Pipeline Walkthrough - Saldes Mobil Churn

**Team:** Golf Team: Marian, Mona & Alicia  
**Course:** Continuous Integration and Delivery (MLOps)  
**Repository:** https://github.com/aliciagez/saldes-mobil-churn-mma

## 1. Overview

Our CI/CD pipeline uses GitHub Actions to automatically test code, validate data, train and evaluate an ML model, and save approved model versions.

The purpose is to prevent incorrect data, broken code and low-quality models from reaching the next stage.

We work with separate branches and pull requests. All changes should be reviewed before merging into `main`.

**Pipeline flow:**

Code tests + Data validation → Model training → Model evaluation → Approved model versioning → Customer call list

Docker packaging and GHCR publishing will be added to the pipeline.

## 2. Workflow Triggers

**File:** `.github/workflows/ci.yml`

The `on` section defines when GitHub Actions starts the pipeline.

- **`push`:** Runs when selected project files change.
- **`pull_request`:** Tests changes in pull requests targeting `main`.
- **`workflow_dispatch`:** Allows us to run the pipeline manually and select a dataset.
- **`schedule`:** Starts the pipeline automatically every Monday at 06:00, Europe/Stockholm.

The `paths` filter limits automatic runs to relevant files, such as Python code, tests, data and workflow files.

**Why?** We want automatic checks when important files change, without unnecessary workflow executions.

### 2.1 Concurrency

**Explanation:**

- `concurrency` controls overlapping workflow executions.
- `github.workflow` identifies the workflow.
- `github.ref` identifies the branch or Git reference.
- `group` combines these values into a unique concurrency group.
- `cancel-in-progress: true` cancels a previous running workflow when another run starts in the same group.

**Example:** If we push another commit to the same branch while CI is still running, the older execution is cancelled and the new one runs.

**Why?** This reduces unnecessary CI resource usage and avoids spending time testing outdated commits.

## 3. Code, Data and Model Tests

**Job:** `test`

We use pytest to test the project on three different Python versions.

- `matrix` creates one test job per Python version.
- `fail-fast: false` allows the other matrix jobs to continue if one fails.
- `runs-on: ubuntu-24.04` specifies the operating system.
- `actions/checkout` downloads the repository code to the runner.
- Our local setup action installs Python and project dependencies.
- `uv run pytest` executes the tests using the project environment.

### Three test levels

**Code/Feature tests `test_features.py`**

Checks that feature engineering works as expected.

**Data tests `test_data.py`**

Checks the expected columns, unique customer IDs and valid target values.

**Model tests `test_model.py`**

Checks prediction output, reproducibility, model quality and performance compared with a simple baseline model.

**Why?** These tests detect errors before model training.

If a required test fails, the `train` job will not start.

## 4. Data Validation

**Job:** `validera_data`  
**File:** `kontroller/schema.py`

We use Pandera to validate incoming customer data.

**Explanation:**

- `uv run python` runs the validation using the project's Python environment.
- `inputs.datafil` uses the dataset selected in a manual workflow run.
- `|| 'data/kundbas.csv'` uses the standard dataset if no file was selected.

### What Pandera checks

- Required columns and expected data types.
- Unique and non-null customer IDs.
- Non-negative age, costs, data usage and support cases.
- Valid target values (`avslutat` must be 0 or 1).
- Required fields must not contain missing values.

### Two datasets

- `kundbas.csv` expected to pass validation.
- `kundbas_ny_leverans.csv` expected to fail validation.

When validation fails, Pandera raises an error and GitHub Actions marks the job as failed.

**Why?** Incorrect data must be detected before model training.

The normal tests and data validation can run in parallel. The training job waits for both to succeed.

## 5. Job Dependencies `needs`

`needs` defines dependencies between jobs.

Here, `train` depends on both `test` and `validera_data`.

Training can only start after both jobs complete successfully.

The later jobs follow the same principle:

- `utvardera` depends on `train`.
- `versionera_modell` depends on `utvardera`.
- `ringlista` depends on `versionera_modell`.

**Why?** This ensures that failed tests, invalid datasets and models that do not pass evaluation cannot continue through the dependent pipeline jobs.

## 6. Model Training

**Job:** `train`  
**File:** `src/churn/model.py`

The training job starts only after the tests and data validation have passed.

The project uses a scikit-learn pipeline with preprocessing and logistic regression.

The dataset is split into training and test data using a fixed random seed.

### Files created

**`outputs/modell.joblib`**

Contains the trained ML model.

**`outputs/matvarden.json`**

Contains:

- `roc_auc` model discrimination performance.
- `accuracy` proportion of correct predictions.
- `commit` Git commit SHA.
- `datafil` dataset filename.
- `data_sha256` SHA256 hash of the training data.

### Upload artifact

**Explanation:**

- `upload-artifact` saves files from a workflow job.
- `github.sha` identifies the commit associated with the workflow run.
- `path: outputs/` specifies which files are uploaded.

**Why?** GitHub Actions jobs run in separate environments. The artifact allows later jobs to access the trained model and its metrics.

This first artifact is a training artifact, not yet the final approved model version.

## 7. Model Evaluation

**Job:** `utvardera`  
**File:** `src/churn/evaluate.py`

The evaluation job downloads the training artifact:

`download-artifact` retrieves files uploaded by an earlier job.

The job then runs:
uv run python -m churn.evaluate

### Quality threshold

The model must achieve:

**ROC AUC ≥ 0.70**

ROC AUC measures how well the model distinguishes between customers who leave and customers who stay.

- A value close to 0.5 indicates approximately random ranking.
- A value closer to 1.0 indicates better discrimination.

The threshold is defined in `evaluate.py` and can be overridden using the `MIN_ROC_AUC` environment variable.

If the model performs below the threshold, the script returns exit code 1.

GitHub Actions then marks the job as failed.

**Why?** Only models meeting the minimum quality requirement should be approved.

### 7.1 GitHub Actions Summary

**Explanation:**

- `name` gives the step a readable name in GitHub Actions.
- `run: |` allows multiple shell commands.
- `echo` writes headings and JSON code-block formatting.
- `cat outputs/matvarden.json` reads the metrics file.
- `>>` appends text to a file.
- `$GITHUB_STEP_SUMMARY` is a special GitHub Actions file used to display formatted results on the workflow run's Summary page.

**Why?** We can inspect ROC AUC, accuracy and traceability information directly in GitHub Actions without downloading the artifact.

## 8. Model Versioning

**Job:** `versionera_modell`

This job depends on successful model evaluation:
needs: utvardera

It downloads the validated training artifact into `approved-model/` and uploads it under a new name:

`approved-modell-${{ github.sha }}`

### What is included?

- Trained model (`modell.joblib`).
- Evaluation metrics (`matvarden.json`).
- Git commit SHA.
- Training data SHA256 hash.

**Why?** We can identify the exact code and data used to create a model.

The job only runs when model evaluation succeeds.

This separates the training artifact from the approved model version.

### Important distinction

The artifact name contains the commit SHA, while the data hash is stored in the metadata.

The model can be traced back to the source code and training data.

A GitHub Actions artifact is a stored workflow output, not a full model registry such as MLflow.

## 9. Reproducibility and Dependency Management

**File:** `.github/actions/setup/action.yml`

We use a reusable composite action to prepare the Python environment.

This avoids repeating the same installation commands in every job.

### Version pinning

- Ubuntu runner: `ubuntu-24.04`.
- Python test versions: 3.11, 3.12 and 3.13.
- Python runtime for training and evaluation: 3.11.
- GitHub Actions: specified action versions.
- `setup-uv`: pinned to a specific commit SHA.

### Why pin versions?

Using fixed versions reduces unexpected changes between workflow runs and improves reproducibility.

A commit SHA identifies one exact revision of a GitHub Action.

Version tags such as `@v4` or `@v7` specify a version series but are not as strictly pinned as full commit SHAs.

### Python dependencies

uv sync --frozen --extra dev

**Explanation:**

- `uv sync` creates or synchronizes the project's Python environment.
- `--frozen` uses the existing lockfile without updating it.
- `--extra dev` includes development dependencies such as pytest.

The file `uv.lock` records resolved dependency versions.

### Running commands

uv run pytest
uv run python -m churn.model
uv run python -m churn.evaluate

`uv run` executes the commands in the project's managed environment.

### Caching

We enable caching in `setup-uv`.

This allows downloaded dependencies to be reused in later workflow runs when the cache is available.

**Why?** Caching can reduce repeated dependency downloads and improve CI performance.

## 10. Customer Call List

**Job:** `ringlista`

The job runs after approved model versioning succeeds.
if: github.ref == 'refs/heads/main' && github.event_name != 'pull_request'

**Explanation:**

- `if` defines a condition for running the job.
- `github.ref == 'refs/heads/main'` requires the `main` branch.
- `github.event_name != 'pull_request'` excludes pull request events.
- `&&` means both conditions must be true.

The job downloads the trained model artifact and runs:
uv run python -m churn.score

This generates `outputs/ringlista.csv`, containing customers selected for follow-up based on the model's predictions.

The ring list is uploaded as a GitHub Actions artifact.

**Why?** It shows how an approved ML model can produce a business output, while preventing call-list generation during pull request checks.

## 11. Docker and Smoke Test

**Status: TODO Awaiting Alicia's Docker implementation**

This section will explain:

- Which base image we use.
- How the Dockerfile installs dependencies.
- How the approved model is included.
- How the Docker image is built.
- How the smoke test verifies that the model works inside the container.
- What happens if the smoke test fails.

**Why?** A smoke test checks that the packaged application works at a basic level before publication.

## 12. GitHub Container Registry (GHCR)

**Status: TODO Awaiting GHCR implementation**

This section will describe:

- How Docker images are tagged.
- How GitHub Actions authenticates to GHCR.
- Which permissions are required.
- How the tested image is published.
- How the image can be traced to the approved model and commit.

**Why?** GHCR stores the Docker image so it can later be downloaded and deployed.

## 13. Pull Requests and Branch Protection

We work with separate branches instead of pushing directly to `main`.

Our process is:

1. Create or select a GitHub Issue.
2. Create a branch.
3. Make and test changes.
4. Push the branch.
5. Create a pull request.
6. Run GitHub Actions checks.
7. Request a review from another team member.
8. Merge after approval and successful required checks.

### Why use pull requests?

Pull requests allow team members to review code before changes are integrated.

Branch protection helps prevent unreviewed or failing changes from reaching `main`.

### Important GitHub expressions

- `${{ github.sha }}` commit identifier for the workflow run.
- `${{ github.ref }}` branch or Git reference.
- `${{ matrix.python-version }}` Python version for the current matrix job.
- `${{ inputs.datafil }}` manually selected dataset.
- `needs` defines job dependencies.
- `with` passes inputs to an action.
- `uses` runs a GitHub Action.
- `run` executes shell commands.
- `if` controls whether a job or step runs.

## 14. Demonstration

During the demonstration, we will show:

- A successful GitHub Actions run.
- A failed run where Pandera rejects invalid data.
- The job dependency structure.
- Model training and evaluation metrics.
- The ROC AUC quality threshold.
- Approved model artifacts and traceability metadata.
- The final Docker image and smoke test.
- The GHCR publication.
- Our pull requests and code reviews.
- How we used AI and verified suggested changes.

We will also be prepared to explain what happens when each stage fails.

## 15. Conclusion

Our CI/CD pipeline automates the validation and testing of code, data and machine learning models.

Job dependencies prevent failed validation or low-quality models from progressing.

Version pinning, dependency locking and caching support reproducibility and efficient resource usage.

Model artifacts preserve traceability through commit identifiers and data hashes.

Docker and GHCR will complete the model packaging and publication stages.

The overall goal is to create a reliable and maintainable MLOps workflow.