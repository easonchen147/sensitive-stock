# akquant-runtime-adapter Specification

## Purpose
Define the backend adapter boundary that executes backtests through the official AKQuant runtime while preserving a normalized application contract for APIs and frontend pages.
## Requirements
### Requirement: Backend SHALL execute backtests through an AKQuant runtime adapter
The system SHALL execute backtests through an adapter that invokes the official AKQuant runtime and normalizes the request and response boundaries used by the rest of the application.

#### Scenario: Client submits a supported AKQuant-backed backtest request
- **WHEN** a client submits a supported backtest request through the backend API
- **THEN** the backend invokes the AKQuant runtime through the adapter and returns a normalized response contract to the caller

#### Scenario: AKQuant runtime raises an execution or configuration error
- **WHEN** the underlying AKQuant runtime cannot execute the submitted request because of configuration, strategy, or runtime errors
- **THEN** the adapter returns a structured backend error instead of leaking raw third-party exceptions

### Requirement: AKQuant adapter SHALL provide a migration path for supported legacy fields
The system SHALL provide a bounded compatibility layer that maps supported legacy backtest request fields into the AKQuant-backed internal contract during migration.

#### Scenario: Client submits legacy flat backtest fields
- **WHEN** a client submits a request using supported legacy flat backtest fields
- **THEN** the adapter maps those fields into the AKQuant-backed internal request model before execution

### Requirement: AKQuant adapter SHALL expose advanced execution and risk controls
The AKQuant adapter SHALL map supported structured request fields into AKQuant runtime parameters for volume limits, fee floors, transfer fees, and strategy-level risk controls.

#### Scenario: Client submits advanced execution controls
- **WHEN** a backtest request includes `volumeLimitPct`, `minCommission`, or `transferFeeRate`
- **THEN** the adapter passes those values to AKQuant using the corresponding runtime parameters

#### Scenario: Client submits strategy-level risk controls
- **WHEN** a backtest request includes supported strategy-level risk controls
- **THEN** the adapter passes enabled controls to AKQuant using a stable `signal_replay` strategy ID

### Requirement: AKQuant adapter SHALL collect runtime event summaries
The AKQuant adapter SHALL collect AKQuant stream event summaries for each completed run without leaking raw third-party event objects in the public API.

#### Scenario: AKQuant emits stream events
- **WHEN** AKQuant emits runtime stream events during a backtest
- **THEN** the normalized response includes event counts, warning counts, error counts, and recent event type names

#### Scenario: AKQuant emits no stream events
- **WHEN** AKQuant completes without stream events
- **THEN** the normalized response still includes an `engineEvents` object with zero counts
