from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_categories_service
from app.schemas.category import (
    CategoryCreateSchema,
    CategorySchema,
    CategoryUpdateSchema,
)
from app.services.category import CategoryNotFoundError, CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategorySchema])
def get_categories(
    service: CategoryService = Depends(get_categories_service),
) -> list[CategorySchema]:
    return service.list_categories()


@router.post("", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreateSchema,
    service: CategoryService = Depends(get_categories_service),
) -> CategorySchema:
    return service.create_category(payload)


@router.patch("/{category_id}", response_model=CategorySchema)
def update_category(
    category_id: str,
    payload: CategoryUpdateSchema,
    service: CategoryService = Depends(get_categories_service),
) -> CategorySchema:
    try:
        return service.update_category(category_id, payload)
    except CategoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    service: CategoryService = Depends(get_categories_service),
) -> None:
    try:
        service.delete_category(category_id)
    except CategoryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )
