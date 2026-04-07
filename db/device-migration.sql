-- Device and Firmware Management Migration
-- Adds tables for tracking IoT devices and firmware deployments

-- Devices table: tracks individual hardware instances
CREATE TABLE IF NOT EXISTS devices (
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
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(project_id, unique_id)
);

-- Firmware versions table: tracks firmware builds and deployments
CREATE TABLE IF NOT EXISTS firmware_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  version text NOT NULL,
  description text,
  binary_url text NOT NULL,
  checksum text,
  size_bytes bigint,
  build_timestamp timestamptz,
  from_commit text,
  is_stable boolean DEFAULT false,
  release_notes text,
  created_by uuid NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(project_id, version)
);

-- Firmware deployments table: tracks which devices have which firmware
CREATE TABLE IF NOT EXISTS firmware_deployments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id uuid NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  firmware_version_id uuid NOT NULL REFERENCES firmware_versions(id) ON DELETE CASCADE,
  status text NOT NULL DEFAULT 'pending',
  deployed_at timestamptz,
  last_error text,
  retry_count integer DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Device telemetry table: stores metrics and health data
CREATE TABLE IF NOT EXISTS device_telemetry (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id uuid NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  timestamp timestamptz NOT NULL DEFAULT now(),
  metric_name text NOT NULL,
  metric_value jsonb NOT NULL,
  tags jsonb
);

-- OTA rollback history: track firmware rollbacks for safety
CREATE TABLE IF NOT EXISTS ota_rollbacks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id uuid NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  from_version uuid REFERENCES firmware_versions(id) ON DELETE SET NULL,
  to_version uuid REFERENCES firmware_versions(id) ON DELETE SET NULL,
  reason text,
  triggered_at timestamptz NOT NULL DEFAULT now(),
  created_by uuid REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_devices_project_id ON devices(project_id);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
CREATE INDEX IF NOT EXISTS idx_firmware_versions_project_id ON firmware_versions(project_id);
CREATE INDEX IF NOT EXISTS idx_firmware_deployments_device_id ON firmware_deployments(device_id);
CREATE INDEX IF NOT EXISTS idx_device_telemetry_device_id ON device_telemetry(device_id);
CREATE INDEX IF NOT EXISTS idx_device_telemetry_timestamp ON device_telemetry(timestamp);
CREATE INDEX IF NOT EXISTS idx_device_telemetry_metric ON device_telemetry(metric_name);
