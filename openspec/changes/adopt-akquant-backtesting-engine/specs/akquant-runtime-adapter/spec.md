## ADDED Requirements

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
