# frontend-research-design-system Specification

## Purpose

Define the updated Chinese research-terminal design system requirements for all formal frontend pages.

## ADDED Requirements

### Requirement: Frontend SHALL use Chinese-only user-facing copy on formal pages
The system SHALL render all formal application pages with Simplified Chinese user-facing labels, headings, buttons, status text, empty states, error states, and table headers.

#### Scenario: User opens any formal frontend page
- **WHEN** a user opens `/login`, `/`, `/market`, `/backtests`, `/screener`, `/diagnosis`, `/factors`, or `/portfolio`
- **THEN** visible UI copy uses Simplified Chinese and contains no mojibake or unnecessary English labels

#### Scenario: Technical identifiers are displayed
- **WHEN** the UI must display stock codes, API paths, model identifiers, date strings, or accepted finance abbreviations
- **THEN** those identifiers may remain literal while the surrounding label and explanation remain Chinese

### Requirement: Frontend SHALL follow the Chinese research-terminal visual system
The system SHALL implement a unified Chinese research-terminal visual style based on the saved design reference and HTML prototype.

#### Scenario: User moves across major pages
- **WHEN** a user navigates between dashboard, market, backtest, screener, diagnosis, factor, and portfolio pages
- **THEN** the pages share the same navigation language, spacing rhythm, state surfaces, metric cards, tables, and action treatment

#### Scenario: Page renders in mobile viewport
- **WHEN** a formal page is rendered in a mobile viewport
- **THEN** Chinese text, buttons, tables, and state surfaces do not overlap or overflow their containers incoherently

### Requirement: Shared state surfaces SHALL display Chinese workflow states
The system SHALL provide Chinese labels for loading, empty, degraded, error, ready, pending, hit, and miss states.

#### Scenario: Backend response is degraded
- **WHEN** a frontend page receives degraded backend metadata
- **THEN** the shared state surface displays a Chinese degraded label and Chinese explanatory detail
