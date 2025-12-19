from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_database
from app.api.dependencies import get_current_active_user
from app.crud.category import CategoryCRUD
from app.models.user import UserInDB
from app.models.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    TipoCategoria
)

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Crear una nueva categoría (generalmente no se usa, las 4 categorías se crean automáticamente)
    """
    category_crud = CategoryCRUD(db)
    created = await category_crud.create(str(current_user.id), category)

    return CategoryResponse(
        _id=str(created.id),
        user_id=str(created.user_id),
        nombre=created.nombre,
        slug=created.slug,
        icono=created.icono,
        color=created.color,
        tiene_meta=created.tiene_meta,
        descripcion=created.descripcion,
        created_at=created.created_at,
        updated_at=created.updated_at
    )


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener todas las categorías del usuario
    Verifica y crea las 4 categorías por defecto si no existen
    """
    category_crud = CategoryCRUD(db)
    categories = await category_crud.check_and_init_if_needed(str(current_user.id))

    return [
        CategoryResponse(
            _id=str(cat.id),
            user_id=str(cat.user_id),
            nombre=cat.nombre,
            slug=cat.slug,
            icono=cat.icono,
            color=cat.color,
            tiene_meta=cat.tiene_meta,
            descripcion=cat.descripcion,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        )
        for cat in categories
    ]


@router.post("/init-defaults", response_model=List[CategoryResponse])
async def init_default_categories(
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Inicializar las 4 categorías por defecto para el usuario

    Las 4 categorías según LOGICA_SISTEMA.md:
    1. 💵 Ahorro
    2. 🏠 Arriendo
    3. 💳 Crédito Usable
    4. 💸 Liquidez
    """
    category_crud = CategoryCRUD(db)
    categories = await category_crud.init_default_categories(str(current_user.id))

    return [
        CategoryResponse(
            _id=str(cat.id),
            user_id=str(cat.user_id),
            nombre=cat.nombre,
            slug=cat.slug,
            icono=cat.icono,
            color=cat.color,
            tiene_meta=cat.tiene_meta,
            descripcion=cat.descripcion,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        )
        for cat in categories
    ]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener una categoría por ID
    """
    category_crud = CategoryCRUD(db)
    category = await category_crud.get_by_id(str(current_user.id), category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return CategoryResponse(
        _id=str(category.id),
        user_id=str(category.user_id),
        nombre=category.nombre,
        slug=category.slug,
        icono=category.icono,
        color=category.color,
        tiene_meta=category.tiene_meta,
        descripcion=category.descripcion,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@router.get("/by-slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: TipoCategoria,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener una categoría por slug (ahorro, arriendo, credito, liquidez)
    """
    category_crud = CategoryCRUD(db)
    category = await category_crud.get_by_slug(str(current_user.id), slug)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with slug '{slug}' not found"
        )

    return CategoryResponse(
        _id=str(category.id),
        user_id=str(category.user_id),
        nombre=category.nombre,
        slug=category.slug,
        icono=category.icono,
        color=category.color,
        tiene_meta=category.tiene_meta,
        descripcion=category.descripcion,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_update: CategoryUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Actualizar una categoría
    Solo permite editar nombre, icono, color y descripción
    """
    category_crud = CategoryCRUD(db)
    updated = await category_crud.update(str(current_user.id), category_id, category_update)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return CategoryResponse(
        _id=str(updated.id),
        user_id=str(updated.user_id),
        nombre=updated.nombre,
        slug=updated.slug,
        icono=updated.icono,
        color=updated.color,
        tiene_meta=updated.tiene_meta,
        descripcion=updated.descripcion,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Eliminar una categoría

    NOTA: En producción, probablemente NO se deberían eliminar las 4 categorías fijas
    """
    category_crud = CategoryCRUD(db)
    deleted = await category_crud.delete(str(current_user.id), category_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return None
