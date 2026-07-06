from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from shared.models import Project
from admin.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from admin.api.deps import get_db, get_current_user
from admin.models import User

router = APIRouter()

@router.get("/projects", response_model=List[ProjectListResponse])
def list_projects(
    status: str = Query(None),
    is_own_project: bool = Query(None),
    is_published: bool = Query(None),
    client_id: UUID = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Project)

    if status:
        query = query.filter(Project.status == status)
    if is_own_project is not None:
        query = query.filter(Project.is_own_project == is_own_project)
    if is_published is not None:
        query = query.filter(Project.is_published == is_published)
    if client_id:
        query = query.filter(Project.client_id == client_id)

    return query.order_by(Project.display_order, Project.updated_at.desc()).all()

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return project

@router.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_project = db.query(Project).filter(Project.slug == project_data.slug).first()
    if existing_project:
        raise HTTPException(status_code=409, detail="Ya existe un proyecto con este slug")

    db_project = Project(**project_data.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project

@router.patch("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    update_data = project_data.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != project.slug:
        existing = db.query(Project).filter(Project.slug == update_data["slug"]).first()
        if existing:
            raise HTTPException(status_code=409, detail="Ya existe un proyecto con este slug")

    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return project

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    db.delete(project)
    db.commit()

    return {"message": "Proyecto eliminado exitosamente"}