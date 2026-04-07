from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List, Optional
from ..models import ProjectCreate, ProjectRead, ProjectUpdate
from ..database import get_pool
from ..utils import get_current_user, get_current_user_optional, slugify

router = APIRouter()

async def fetch_project_tags(conn, project_id: str) -> List[str]:
    rows = await conn.fetch(
        "SELECT t.name FROM tags t JOIN project_tags pt ON t.id = pt.tag_id WHERE pt.project_id = $1",
        project_id,
    )
    return [row["name"] for row in rows]

async def save_project_tags(conn, project_id: str, tag_names: Optional[List[str]]) -> None:
    if tag_names is None:
        return

    await conn.execute("DELETE FROM project_tags WHERE project_id = $1", project_id)
    unique_tags = []
    for tag in tag_names:
        cleaned = tag.strip()
        if cleaned and cleaned.lower() not in [t.lower() for t in unique_tags]:
            unique_tags.append(cleaned)

    for tag in unique_tags:
        row = await conn.fetchrow("SELECT id FROM tags WHERE lower(name) = lower($1)", tag)
        if row is None:
            row = await conn.fetchrow("INSERT INTO tags(name) VALUES ($1) RETURNING id", tag)
        await conn.execute(
            "INSERT INTO project_tags(project_id, tag_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            project_id,
            row["id"],
        )

async def build_project_response(conn, row) -> ProjectRead:
    tags = await fetch_project_tags(conn, row["id"])
    return ProjectRead(
        id=str(row["id"]),
        owner_id=str(row["owner_id"]),
        title=row["title"],
        summary=row["summary"],
        description=row["description"],
        visibility=row["visibility"],
        status=row["status"],
        tags=tags,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )

@router.get("/", response_model=List[ProjectRead])
async def list_projects(
    request: Request,
    current_user=Depends(get_current_user)
):
    pool = get_pool(request.app)
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM projects WHERE owner_id = $1 ORDER BY created_at DESC LIMIT 50",
            current_user['id']
        )
        result = [await build_project_response(conn, row) for row in rows]
    return result

@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user=Depends(get_current_user),
    request: Request = None,
):
    pool = get_pool(request.app)
    async with pool.acquire() as conn:
        base_slug = slugify(project.title)
        slug = base_slug
        suffix = 1
        while await conn.fetchval("SELECT 1 FROM projects WHERE slug = $1", slug):
            suffix += 1
            slug = f"{base_slug}-{suffix}"

        row = await conn.fetchrow(
            "INSERT INTO projects(owner_id, title, slug, summary, description, visibility, status) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *",
            current_user["id"],
            project.title,
            slug,
            project.summary,
            project.description,
            project.visibility,
            project.status,
        )
        await save_project_tags(conn, row["id"], project.tags)
        return await build_project_response(conn, row)

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: str, request: Request):
    current_user = await get_current_user_optional(request)
    pool = get_pool(request.app)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM projects WHERE id = $1", project_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if row["visibility"] != "public" and (
            current_user is None or str(current_user["id"]) != str(row["owner_id"])
        ):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")
        return await build_project_response(conn, row)

@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str,
    project: ProjectUpdate,
    current_user=Depends(get_current_user),
    request: Request = None,
):
    pool = get_pool(request.app)
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT * FROM projects WHERE id = $1", project_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if str(existing["owner_id"]) != str(current_user["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can update this project")

        values = {
            "title": project.title or existing["title"],
            "summary": project.summary if project.summary is not None else existing["summary"],
            "description": project.description if project.description is not None else existing["description"],
            "visibility": project.visibility or existing["visibility"],
            "status": project.status or existing["status"],
        }
        row = await conn.fetchrow(
            "UPDATE projects SET title = $1, summary = $2, description = $3, visibility = $4, status = $5, updated_at = now() WHERE id = $6 RETURNING *",
            values["title"],
            values["summary"],
            values["description"],
            values["visibility"],
            values["status"],
            project_id,
        )
        if project.tags is not None:
            await save_project_tags(conn, project_id, project.tags)
        return await build_project_response(conn, row)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, current_user=Depends(get_current_user), request: Request = None):
    pool = get_pool(request.app)
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT owner_id FROM projects WHERE id = $1", project_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if str(existing["owner_id"]) != str(current_user["id"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can delete this project")
        await conn.execute("DELETE FROM projects WHERE id = $1", project_id)
        return None
