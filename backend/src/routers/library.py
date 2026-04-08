from fastapi import APIRouter, Query, Request, Depends, HTTPException, status
from typing import List, Optional
from ..database import get_pool
from ..models import (
    DeviceLibraryAutocomplete,
    ComponentLibraryAutocomplete,
    DeviceAutocomplete,
    ProjectAutocomplete,
    DeviceLibraryRead,
)
from ..utils import get_current_user

router = APIRouter()

# ===== DEVICE LIBRARY SEARCH =====

@router.get("/library/devices/search", response_model=List[DeviceLibraryAutocomplete])
async def search_device_library(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    request: Request = None
):
    """Search device library (boards, microcontrollers, etc.)"""
    pool = get_pool(request.app)
    
    search_term = f"%{q.lower()}%"
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, version, category, description
            FROM device_library
            WHERE LOWER(name) LIKE $1 OR LOWER(description) LIKE $1
            ORDER BY name ASC
            LIMIT $2
            """,
            search_term,
            limit
        )
        
        return [
            DeviceLibraryAutocomplete(
                id=str(row['id']),
                name=row['name'],
                version=row['version'],
                category=row['category'],
                description=row['description']
            )
            for row in rows
        ]

@router.get("/library/devices/category/{category}", response_model=List[DeviceLibraryAutocomplete])
async def get_devices_by_category(
    category: str,
    limit: int = Query(20, ge=1, le=100),
    request: Request = None
):
    """Get devices by category"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, version, category, description
            FROM device_library
            WHERE LOWER(category) = LOWER($1)
            ORDER BY name ASC
            LIMIT $2
            """,
            category,
            limit
        )
        
        return [
            DeviceLibraryAutocomplete(
                id=str(row['id']),
                name=row['name'],
                version=row['version'],
                category=row['category'],
                description=row['description']
            )
            for row in rows
        ]

# ===== COMPONENT LIBRARY SEARCH =====

@router.get("/library/components/search", response_model=List[ComponentLibraryAutocomplete])
async def search_component_library(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    request: Request = None
):
    """Search component library for BOM"""
    pool = get_pool(request.app)
    
    search_term = f"%{q.lower()}%"
    
    async with pool.acquire() as conn:
        # Search by name, part_number, or keywords
        rows = await conn.fetch(
            """
            SELECT id, name, part_number, category, manufacturer, description
            FROM component_library
            WHERE LOWER(name) LIKE $1 
               OR LOWER(part_number) LIKE $1
               OR LOWER(manufacturer) LIKE $1
            ORDER BY name ASC
            LIMIT $2
            """,
            search_term,
            limit
        )
        
        return [
            ComponentLibraryAutocomplete(
                id=str(row['id']),
                name=row['name'],
                part_number=row['part_number'],
                category=row['category'],
                manufacturer=row['manufacturer'],
                description=row['description']
            )
            for row in rows
        ]

@router.get("/library/components/category/{category}", response_model=List[ComponentLibraryAutocomplete])
async def get_components_by_category(
    category: str,
    limit: int = Query(20, ge=1, le=100),
    request: Request = None
):
    """Get components by category"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, part_number, category, manufacturer, description
            FROM component_library
            WHERE LOWER(category) = LOWER($1)
            ORDER BY name ASC
            LIMIT $2
            """,
            category,
            limit
        )
        
        return [
            ComponentLibraryAutocomplete(
                id=str(row['id']),
                name=row['name'],
                part_number=row['part_number'],
                category=row['category'],
                manufacturer=row['manufacturer'],
                description=row['description']
            )
            for row in rows
        ]

# ===== DEVICE AUTOCOMPLETE (Project Devices) =====

@router.get("/devices/search", response_model=List[DeviceAutocomplete])
async def search_project_devices(
    project_id: str = Query(...),
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    request: Request = None,
    current_user=Depends(get_current_user)
):
    """Search devices in a project"""
    pool = get_pool(request.app)
    
    search_term = f"%{q.lower()}%"
    
    async with pool.acquire() as conn:
        # Verify user owns the project
        project = await conn.fetchrow(
            "SELECT owner_id FROM projects WHERE id = $1",
            project_id
        )
        if not project or project['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        rows = await conn.fetch(
            """
            SELECT id, name, device_type, project_id
            FROM devices
            WHERE project_id = $1 AND (LOWER(name) LIKE $2 OR LOWER(device_type) LIKE $2)
            ORDER BY name ASC
            LIMIT $3
            """,
            project_id,
            search_term,
            limit
        )
        
        return [
            DeviceAutocomplete(
                id=str(row['id']),
                name=row['name'],
                device_type=row['device_type'],
                project_id=str(row['project_id'])
            )
            for row in rows
        ]

# ===== PROJECT AUTOCOMPLETE =====

@router.get("/projects/search", response_model=List[ProjectAutocomplete])
async def search_projects(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    request: Request = None,
    current_user=Depends(get_current_user)
):
    """Search user's projects"""
    pool = get_pool(request.app)
    
    search_term = f"%{q.lower()}%"
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, title, slug, owner_id
            FROM projects
            WHERE owner_id = $1 AND LOWER(title) LIKE $2
            ORDER BY title ASC
            LIMIT $3
            """,
            current_user['id'],
            search_term,
            limit
        )
        
        return [
            ProjectAutocomplete(
                id=str(row['id']),
                title=row['title'],
                slug=row['slug'],
                owner_id=str(row['owner_id'])
            )
            for row in rows
        ]

# ===== LIBRARY STATISTICS =====

@router.get("/library/stats")
async def get_library_stats(request: Request = None):
    """Get library statistics (device and component counts)"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        device_count = await conn.fetchval("SELECT COUNT(*) FROM device_library")
        component_count = await conn.fetchval("SELECT COUNT(*) FROM component_library")
        
        # Get top categories
        device_categories = await conn.fetch(
            """
            SELECT category, COUNT(*) as count
            FROM device_library
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            LIMIT 10
            """
        )
        
        component_categories = await conn.fetch(
            """
            SELECT category, COUNT(*) as count
            FROM component_library
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            LIMIT 10
            """
        )
        
        return {
            "device_library": {
                "total": device_count,
                "top_categories": [
                    {"category": row['category'], "count": row['count']}
                    for row in device_categories
                ]
            },
            "component_library": {
                "total": component_count,
                "top_categories": [
                    {"category": row['category'], "count": row['count']}
                    for row in component_categories
                ]
            }
        }

