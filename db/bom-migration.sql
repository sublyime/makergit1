-- BOM (Bill of Materials) Management Migration
-- Adds tables for component BOMs, variants, and supplier management

-- Component library: Global component catalog for knowledge base
CREATE TABLE IF NOT EXISTS component_library (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  part_number text NOT NULL UNIQUE,
  manufacturer text,
  name text NOT NULL,
  category text NOT NULL,
  description text,
  datasheet_url text,
  pinout_diagram_url text,
  specifications jsonb,
  package_type text,
  supplier_links jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- BOM (Bill of Materials): Project-specific BOMs
CREATE TABLE IF NOT EXISTS boms (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  device_id uuid REFERENCES devices(id) ON DELETE SET NULL,
  version text NOT NULL DEFAULT '1.0.0',
  name text NOT NULL,
  description text,
  estimated_cost numeric(12,2),
  is_locked boolean DEFAULT false,
  parent_bom_id uuid REFERENCES boms(id) ON DELETE SET NULL,
  created_by uuid NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(project_id, version)
);

-- BOM items: Individual components in a BOM
CREATE TABLE IF NOT EXISTS bom_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bom_id uuid NOT NULL REFERENCES boms(id) ON DELETE CASCADE,
  component_library_id uuid REFERENCES component_library(id) ON DELETE SET NULL,
  reference text NOT NULL,
  description text NOT NULL,
  part_number text,
  manufacturer text,
  quantity integer NOT NULL DEFAULT 1,
  unit_price numeric(10,4),
  supplier text,
  supplier_url text,
  lead_time_days integer,
  datasheet_url text,
  notes text,
  custom_fields jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Component variants: Track component swaps and alternatives
CREATE TABLE IF NOT EXISTS component_variants (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bom_id uuid NOT NULL REFERENCES boms(id) ON DELETE CASCADE,
  original_item_id uuid NOT NULL REFERENCES bom_items(id) ON DELETE CASCADE,
  variant_name text NOT NULL,
  alternative_part_number text NOT NULL,
  alternative_manufacturer text,
  reason_for_variant text,
  cost_delta numeric(10,4),
  performance_impact text,
  availability_status text,
  created_by uuid NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- BOM snapshots: Track BOMs over time for revisions
CREATE TABLE IF NOT EXISTS bom_revisions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  bom_id uuid NOT NULL REFERENCES boms(id) ON DELETE CASCADE,
  revision_number integer NOT NULL,
  snapshot_data jsonb NOT NULL,
  total_cost numeric(12,2),
  created_by uuid NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(bom_id, revision_number)
);

-- Supplier tracking
CREATE TABLE IF NOT EXISTS suppliers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  website text,
  contact_email text,
  lead_time_days integer,
  shipping_cost numeric(10,2),
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_component_library_part_number ON component_library(part_number);
CREATE INDEX IF NOT EXISTS idx_component_library_category ON component_library(category);
CREATE INDEX IF NOT EXISTS idx_boms_project_id ON boms(project_id);
CREATE INDEX IF NOT EXISTS idx_boms_device_id ON boms(device_id);
CREATE INDEX IF NOT EXISTS idx_bom_items_bom_id ON bom_items(bom_id);
CREATE INDEX IF NOT EXISTS idx_bom_items_component_library_id ON bom_items(component_library_id);
CREATE INDEX IF NOT EXISTS idx_component_variants_bom_id ON component_variants(bom_id);
CREATE INDEX IF NOT EXISTS idx_bom_revisions_bom_id ON bom_revisions(bom_id);
