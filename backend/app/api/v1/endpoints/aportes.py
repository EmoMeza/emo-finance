from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.database import get_database
from app.api.dependencies import get_current_active_user
from app.crud.aporte import AporteCRUD
from app.crud.period import PeriodCRUD
from app.models.user import UserInDB
from app.models.aporte import (
    AporteCreate,
    AporteUpdate,
    AporteResponse
)

router = APIRouter()


@router.post("/", response_model=AporteResponse, status_code=status.HTTP_201_CREATED)
async def create_aporte(
    aporte: AporteCreate,
    periodo_id: str = Query(..., description="ID del período al que pertenece"),
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Crear un nuevo aporte

    Los aportes son ingresos adicionales que REDUCEN el total de gastos de una categoría.
    Fórmula: total_categoria = gastos - aportes

    Tipos de aportes:
    - es_fijo=True: Se copia cada período (ej: aporte mensual de pareja)
    - es_fijo=False: Aporte único del período, no se copia (ej: venta de celular)
    """
    # Verificar que el período existe y pertenece al usuario
    period_crud = PeriodCRUD(db)
    period = await period_crud.get_by_id(str(current_user.id), periodo_id)

    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )

    aporte_crud = AporteCRUD(db)
    created = await aporte_crud.create(str(current_user.id), periodo_id, aporte)

    return AporteResponse(
        _id=str(created.id),
        user_id=str(created.user_id),
        periodo_id=str(created.periodo_id),
        categoria_id=str(created.categoria_id),
        nombre=created.nombre,
        monto=created.monto,
        es_fijo=created.es_fijo,
        descripcion=created.descripcion,
        fecha_registro=created.fecha_registro,
        created_at=created.created_at,
        updated_at=created.updated_at
    )


@router.get("/", response_model=List[AporteResponse])
async def get_aportes(
    periodo_id: str = Query(..., description="ID del período"),
    es_fijo: Optional[bool] = Query(None, description="Filtrar por tipo (true=fijo, false=variable)"),
    categoria_id: Optional[str] = Query(None, description="Filtrar por categoría"),
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener todos los aportes de un período

    Filtros opcionales:
    - es_fijo: True para aportes fijos, False para variables
    - categoria_id: ID de la categoría
    """
    aporte_crud = AporteCRUD(db)
    aportes = await aporte_crud.get_by_periodo(
        str(current_user.id),
        periodo_id,
        es_fijo=es_fijo,
        categoria_id=categoria_id
    )

    return [
        AporteResponse(
            _id=str(ap.id),
            user_id=str(ap.user_id),
            periodo_id=str(ap.periodo_id),
            categoria_id=str(ap.categoria_id),
            nombre=ap.nombre,
            monto=ap.monto,
            es_fijo=ap.es_fijo,
            descripcion=ap.descripcion,
            fecha_registro=ap.fecha_registro,
            created_at=ap.created_at,
            updated_at=ap.updated_at
        )
        for ap in aportes
    ]


@router.get("/{aporte_id}", response_model=AporteResponse)
async def get_aporte(
    aporte_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener un aporte por ID
    """
    aporte_crud = AporteCRUD(db)
    aporte = await aporte_crud.get_by_id(str(current_user.id), aporte_id)

    if not aporte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aporte not found"
        )

    return AporteResponse(
        _id=str(aporte.id),
        user_id=str(aporte.user_id),
        periodo_id=str(aporte.periodo_id),
        categoria_id=str(aporte.categoria_id),
        nombre=aporte.nombre,
        monto=aporte.monto,
        es_fijo=aporte.es_fijo,
        descripcion=aporte.descripcion,
        fecha_registro=aporte.fecha_registro,
        created_at=aporte.created_at,
        updated_at=aporte.updated_at
    )


@router.put("/{aporte_id}", response_model=AporteResponse)
async def update_aporte(
    aporte_id: str,
    aporte_update: AporteUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Actualizar un aporte
    Solo permite editar nombre, monto y descripción
    """
    aporte_crud = AporteCRUD(db)
    updated = await aporte_crud.update(str(current_user.id), aporte_id, aporte_update)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aporte not found"
        )

    return AporteResponse(
        _id=str(updated.id),
        user_id=str(updated.user_id),
        periodo_id=str(updated.periodo_id),
        categoria_id=str(updated.categoria_id),
        nombre=updated.nombre,
        monto=updated.monto,
        es_fijo=updated.es_fijo,
        descripcion=updated.descripcion,
        fecha_registro=updated.fecha_registro,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )


@router.delete("/{aporte_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_aporte(
    aporte_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Eliminar un aporte
    """
    aporte_crud = AporteCRUD(db)
    deleted = await aporte_crud.delete(str(current_user.id), aporte_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aporte not found"
        )

    return None
