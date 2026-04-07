from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from datetime import datetime
from typing import List
import json
from ..database import get_pool
from ..models import (
    BOMCreate, BOMRead, BOMUpdate, BOMItemCreate, BOMItemRead, BOMItemUpdate,
    ComponentVariantCreate, ComponentVariantRead,
    ComponentLibraryCreate, ComponentLibraryRead,
    BOMMaterialCostSummary, BOMForkRequest
)
from ..utils import get_current_user

router = APIRouter()

# ===== COMPONENT LIBRARY =====

@router.post("/library", response_model=ComponentLibraryRead)
async def add_to_library(
    component: ComponentLibraryCreate,
    request: Request
):
    """Add a component to the global library (public contribution)"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Check if already exists
        existing = await conn.fetchrow(
            "SELECT id FROM component_library WHERE part_number = $1",
            component.part_number
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Component already exists in library"
            )
        
        row = await conn.fetchrow(
            """
            INSERT INTO component_library(
                part_number, name, category, manufacturer, description,
                datasheet_url, pinout_diagram_url, specifications, package_type
            )
            VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, part_number, name, category, manufacturer, description,
                      datasheet_url, pinout_diagram_url, specifications, package_type,
                      created_at, updated_at
            """,
            component.part_number, component.name, component.category,
            component.manufacturer, component.description,
            component.datasheet_url, component.pinout_diagram_url,
            component.specifications, component.package_type
        )
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        return ComponentLibraryRead(**row_dict)

@router.get("/library/search")
async def search_library(
    q: str = Query(..., min_length=1),
    category: str = None,
    request: Request = None
):
    """Search component library by name, part number, or category"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        if category:
            rows = await conn.fetch(
                """
                SELECT id, part_number, name, category, manufacturer, description,
                       datasheet_url, pinout_diagram_url, specifications, package_type,
                       created_at, updated_at
                FROM component_library
                WHERE (name ILIKE $1 OR part_number ILIKE $1 OR manufacturer ILIKE $1)
                  AND category = $2
                LIMIT 50
                """,
                f"%{q}%", category
            )
        else:
            rows = await conn.fetch(
                """
                SELECT id, part_number, name, category, manufacturer, description,
                       datasheet_url, pinout_diagram_url, specifications, package_type,
                       created_at, updated_at
                FROM component_library
                WHERE name ILIKE $1 OR part_number ILIKE $1 OR manufacturer ILIKE $1
                LIMIT 50
                """,
                f"%{q}%"
            )
        
        results = []
        for row in rows:
            row_dict = dict(row)
            row_dict['id'] = str(row_dict['id'])
            results.append(ComponentLibraryRead(**row_dict))
        
        return results

@router.get("/library/{component_id}", response_model=ComponentLibraryRead)
async def get_library_component(
    component_id: str,
    request: Request = None
):
    """Get component library entry"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, part_number, name, category, manufacturer, description,
                   datasheet_url, pinout_diagram_url, specifications, package_type,
                   created_at, updated_at
            FROM component_library WHERE id = $1
            """,
            component_id
        )
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Component not found"
            )
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        return ComponentLibraryRead(**row_dict)

# ===== BOM MANAGEMENT =====

