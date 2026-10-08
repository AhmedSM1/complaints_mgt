from fastapi import APIRouter, HTTPException, status

from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.services.items import ItemNotFoundError, item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[Item])
def list_items() -> list[Item]:
    return item_service.list_items()


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int) -> Item:
    try:
        return item_service.get_item(item_id)
    except ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate) -> Item:
    return item_service.create_item(payload)


@router.patch("/{item_id}", response_model=Item)
def update_item(item_id: int, payload: ItemUpdate) -> Item:
    try:
        return item_service.update_item(item_id, payload)
    except ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    try:
        item_service.delete_item(item_id)
    except ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
