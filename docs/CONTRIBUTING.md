# FairLens AI – Collaboration Protocol & Workflow

## Collaboration Protocol
The implementation must be iterative. Do not attempt to build the entire application in a single response.
For every milestone:
1. Present a concise implementation plan.
2. Explain key architectural decisions.
3. List all files that will be created or modified.
4. Implement only the agreed scope.
5. Run linting, formatting, and tests before considering the milestone complete.
6. Summarize what was completed and list remaining work.
7. Wait for approval before proceeding to the next milestone.
*Never skip milestones or merge unfinished work into later phases.*

## Agent Constraints
- Never rewrite working code unless required.
- Never rename public APIs without updating all consumers.
- Never introduce a dependency without justification.
- Prefer extending existing modules over creating duplicates.
- Preserve backward compatibility within a phase.
- Keep pull requests small and reviewable.

## Deliverables & Documentation Requirements
### Per Milestone Deliverables
- Working source code, Passing tests, Updated documentation, Docker support, Database migrations (if applicable), Screenshots of the implemented UI, Conventional Commit message.
### Documentation Requirement
- Every completed milestone must update: `README.md`, `CHANGELOG.md`, Architecture documentation, API documentation, Installation guide (if changed).

## Final Validation Checklist
Before declaring the project complete, verify:
- All milestones are complete.
- Every acceptance criterion is satisfied.
- Every endpoint is documented.
- No placeholder code remains.
- No lint or type errors exist.
- Test coverage targets are met.
- Docker Compose starts the complete application.
- A new developer can clone the repository and run the project using only the documented setup steps.
