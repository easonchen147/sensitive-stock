## ADDED Requirements

### Requirement: Shared market data contracts SHALL support screener, diagnosis, factor, and portfolio workflows
The system SHALL make AkShare-first market data contracts reusable across screening, diagnosis, factor analysis, and portfolio optimization workflows so all research capabilities consume consistent normalized market inputs.

#### Scenario: Research workflow requests normalized market history
- **WHEN** a screener, diagnosis, factor-analysis, or portfolio workflow requests A-share market data
- **THEN** the system resolves the request through the shared normalized market-data contract instead of introducing a workflow-specific ad hoc data shape