@router.post("/boms", response_model=BOMRead)
async def create_bom(
    project_id: str,
    bom: BOMCreate,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Create a new BOM for a project"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify ownership
        project = await conn.fetchrow(
            "SELECT owner_id FROM projects WHERE id = $1",
            project_id
        )
        if not project or project['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create BOM for this project"
            )
        
        # Create BOM
        row = await conn.fetchrow(
            """
            INSERT INTO boms(project_id, device_id, version, name, description, created_by)
            VALUES($1, $2, $3, $4, $5, $6)
            RETURNING id, project_id, device_id, version, name, description,
                      estimated_cost, is_locked, created_by, created_at, updated_at
            """,
            project_id, bom.device_id, bom.version, bom.name, bom.description,
            str(current_user['id'])
        )
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        row_dict['project_id'] = str(row_dict['project_id'])
        row_dict['created_by'] = str(row_dict['created_by'])
        row_dict['items'] = []
        return BOMRead(**row_dict)

@router.get("/boms", response_model=List[BOMRead])
async def list_boms(
    project_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    """List all BOMs for a project"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify ownership
        project = await conn.fetchrow(
            "SELECT owner_id FROM projects WHERE id = $1",
            project_id
        )
        if not project or project['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view BOMs for this project"
            )
        
        rows = await conn.fetch(
            """
            SELECT id, project_id, device_id, version, name, description,
                   estimated_cost, is_locked, created_by, created_at, updated_at
            FROM boms WHERE project_id = $1 ORDER BY created_at DESC
            """,
            project_id
        )
        
        boms = []
        for row in rows:
            row_dict = dict(row)
            row_dict['id'] = str(row_dict['id'])
            row_dict['project_id'] = str(row_dict['project_id'])
            row_dict['created_by'] = str(row_dict['created_by'])
            row_dict['items'] = []
            boms.append(BOMRead(**row_dict))
        
        return boms

@router.get("/boms/{bom_id}", response_model=BOMRead)
async def get_bom(
    bom_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Get BOM with all items"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Get BOM and verify ownership
        bom_row = await conn.fetchrow(
            """
            SELECT b.id, b.project_id, b.device_id, b.version, b.name, b.description,
                   b.estimated_cost, b.is_locked, b.created_by, b.created_at, b.updated_at,
                   p.owner_id
            FROM boms b
            JOIN projects p ON b.project_id = p.id
            WHERE b.id = $1
            """,
            bom_id
        )
        
        if not bom_row or bom_row['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BOM not found"
            )
        
        # Get BOM items
        item_rows = await conn.fetch(
            """
            SELECT id, bom_id, reference, description, quantity, part_number,
                   manufacturer, unit_price, supplier, supplier_url, lead_time_days,
                   datasheet_url, notes, created_at, updated_at
            FROM bom_items WHERE bom_id = $1 ORDER BY reference ASC
            """,
            bom_id
        )
        
        items = []
        for item_row in item_rows:
            item_dict = dict(item_row)
            item_dict['id'] = str(item_dict['id'])
            item_dict['bom_id'] = str(item_dict['bom_id'])
            item_dict['total_price'] = (item_dict['unit_price'] * item_dict['quantity']) if item_dict['unit_price'] else None
            items.append(BOMItemRead(**item_dict))
        
        bom_dict = dict(bom_row)
        bom_dict['id'] = str(bom_dict['id'])
        bom_dict['project_id'] = str(bom_dict['project_id'])
        bom_dict['created_by'] = str(bom_dict['created_by'])
        bom_dict['items'] = items
        return BOMRead(**bom_dict)

@router.put("/boms/{bom_id}", response_model=BOMRead)
async def update_bom(
    bom_id: str,
    update: BOMUpdate,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Update BOM metadata"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify ownership
        bom_row = await conn.fetchrow(
            """
            SELECT b.id, p.owner_id FROM boms b
            JOIN projects p ON b.project_id = p.id
            WHERE b.id = $1
            """,
            bom_id
        )
        
        if not bom_row or bom_row['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BOM not found"
            )
        
        # Build update query
        updates = ["updated_at = now()"]
        params = []
        
        if update.name is not None:
            updates.append(f"name = ${len(params) + 1}")
            params.append(update.name)
        if update.description is not None:
            updates.append(f"description = ${len(params) + 1}")
            params.append(update.description)
        if update.estimated_cost is not None:
            updates.append(f"estimated_cost = ${len(params) + 1}")
            params.append(update.estimated_cost)
        if update.is_locked is not None:
            updates.append(f"is_locked = ${len(params) + 1}")
            params.append(update.is_locked)
        
        params.append(bom_id)
        
        query = f"""
            UPDATE boms SET {', '.join(updates)} WHERE id = ${len(params)}
            RETURNING id, project_id, device_id, version, name, description,
                      estimated_cost, is_locked, created_by, created_at, updated_at
        """
        
        row = await conn.fetchrow(query, *params)
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        row_dict['project_id'] = str(row_dict['project_id'])
        row_dict['created_by'] = str(row_dict['created_by'])
        row_dict['items'] = []
        return BOMRead(**row_dict)

# ===== BOM ITEMS =====

@router.post("/boms/{bom_id}/items", response_model=BOMItemRead)
async def add_bom_item(
    bom_id: str,
    item: BOMItemCreate,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Add an item to a BOM"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify ownership
        bom_row = await conn.fetchrow(
            """
            SELECT b.id, p.owner_id FROM boms b
            JOIN projects p ON b.project_id = p.id
            WHERE b.id = $1
            """,
            bom_id
        )
        
        if not bom_row or bom_row['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BOM not found"
            )
        
        row = await conn.fetchrow(
            """
            INSERT INTO bom_items(
                bom_id, reference, description, quantity, part_number, manufacturer,
                unit_price, supplier, supplier_url, lead_time_days, datasheet_url, notes,
                component_library_id
            )
            VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING id, bom_id, reference, description, quantity, part_number,
                      manufacturer, unit_price, supplier, supplier_url, lead_time_days,
                      datasheet_url, notes, created_at, updated_at
            """,
            bom_id, item.reference, item.description, item.quantity,
            item.part_number, item.manufacturer, item.unit_price,
            item.supplier, item.supplier_url, item.lead_time_days,
            item.datasheet_url, item.notes, item.component_library_id
        )
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        row_dict['bom_id'] = str(row_dict['bom_id'])
        row_dict['total_price'] = (row_dict['unit_price'] * row_dict['quantity']) if row_dict['unit_price'] else None
        return BOMItemRead(**row_dict)

@router.put("/bom-items/{item_id}", response_model=BOMItemRead)
async def update_bom_item(
    item_id: str,
    update: BOMItemUpdate,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Update a BOM item"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify ownership
        item_row = await conn.fetchrow(
            """
            SELECT bi.id, p.owner_id FROM bom_items bi
            JOIN boms b ON bi.bom_id = b.id
            JOIN projects p ON b.project_id = p.id
            WHERE bi.id = $1
            """,
            item_id
        )
        
        if not item_row or item_row['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        # Build update query
        updates = ["updated_at = now()"]
        params = []
        param_idx = 1
        
        if update.reference is not None:
            updates.append(f"reference = ${param_idx}")
            params.append(update.reference)
            param_idx += 1
        if update.description is not None:
            updates.append(f"description = ${param_idx}")
            params.append(update.description)
            param_idx += 1
        if update.quantity is not None:
            updates.append(f"quantity = ${param_idx}")
            params.append(update.quantity)
            param_idx += 1
        if update.part_number is not None:
            updates.append(f"part_number = ${param_idx}")
            params.append(update.part_number)
            param_idx += 1
        if update.manufacturer is not None:
            updates.append(f"manufacturer = ${param_idx}")
            params.append(update.manufacturer)
            param_idx += 1
        if update.unit_price is not None:
            updates.append(f"unit_price = ${param_idx}")
            params.append(update.unit_price)
            param_idx += 1
        if update.supplier is not None:
            updates.append(f"supplier = ${param_idx}")
            params.append(update.supplier)
            param_idx += 1
        if update.supplier_url is not None:
            updates.append(f"supplier_url = ${param_idx}")
            params.append(update.supplier_url)
            param_idx += 1
        if update.notes is not None:
            updates.append(f"notes = ${param_idx}")
            params.append(update.notes)
            param_idx += 1
        
        params.append(item_id)
        
        query = f"""
            UPDATE bom_items SET {', '.join(updates)} WHERE id = ${param_idx}
            RETURNING id, bom_id, reference, description, quantity, part_number,
                      manufacturer, unit_price, supplier, supplier_url, lead_time_days,
                      datasheet_url, notes, created_at, updated_at
        """
        
        row = await conn.fetchrow(query, *params)
        
        row_dict = dict(row)
        row_dict['id'] = str(row_dict['id'])
        row_dict['bom_id'] = str(row_dict['bom_id'])
        row_dict['total_price'] = (row_dict['unit_price'] * row_dict['quantity']) if row_dict['unit_price'] else None
        return BOMItemRead(**row_dict)

@router.delete("/bom-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bom_item(
    item_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Delete a BOM item"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify ownership
        item_row = await conn.fetchrow(
            """
            SELECT bi.id, p.owner_id FROM bom_items bi
            JOIN boms b ON bi.bom_id = b.id
            JOIN projects p ON b.project_id = p.id
            WHERE bi.id = $1
            """,
            item_id
        )
        
        if not item_row or item_row['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        
        await conn.execute("DELETE FROM bom_items WHERE id = $1", item_id)

# ===== BOM SUMMARY & COST ANALYSIS =====

@router.get("/boms/{bom_id}/summary", response_model=BOMMaterialCostSummary)
async def get_bom_summary(
    bom_id: str,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Get BOM cost summary and statistics"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Verify ownership
        bom_row = await conn.fetchrow(
            """
            SELECT b.id, p.owner_id FROM boms b
            JOIN projects p ON b.project_id = p.id
            WHERE b.id = $1
            """,
            bom_id
        )
        
        if not bom_row or bom_row['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BOM not found"
            )
        
        # Get aggregate stats
        stats = await conn.fetchrow(
            """
            SELECT
              COUNT(*) as total_items,
              COUNT(DISTINCT part_number) as unique_parts,
              SUM(unit_price * quantity) as total_cost,
              AVG(unit_price) as average_unit_cost,
              MAX(lead_time_days) as longest_lead_time,
              array_agg(DISTINCT supplier) as suppliers
            FROM bom_items WHERE bom_id = $1
            """,
            bom_id
        )
        
        return BOMMaterialCostSummary(
            total_items=stats['total_items'] or 0,
            unique_parts=stats['unique_parts'] or 0,
            total_cost=float(stats['total_cost']) if stats['total_cost'] else 0.0,
            average_unit_cost=float(stats['average_unit_cost']) if stats['average_unit_cost'] else 0.0,
            longest_lead_time_days=stats['longest_lead_time'],
            suppliers=[s for s in (stats['suppliers'] or []) if s]
        )

# ===== BOM FORKING (Clone BOM with variants) =====

@router.post("/boms/{bom_id}/fork", response_model=BOMRead)
async def fork_bom(
    bom_id: str,
    fork_request: BOMForkRequest,
    request: Request,
    current_user=Depends(get_current_user)
):
    """Fork a BOM to create variant with potential component swaps"""
    pool = get_pool(request.app)
    
    async with pool.acquire() as conn:
        # Get source BOM
        source_bom = await conn.fetchrow(
            """
            SELECT b.id, b.project_id, b.device_id, p.owner_id
            FROM boms b
            JOIN projects p ON b.project_id = p.id
            WHERE b.id = $1
            """,
            bom_id
        )
        
        if not source_bom or source_bom['owner_id'] != current_user['id']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source BOM not found"
            )
        
        # Create new BOM
        new_bom = await conn.fetchrow(
            """
            INSERT INTO boms(project_id, device_id, version, name, description, parent_bom_id, created_by)
            VALUES($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, project_id, device_id, version, name, description,
                      estimated_cost, is_locked, created_by, created_at, updated_at
            """,
            source_bom['project_id'], fork_request.new_device_id or source_bom['device_id'],
            fork_request.new_version, fork_request.new_name, None, bom_id,
            str(current_user['id'])
        )
        
        # Copy all items from source BOM
        items = await conn.fetch(
            """
            SELECT reference, description, quantity, part_number, manufacturer,
                   unit_price, supplier, supplier_url, lead_time_days, datasheet_url,
                   notes, component_library_id
            FROM bom_items WHERE bom_id = $1
            """,
            bom_id
        )
        
        for item in items:
            await conn.execute(
                """
                INSERT INTO bom_items(
                    bom_id, reference, description, quantity, part_number, manufacturer,
                    unit_price, supplier, supplier_url, lead_time_days, datasheet_url, notes,
                    component_library_id
                )
                VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """,
                new_bom['id'], item['reference'], item['description'], item['quantity'],
                item['part_number'], item['manufacturer'], item['unit_price'],
                item['supplier'], item['supplier_url'], item['lead_time_days'],
                item['datasheet_url'], item['notes'], item['component_library_id']
            )
        
        new_bom_dict = dict(new_bom)
        new_bom_dict['id'] = str(new_bom_dict['id'])
        new_bom_dict['project_id'] = str(new_bom_dict['project_id'])
        new_bom_dict['created_by'] = str(new_bom_dict['created_by'])
        new_bom_dict['items'] = []
        return BOMRead(**new_bom_dict)
