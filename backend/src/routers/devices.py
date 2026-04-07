from fastapi import APIRouter, Depends, HTTPException, Request, status
from datetime import datetime
import json
from ..database import get_pool
from ..models import (
    DeviceCreate, DeviceRead, DeviceUpdate,
    FirmwareVersionCreate, FirmwareVersionRead,
    TelemetryDataCreate, TelemetryDataRead,
    DeviceHealthRead
)
from ..utils import get_current_user

router = APIRouter()

# ===== DEVICE MANAGEMENT =====

@router.post("/devices", response_model=DeviceRead)
async def register_device(
    project_id: str,
    device: DeviceCreate,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Register a new device to a project"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify user owns the project
        project = await conn.fetchrow(
            "SELECT owner_id FROM projects WHERE id = $1",
            project_id
        )
        if not project or project['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add devices to this project"
            )
        
        # Register device
        row = await conn.fetchrow(
            """
            INSERT INTO devices(project_id, unique_id, name, device_type, status, config, metadata)
            VALUES($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, project_id, unique_id, name, device_type, status, last_seen, ip_address, 
                      mac_address, firmware_version, config, metadata, created_at, updated_at
            """,
            project_id, device.unique_id, device.name, device.device_type,
            'offline', json.dumps(device.config) if device.config else json.dumps({}), json.dumps(device.metadata) if device.metadata else json.dumps({})
        )
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        row_dict['project_id'] = str(row_dict['project_id'])
        # Deserialize JSON fields
        if isinstance(row_dict.get('config'), str):
            row_dict['config'] = json.loads(row_dict['config'])
        if isinstance(row_dict.get('metadata'), str):
            row_dict['metadata'] = json.loads(row_dict['metadata'])
        return DeviceRead(**row_dict)

@router.get("/devices")
async def list_devices(
    project_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    """List all devices for a project"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify user owns the project
        project = await conn.fetchrow(
            "SELECT owner_id FROM projects WHERE id = $1",
            project_id
        )
        if not project or project['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view devices for this project"
            )
        
        rows = await conn.fetch(
            """
            SELECT id, project_id, unique_id, name, device_type, status, last_seen, ip_address,
                   mac_address, firmware_version, config, metadata, created_at, updated_at
            FROM devices WHERE project_id = $1 ORDER BY created_at DESC
            """,
            project_id
        )
        
        devices = []
        for row in rows:
            row_dict = dict(row)
            row_dict['id'] = str(row_dict['id'])
            row_dict['project_id'] = str(row_dict['project_id'])
            # Deserialize JSON fields
            if isinstance(row_dict.get('config'), str):
                row_dict['config'] = json.loads(row_dict['config'])
            if isinstance(row_dict.get('metadata'), str):
                row_dict['metadata'] = json.loads(row_dict['metadata'])
            devices.append(DeviceRead(**row_dict))
        
        return devices

@router.get("/devices/{device_id}", response_model=DeviceRead)
async def get_device(
    device_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Get device details"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT d.id, d.project_id, d.unique_id, d.name, d.device_type, d.status, 
                   d.last_seen, d.ip_address, d.mac_address, d.firmware_version, 
                   d.config, d.metadata, d.created_at, d.updated_at
            FROM devices d
            JOIN projects p ON d.project_id = p.id
            WHERE d.id = $1 AND p.owner_id = $2
            """,
            device_id, current_user['id']
        )
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        row_dict['project_id'] = str(row_dict['project_id'])
        return DeviceRead(**row_dict)

@router.put("/devices/{device_id}", response_model=DeviceRead)
async def update_device(
    device_id: str,
    update: DeviceUpdate,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Update device metadata"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify ownership
        row = await conn.fetchrow(
            """
            SELECT d.id FROM devices d
            JOIN projects p ON d.project_id = p.id
            WHERE d.id = $1 AND p.owner_id = $2
            """,
            device_id, current_user['id']
        )
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Build update query
        updates = []
        params = []
        param_idx = 1
        
        if update.name is not None:
            updates.append(f"name = ${param_idx}")
            params.append(update.name)
            param_idx += 1
        if update.status is not None:
            updates.append(f"status = ${param_idx}")
            params.append(update.status)
            param_idx += 1
        if update.firmware_version is not None:
            updates.append(f"firmware_version = ${param_idx}")
            params.append(update.firmware_version)
            param_idx += 1
        if update.ip_address is not None:
            updates.append(f"ip_address = ${param_idx}")
            params.append(update.ip_address)
            param_idx += 1
        if update.config is not None:
            updates.append(f"config = ${param_idx}")
            params.append(update.config)
            param_idx += 1
        
        updates.append(f"updated_at = now()")
        params.append(device_id)
        
        query = f"""
            UPDATE devices
            SET {', '.join(updates)}
            WHERE id = ${param_idx}
            RETURNING id, project_id, unique_id, name, device_type, status, last_seen,
                      ip_address, mac_address, firmware_version, config, metadata, created_at, updated_at
        """
        
        row = await conn.fetchrow(query, *params)
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        row_dict['project_id'] = str(row_dict['project_id'])
        return DeviceRead(**row_dict)

@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Delete a device"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify ownership
        row = await conn.fetchrow(
            """
            SELECT d.id FROM devices d
            JOIN projects p ON d.project_id = p.id
            WHERE d.id = $1 AND p.owner_id = $2
            """,
            device_id, current_user['id']
        )
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        await conn.execute("DELETE FROM devices WHERE id = $1", device_id)

# ===== FIRMWARE MANAGEMENT =====

@router.post("/firmware", response_model=FirmwareVersionRead)
async def upload_firmware(
    project_id: str,
    firmware: FirmwareVersionCreate,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Upload a new firmware version"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify user owns the project
        project = await conn.fetchrow(
            "SELECT owner_id FROM projects WHERE id = $1",
            project_id
        )
        if not project or project['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to upload firmware for this project"
            )
        
        row = await conn.fetchrow(
            """
            INSERT INTO firmware_versions(
                project_id, version, description, binary_url, checksum, 
                size_bytes, from_commit, is_stable, release_notes, created_by, build_timestamp
            )
            VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, now())
            RETURNING id, project_id, version, description, binary_url, checksum,
                      size_bytes, build_timestamp, from_commit, is_stable, release_notes, created_by, created_at
            """,
            project_id, firmware.version, firmware.description, firmware.binary_url,
            firmware.checksum, firmware.size_bytes, firmware.from_commit, 
            firmware.is_stable, firmware.release_notes, str(current_user['id'])
        )
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        row_dict['project_id'] = str(row_dict['project_id'])
        row_dict['created_by'] = str(row_dict['created_by'])
        return FirmwareVersionRead(**row_dict)

@router.get("/firmware", response_model=list)
async def list_firmware_versions(
    project_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    """List all firmware versions for a project"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify user owns the project
        project = await conn.fetchrow(
            "SELECT owner_id FROM projects WHERE id = $1",
            project_id
        )
        if not project or project['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view firmware for this project"
            )
        
        rows = await conn.fetch(
            """
            SELECT id, project_id, version, description, binary_url, checksum,
                   size_bytes, build_timestamp, from_commit, is_stable, release_notes, created_by, created_at
            FROM firmware_versions WHERE project_id = $1 ORDER BY created_at DESC
            """,
            project_id
        )
        
        versions = []
        for row in rows:
            row_dict = dict(row)
            row_dict['id'] = str(row_dict['id'])
            row_dict['project_id'] = str(row_dict['project_id'])
            row_dict['created_by'] = str(row_dict['created_by'])
            versions.append(FirmwareVersionRead(**row_dict))
        
        return versions

# ===== TELEMETRY INGESTION =====

@router.post("/telemetry", response_model=TelemetryDataRead)
async def record_telemetry(
    device_id: str,
    telemetry: TelemetryDataCreate,
    request: Request
):
    """Record device telemetry (device can call with device registration endpoint)"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify device exists
        device = await conn.fetchrow(
            "SELECT id FROM devices WHERE id = $1",
            device_id
        )
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Update last_seen
        await conn.execute(
            "UPDATE devices SET last_seen = now(), status = 'online' WHERE id = $1",
            device_id
        )
        
        # Record telemetry
        row = await conn.fetchrow(
            """
            INSERT INTO device_telemetry(device_id, metric_name, metric_value, tags, timestamp)
            VALUES($1, $2, $3, $4, now())
            RETURNING id, device_id, timestamp, metric_name, metric_value, tags
            """,
            device_id, telemetry.metric_name, telemetry.metric_value, telemetry.tags
        )
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        row_dict['device_id'] = str(row_dict['device_id'])
        return TelemetryDataRead(**row_dict)

@router.get("/telemetry/{device_id}", response_model=list)
async def get_device_telemetry(
    device_id: str,
    limit: int = 100,
    request: Request = None,
    current_user=Depends(get_current_user)
):
    """Get telemetry history for a device"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify ownership
        row = await conn.fetchrow(
            """
            SELECT d.id FROM devices d
            JOIN projects p ON d.project_id = p.id
            WHERE d.id = $1 AND p.owner_id = $2
            """,
            device_id, current_user['id']
        )
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        rows = await conn.fetch(
            """
            SELECT id, device_id, timestamp, metric_name, metric_value, tags
            FROM device_telemetry WHERE device_id = $1
            ORDER BY timestamp DESC LIMIT $2
            """,
            device_id, limit
        )
        
        telemetry_list = []
        for row in rows:
            row_dict = dict(row)
            row_dict['id'] = str(row_dict['id'])
            row_dict['device_id'] = str(row_dict['device_id'])
            telemetry_list.append(TelemetryDataRead(**row_dict))
        
        return telemetry_list

# ===== DEVICE HEALTH =====

@router.get("/devices/{device_id}/health", response_model=DeviceHealthRead)
async def get_device_health(
    device_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Get device health status"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT d.id, d.name, d.status, d.firmware_version, d.last_seen
            FROM devices d
            JOIN projects p ON d.project_id = p.id
            WHERE d.id = $1 AND p.owner_id = $2
            """,
            device_id, current_user['id']
        )
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Calculate uptime
        uptime = None
        if row['last_seen']:
            uptime = int((datetime.utcnow() - row['last_seen']).total_seconds())
        
        return DeviceHealthRead(
            device_id=str(row['id']),
            device_name=row['name'],
            status=row['status'],
            firmware_version=row['firmware_version'],
            last_seen=row['last_seen'],
            uptime_seconds=uptime
        )
