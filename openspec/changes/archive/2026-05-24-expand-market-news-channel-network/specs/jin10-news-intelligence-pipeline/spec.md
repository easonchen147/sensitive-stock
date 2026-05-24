## MODIFIED Requirements

### Requirement: Market news intelligence SHALL aggregate multiple news channels
The system SHALL preserve the existing Jin10 realtime ingestion path while also
fetching additional market news channels, normalizing items into the shared
market-news shape, deduplicating repeated stories, and returning per-channel
status, source-quality, and dedupe metadata. The default configured extra
channels SHALL include Eastmoney stock news, Sina finance live feed, CLS
telegraph page items, STCN article headlines, and 21st Century Business Herald
capital-market headlines when those sources are reachable.

#### Scenario: Multiple channels return overlapping stories
- **WHEN** Jin10 and another configured market news channel return the same or substantially similar story
- **THEN** the intelligence payload contains one normalized story, channel metadata that records which channels were queried, `sourceQuality.duplicateItems`, and `dedupeMetadata.duplicateCount`

#### Scenario: One non-primary channel fails
- **WHEN** one additional market news channel fails while at least one other channel succeeds
- **THEN** the news payload still succeeds, marks the response as degraded, includes warning metadata for the failed channel, and increments `sourceQuality.failedChannels`

#### Scenario: CLS telegraph page is reachable
- **WHEN** the CLS telegraph page can be fetched successfully
- **THEN** the aggregation layer parses page-embedded structured telegraph data and includes normalized CLS items in the merged news payload

#### Scenario: HTML headline sources are reachable
- **WHEN** the STCN homepage or 21st Century Business Herald capital channel page can be fetched successfully
- **THEN** the aggregation layer extracts article headlines and links from the page HTML and includes normalized items in the merged news payload

#### Scenario: A low-quality public RSS feed is currently unusable
- **WHEN** a candidate public RSS feed returns stale, blank, or obviously mis-decoded content during integration review
- **THEN** the system does not add that feed as a default formal source until a stable parse path is available

#### Scenario: One newly added page source fails
- **WHEN** CLS, STCN, or 21st Century Business Herald fails while at least one other news source succeeds
- **THEN** the aggregated news payload still succeeds, marks the response as degraded, records the failed channel in `channels`, and appends a warning explaining the failure
