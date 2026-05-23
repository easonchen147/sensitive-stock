# nextjs-frontend-shell Specification

## Purpose

Define the frontend shell and page-level behavior updates required for the Chinese research terminal and prediction-loop UI.

## ADDED Requirements

### Requirement: Application shell SHALL use Chinese navigation and status language
The Next.js application shell SHALL render Chinese brand, navigation, page context, status chips, and authentication controls across all protected pages.

#### Scenario: Authenticated user opens the shell
- **WHEN** an authenticated user opens any protected page
- **THEN** navigation entries, current page context, status chips, and auth controls are displayed in Chinese
- **AND** the shell uses runtime product states rather than migration labels

### Requirement: Market page SHALL provide prediction detail, history, and evaluation areas
The market workbench SHALL render prediction rows together with selectable detail, recent prediction history, source-quality scoring, DeepSeek mode metadata, evaluation summary, and backtest handoff information.

#### Scenario: Prediction response includes a run id
- **WHEN** the market prediction endpoint returns `runId`
- **THEN** the market workbench displays the run id in Chinese context and can load that run from the prediction-detail endpoint

#### Scenario: Prediction history returns runs
- **WHEN** the market page loads prediction history
- **THEN** it displays recent runs with Chinese model, source-quality, degraded, and evaluation labels

#### Scenario: Evaluation endpoint returns mixed statuses
- **WHEN** a prediction run evaluation contains hit, miss, neutral, and pending rows
- **THEN** the market page renders those statuses in Chinese without treating pending rows as failures

### Requirement: Backtest and research workbenches SHALL use Chinese form and result labels
Backtest, screener, diagnosis, factor, and portfolio pages SHALL render all form labels, button labels, result headers, table headers, and empty/error states in Chinese.

#### Scenario: User opens a research workbench
- **WHEN** a user opens `/backtests`, `/screener`, `/diagnosis`, `/factors`, or `/portfolio`
- **THEN** the page uses Chinese labels for controls, results, metadata, and actions
