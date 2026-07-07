from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from shared.models import Client, Conversation, Contact
from admin.schemas import ClientCreate, ClientUpdate, ClientResponse, ClientListResponse
from admin.api.deps import get_db, get_current_user
from admin.models import User

router = APIRouter()

@router.get("/clients", response_model=List[ClientListResponse])
def list_clients(
    status: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Client)

    if status:
        query = query.filter(Client.status == status)

    return query.order_by(Client.updated_at.desc()).all()

@router.get("/clients/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    return client

@router.post("/clients", response_model=ClientResponse, status_code=201)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_client = Client(**client_data.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    return db_client

@router.patch("/clients/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: UUID,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)

    return client

@router.delete("/clients/{client_id}")
def delete_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    db.delete(client)
    db.commit()

    return {"message": "Cliente eliminado exitosamente"}