# ===== COMPONENT LIBRARY DETAILS =====

@router.get("/library/components/{component_id}", response_model=ComponentLibraryAutocomplete)
async def get_component_details(
    component_id: str,
    request: Request = None
):
    """Get detailed information about a component"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, name, part_number, category, manufacturer, description
            FROM component_library
            WHERE id = $1
            """,
            component_id
        )
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Component not found"
            )
        
        return ComponentLibraryAutocomplete(
            id=str(row['id']),
            name=row['name'],
            part_number=row['part_number'],
            category=row['category'],
            manufacturer=row['manufacturer'],
            description=row['description']
        )

# ===== DEVICE LIBRARY DETAILS =====

@router.get("/library/devices/{device_id}", response_model=DeviceLibraryRead)
async def get_device_library_details(
    device_id: str,
    request: Request = None
):
    """Get detailed information about a device library entry"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, name, version, author, category, architectures, types,
                   description, repository, website, keywords, created_at, updated_at
            FROM device_library
            WHERE id = $1
            """,
            device_id
        )
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        return DeviceLibraryRead(
            id=str(row['id']),
            name=row['name'],
            version=row['version'],
            author=row['author'],
            category=row['category'],
            architectures=row['architectures'] or [],
            types=row['types'] or [],
            description=row['description'],
            repository=row['repository'],
            website=row['website'],
            keywords=row['keywords'] or [],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
