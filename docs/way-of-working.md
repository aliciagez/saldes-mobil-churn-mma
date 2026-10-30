# Way of Working – Golf Team

**Project:** Saldes Mobil Churn  
**Team:** Marian, Mona & Alicia

## Task Management
- We use Tabula as our main project management tool.
- Each task has an assigned team member.
- Tasks move through To Do → In Progress → In Review → Done.
- GitHub Issues are optional.

## Git Workflow
- We create separate branches from `main` for development tasks.
- All changes are submitted through pull requests.
- We link pull requests to the corresponding Tabula cards.
- The `main` branch is protected.
- Pull requests require approval from another team member before merging.

## Quality Assurance
- GitHub Actions automatically runs CI checks.
- We use pytest for automated testing.
- Pandera validates data before model training.
- Failed required checks must be resolved before merging.

## Collaboration
- We communicate through our group chat and meetings.
- Each team member is responsible for their assigned tasks.
- We help each other troubleshoot problems.
- Everyone participates in code reviews and the final demonstration.

## Definition of Done
A task is complete when:
- [ ] Implementation is finished.
- [ ] Relevant tests pass.
- [ ] Pull request is reviewed and approved.
- [ ] Changes are merged into `main`.
- [ ] Tabula card is moved to Done.