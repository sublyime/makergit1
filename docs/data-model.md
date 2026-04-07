# MakerGit Data Model

## Core entities

- `users`
  - user profile and account metadata
- `projects`
  - maker project definition and current state
- `project_revisions`
  - published iterations or build revisions
- `project_metadata`
  - structured IoT and hardware metadata
- `components`
  - BOM items and part details
- `attachments`
  - screenshots, firmware, schematics, and documents
- `build_log_entries`
  - progress updates and maker journal posts
- `discussion_threads`
  - project-level discussions
- `comments`
  - threaded comments and replies
- `tags`
  - discovery and categorical labels
- `project_tags`
  - project/tag relationship
- `favorites`
  - starred projects
- `follows`
  - user connections
- `telemetry_snapshots`
  - optional IoT status payloads

## Notes

The schema is designed to separate the live project record from revision history while keeping a flexible metadata layer for maker-specific attributes.
