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
