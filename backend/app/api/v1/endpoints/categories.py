from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_database
from app.api.dependencies import get_current_user
from app.crud.category import CategoryCRUD
from app.models.user import UserInDB
from app.models.category import CategoryCreate, CategoryUpdate, CategoryResponse, TipoCategoria

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Crear una nueva categoría personalizada.

    Las 4 categorías principales ya existen por defecto, pero se pueden crear subcategorías.
    """
    category_crud = CategoryCRUD(db)
    category = await category_crud.create(str(current_user.id), category_data)

    return CategoryResponse(
        _id=str(category.id),
        user_id=str(category.user_id),
        nombre=category.nombre,
        tipo=category.tipo,
        color=category.color,
        icono=category.icono,
        subcategorias=category.subcategorias,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    tipo: Optional[TipoCategoria] = None,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Obtener todas las categorías del usuario, opcionalmente filtradas por tipo.
    """
    category_crud = CategoryCRUD(db)
    categories = await category_crud.get_all(str(current_user.id), tipo)

    return [
        CategoryResponse(
            _id=str(cat.id),
            user_id=str(cat.user_id),
            nombre=cat.nombre,
            tipo=cat.tipo,
            color=cat.color,
            icono=cat.icono,
            subcategorias=cat.subcategorias,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        )
        for cat in categories
    ]


@router.post("/init-defaults", response_model=List[CategoryResponse])
async def initialize_default_categories(
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Inicializar las 4 categorías predeterminadas para el usuario.

    Solo debe llamarse una vez por usuario (al registrarse).
    """
    category_crud = CategoryCRUD(db)

    # Verificar si ya tiene categorías
    existing = await category_crud.get_all(str(current_user.id))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya tiene categorías inicializadas"
        )

    categories = await category_crud.initialize_default_categories(str(current_user.id))

    return [
        CategoryResponse(
            _id=str(cat.id),
            user_id=str(cat.user_id),
            nombre=cat.nombre,
            tipo=cat.tipo,
            color=cat.color,
            icono=cat.icono,
            subcategorias=cat.subcategorias,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        )
        for cat in categories
    ]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Obtener una categoría específica por ID.
    """
    category_crud = CategoryCRUD(db)
    category = await category_crud.get_by_id(category_id, str(current_user.id))

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    return CategoryResponse(
        _id=str(category.id),
        user_id=str(category.user_id),
        nombre=category.nombre,
        tipo=category.tipo,
        color=category.color,
        icono=category.icono,
        subcategorias=category.subcategorias,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    update_data: CategoryUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Actualizar una categoría existente.
    """
    category_crud = CategoryCRUD(db)
    category = await category_crud.update(category_id, str(current_user.id), update_data)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    return CategoryResponse(
        _id=str(category.id),
        user_id=str(category.user_id),
        nombre=category.nombre,
        tipo=category.tipo,
        color=category.color,
        icono=category.icono,
        subcategorias=category.subcategorias,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Eliminar una categoría.

    No se puede eliminar si tiene gastos asociados.
    """
    category_crud = CategoryCRUD(db)

    # TODO: Verificar que no tenga gastos asociados antes de eliminar

    deleted = await category_crud.delete(category_id, str(current_user.id))

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    return None
