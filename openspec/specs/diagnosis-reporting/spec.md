# diagnosis-reporting Specification

## Purpose
Define the structured stock diagnosis workflow, including market context, indicator summaries, narrative sections, risk notes, and graceful degraded output.

## Requirements
### Requirement: Diagnosis reporting SHALL generate structured stock diagnosis reports
The system SHALL provide a diagnosis workflow that accepts a symbol and returns a structured report composed of market facts, technical indicators, risk notes, and narrative conclusions.

#### Scenario: User requests a diagnosis for a valid symbol
- **WHEN** a client submits a diagnosis request for a supported A-share symbol
- **THEN** the system returns a structured report containing symbol metadata, latest market context, indicator summaries, diagnosis sections, and risk notes

### Requirement: Diagnosis reporting SHALL degrade gracefully when model or context inputs fail
The system SHALL return a usable partial report or structured error metadata when market context, indicator generation, or model output cannot be fully produced.

#### Scenario: Market context is partially unavailable
- **WHEN** a diagnosis request cannot obtain one or more non-critical market context inputs
- **THEN** the system returns a degraded report with available sections plus metadata that explains what inputs were unavailable

#### Scenario: Diagnosis model output fails
- **WHEN** a diagnosis request cannot complete the narrative generation stage
- **THEN** the system returns a structured failure or degraded response instead of an unbounded raw exception
