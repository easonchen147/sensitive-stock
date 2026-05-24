## ADDED Requirements

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
