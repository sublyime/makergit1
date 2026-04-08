-- MakerGit database schema for PostgreSQL
-- Database: makergit

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  username text NOT NULL UNIQUE,
  password_hash text NOT NULL,
  api_key text UNIQUE,
  display_name text,
  email text UNIQUE,
  bio text,
  avatar_url text,
  website_url text,
  location text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE projects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title text NOT NULL,
  slug text NOT NULL UNIQUE,
  summary text,
  description text,
  cover_image_url text,
  visibility text NOT NULL DEFAULT 'public',
  status text NOT NULL DEFAULT 'planning',
  estimated_cost numeric(12,2),
  difficulty_level text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE project_revisions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  version_label text NOT NULL,
  changelog text,
  metadata_snapshot jsonb,
  published_at timestamptz,
  created_by uuid NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE project_metadata (
  project_id uuid PRIMARY KEY REFERENCES projects(id) ON DELETE CASCADE,
  platform text,
  category text,
  connectivity text,
  power_source text,
  firmware_language text,
  hardware_tags text[],
  custom_fields jsonb
);

CREATE TABLE components (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  revision_id uuid REFERENCES project_revisions(id) ON DELETE SET NULL,
  name text NOT NULL,
  part_number text,
  quantity integer NOT NULL DEFAULT 1,
  supplier text,
  category text,
  url text,
  notes text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE attachments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  revision_id uuid REFERENCES project_revisions(id) ON DELETE SET NULL,
  type text NOT NULL,
  filename text NOT NULL,
  url text NOT NULL,
  mime_type text,
  size_bytes bigint,
  uploaded_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE build_log_entries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  revision_id uuid REFERENCES project_revisions(id) ON DELETE SET NULL,
  title text NOT NULL,
  body text,
  entry_date date NOT NULL DEFAULT CURRENT_DATE,
  created_by uuid NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE discussion_threads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  title text NOT NULL,
  body text,
  created_by uuid NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  status text NOT NULL DEFAULT 'open',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE comments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  build_log_entry_id uuid REFERENCES build_log_entries(id) ON DELETE CASCADE,
  discussion_thread_id uuid REFERENCES discussion_threads(id) ON DELETE CASCADE,
  parent_comment_id uuid REFERENCES comments(id) ON DELETE CASCADE,
  author_id uuid NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  body text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  resolved_at timestamptz
);

CREATE TABLE tags (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  category text
);

CREATE TABLE project_tags (
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  tag_id uuid NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (project_id, tag_id)
);

CREATE TABLE favorites (
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, project_id)
);

CREATE TABLE follows (
  follower_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  followee_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (follower_id, followee_id)
);

CREATE TABLE device_templates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text,
  hardware_profile jsonb,
  recommended_components jsonb,
  default_config jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Device Library Table (for autocomplete/search)
CREATE TABLE device_library (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  version text,
  author text,
  category text,
  architectures text[],
  types text[],
  description text,
  repository text,
  website text,
  keywords text[],
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Component Library Table (for autocomplete/search in BOM)
CREATE TABLE component_library (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  part_number text NOT NULL UNIQUE,
  category text,
  manufacturer text,
  description text,
  datasheet_url text,
  pinout_diagram_url text,
  specifications jsonb,
  package_type text,
  keywords text[],
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Devices Table (for project device management)
CREATE TABLE devices (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  unique_id text NOT NULL,
  name text NOT NULL,
  device_type text NOT NULL,
  status text NOT NULL DEFAULT 'offline',
  last_seen timestamptz,
  ip_address text,
  mac_address text,
  firmware_version text,
  config jsonb,
  metadata jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Bill of Materials Table
CREATE TABLE boms (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name text NOT NULL,
  description text,
  revision text DEFAULT '1.0',
  total_cost numeric(12,2),
  currency text DEFAULT 'USD',
  created_by uuid NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- BOM Items Table
CREATE TABLE bom_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bom_id uuid NOT NULL REFERENCES boms(id) ON DELETE CASCADE,
  component_id uuid REFERENCES component_library(id) ON DELETE SET NULL,
  reference_designator text,
  quantity integer NOT NULL DEFAULT 1,
  unit_cost numeric(10,2),
  supplier text,
  supplier_sku text,
  notes text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE telemetry_snapshots (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  timestamp timestamptz NOT NULL DEFAULT now(),
  data jsonb NOT NULL,
  device_status text
);

CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_project_revisions_project_id ON project_revisions(project_id);
CREATE INDEX idx_components_project_id ON components(project_id);
CREATE INDEX idx_attachments_project_id ON attachments(project_id);
CREATE INDEX idx_build_log_entries_project_id ON build_log_entries(project_id);
CREATE INDEX idx_comments_project_id ON comments(project_id);
CREATE INDEX idx_project_tags_tag_id ON project_tags(tag_id);
CREATE INDEX idx_telemetry_snapshots_project_id ON telemetry_snapshots(project_id);

-- Library search indexes
CREATE INDEX idx_device_library_name ON device_library USING GIN(to_tsvector('english', name));
CREATE INDEX idx_device_library_category ON device_library(category);
CREATE INDEX idx_component_library_name ON component_library USING GIN(to_tsvector('english', name));
CREATE INDEX idx_component_library_part_number ON component_library(part_number);
CREATE INDEX idx_component_library_category ON component_library(category);
CREATE INDEX idx_component_library_keywords ON component_library USING GIN(keywords);

-- Device and BOM indexes
CREATE INDEX idx_devices_project_id ON devices(project_id);
CREATE INDEX idx_devices_name ON devices(name);
CREATE INDEX idx_boms_project_id ON boms(project_id);
CREATE INDEX idx_bom_items_bom_id ON bom_items(bom_id);
CREATE INDEX idx_bom_items_component_id ON bom_items(component_id);
