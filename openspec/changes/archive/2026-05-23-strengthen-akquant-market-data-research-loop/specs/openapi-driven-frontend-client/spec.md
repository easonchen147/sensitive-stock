## ADDED Requirements

### Requirement: Frontend backtest client SHALL use the expanded OpenAPI-backed contract
The frontend SHALL send advanced backtest execution, fee, and risk fields through the existing OpenAPI-backed backend route and SHALL render returned diagnostic sections in Chinese.

#### Scenario: User submits advanced backtest controls
- **WHEN** the user configures advanced execution, fee, or risk values on the回测页面
- **THEN** the frontend payload includes those values in the structured backend request

#### Scenario: Backtest response includes diagnostics
- **WHEN** the backend returns `dataQuality`, `executionQuality`, `riskDiagnostics`, or `engineEvents`
- **THEN** the回测页面 renders the diagnostic information with Chinese labels and without unsupported fake controls

### Requirement: Frontend fallback preset metadata SHALL remain compatible
The frontend fallback preset metadata SHALL remain compatible with the backend execution metadata shape after AKQuant diagnostics are expanded.

#### Scenario: Preset catalog request falls back locally
- **WHEN** the preset catalog request fails and the frontend uses local fallback metadata
- **THEN** the fallback metadata still exposes AKQuant execution modes and risk-control support consistently with the expanded contract
