# frontend-research-design-system Specification

## Purpose
Define the shared frontend research-workbench design system, including page hierarchy, layout grammar, workflow state surfaces, and the Quiet Capital Terminal visual direction.

## Requirements
### Requirement: Frontend SHALL use a unified research-workbench design system
The system SHALL provide a unified design system for research workbench pages so stock-research workflows share the same hierarchy, layout grammar, and state language across the application.

#### Scenario: User moves between major workbench pages
- **WHEN** a user moves between the dashboard, backtest, market, screener, diagnosis, factor, or portfolio pages
- **THEN** the pages share a consistent layout grammar for summary, controls, results, and explanation areas instead of behaving like unrelated standalone screens

### Requirement: Frontend SHALL provide shared state surfaces for data workflows
The system SHALL provide shared loading, empty, degraded, error, and ready-state surfaces so data-driven workbench pages express status consistently.

#### Scenario: Backend request is degraded
- **WHEN** a frontend page receives degraded metadata from the backend
- **THEN** the page renders the shared degraded-state surface with context instead of inventing a page-specific improvised status treatment
