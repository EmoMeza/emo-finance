from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from app.core.database import get_database
from app.api.dependencies import get_current_active_user
from app.crud.period import PeriodCRUD
from app.crud.category import CategoryCRUD
from app.crud.expense import ExpenseCRUD
from app.crud.aporte import AporteCRUD
from app.models.user import UserInDB
from app.models.period import (
    PeriodCreate,
    PeriodUpdate,
    PeriodResponse,
    PeriodInDB,
    TipoPeriodo,
    EstadoPeriodo
)
from app.models.category import TipoCategoria

router = APIRouter()


# ====================
# HELPER FUNCTIONS
# ====================

def period_to_response(period: 'PeriodInDB') -> PeriodResponse:
    """Convertir PeriodInDB a PeriodResponse"""
    return PeriodResponse(
        _id=str(period.id),
        user_id=str(period.user_id),
        tipo_periodo=period.tipo_periodo,
        fecha_inicio=period.fecha_inicio,
        fecha_fin=period.fecha_fin,
        sueldo=period.sueldo,
        metas_categorias=period.metas_categorias,
        estado=period.estado,
        categorias=[str(cat_id) for cat_id in (period.categorias if hasattr(period, 'categorias') and period.categorias else [])],
        total_gastado=period.total_gastado,
        created_at=period.created_at,
        updated_at=period.updated_at
    )


# ====================
# SCHEMAS ADICIONALES
# ====================

class CategorySummary(BaseModel):
    """Resumen de una categoría con gastos y aportes"""
    categoria_id: str
    categoria_slug: TipoCategoria
    categoria_nombre: str
    total_gastos: float
    total_aportes: float
    total_real: float  # gastos - aportes
    meta: Optional[float] = None  # Solo para categorías con meta


class PeriodSummaryResponse(BaseModel):
    """Resumen completo del período con todas las categorías"""
    period: PeriodResponse
    categories_summary: List[CategorySummary]
    liquidez_calculada: float


# ====================
# ENDPOINTS
# ====================

@router.post("/", response_model=PeriodResponse, status_code=status.HTTP_201_CREATED)
async def create_period(
    period: PeriodCreate,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Crear un nuevo período manualmente

    Generalmente los períodos se crean automáticamente, pero este endpoint
    permite crear uno manualmente si es necesario.
    """
    period_crud = PeriodCRUD(db)
    created = await period_crud.create(str(current_user.id), period)

    return PeriodResponse(
        _id=str(created.id),
        user_id=str(created.user_id),
        tipo_periodo=created.tipo_periodo,
        fecha_inicio=created.fecha_inicio,
        fecha_fin=created.fecha_fin,
        sueldo=created.sueldo,
        metas_categorias=created.metas_categorias,
        estado=created.estado,
        categorias=[str(cat_id) for cat_id in (created.categorias if hasattr(created, 'categorias') and created.categorias else [])],
        total_gastado=created.total_gastado,
        created_at=created.created_at,
        updated_at=created.updated_at
    )


@router.get("/active", response_model=PeriodResponse)
async def get_active_period(
    tipo_periodo: TipoPeriodo = Query(..., description="Tipo de período (mensual_estandar o ciclo_credito)"),
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener el período activo del tipo especificado

    Si no existe, lo crea automáticamente según LOGICA_SISTEMA.md:
    - Períodos mensuales: del 1 al último día del mes
    - Períodos de crédito: del 25 al 24
    """
    expense_crud = ExpenseCRUD(db)
    aporte_crud = AporteCRUD(db)

    period_crud = PeriodCRUD(db, expense_crud=expense_crud, aporte_crud=aporte_crud)
    period = await period_crud.get_active(str(current_user.id), tipo_periodo)

    return PeriodResponse(
        _id=str(period.id),
        user_id=str(period.user_id),
        tipo_periodo=period.tipo_periodo,
        fecha_inicio=period.fecha_inicio,
        fecha_fin=period.fecha_fin,
        sueldo=period.sueldo,
        metas_categorias=period.metas_categorias,
        estado=period.estado,
        total_gastado=period.total_gastado,
        created_at=period.created_at,
        updated_at=period.updated_at
    )


@router.get("/", response_model=List[PeriodResponse])
async def get_periods(
    tipo_periodo: Optional[TipoPeriodo] = Query(None, description="Filtrar por tipo"),
    estado: Optional[EstadoPeriodo] = Query(None, description="Filtrar por estado"),
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener todos los períodos del usuario con filtros opcionales

    Filtros:
    - tipo_periodo: mensual_estandar o ciclo_credito
    - estado: activo, cerrado o proyectado
    """
    period_crud = PeriodCRUD(db)
    periods = await period_crud.get_all(
        str(current_user.id),
        tipo_periodo=tipo_periodo,
        estado=estado
    )

    return [
        PeriodResponse(
            _id=str(per.id),
            user_id=str(per.user_id),
            tipo_periodo=per.tipo_periodo,
            fecha_inicio=per.fecha_inicio,
            fecha_fin=per.fecha_fin,
            sueldo=per.sueldo,
            metas_categorias=per.metas_categorias,
            estado=per.estado,
            total_gastado=per.total_gastado,
            created_at=per.created_at,
            updated_at=per.updated_at
        )
        for per in periods
    ]


@router.get("/{period_id}", response_model=PeriodResponse)
async def get_period(
    period_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener un período por ID
    """
    period_crud = PeriodCRUD(db)
    period = await period_crud.get_by_id(str(current_user.id), period_id)

    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )

    return PeriodResponse(
        _id=str(period.id),
        user_id=str(period.user_id),
        tipo_periodo=period.tipo_periodo,
        fecha_inicio=period.fecha_inicio,
        fecha_fin=period.fecha_fin,
        sueldo=period.sueldo,
        metas_categorias=period.metas_categorias,
        estado=period.estado,
        total_gastado=period.total_gastado,
        created_at=period.created_at,
        updated_at=period.updated_at
    )


@router.get("/{period_id}/summary", response_model=PeriodSummaryResponse)
async def get_period_summary(
    period_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener resumen completo del período con desglose de todas las categorías

    Incluye:
    - Información del período
    - Total de gastos y aportes por categoría
    - Total real por categoría (gastos - aportes)
    - Liquidez calculada
    """
    expense_crud = ExpenseCRUD(db)
    aporte_crud = AporteCRUD(db)
    period_crud = PeriodCRUD(db, expense_crud=expense_crud, aporte_crud=aporte_crud)
    category_crud = CategoryCRUD(db)

    # Obtener período
    period = await period_crud.get_by_id(str(current_user.id), period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )

    # Obtener categorías
    categories = await category_crud.get_all(str(current_user.id))

    # Calcular resumen por categoría
    categories_summary = []
    categoria_arriendo_id = None

    for cat in categories:
        cat_id = str(cat.id)

        # Calcular totales
        total_gastos = await expense_crud.calculate_total_by_categoria(
            str(current_user.id), period_id, cat_id
        )

        total_aportes = await aporte_crud.calculate_total_by_categoria(
            str(current_user.id), period_id, cat_id
        )

        total_real = total_gastos - total_aportes

        # Guardar ID de categoría arriendo para calcular liquidez
        if cat.slug == TipoCategoria.ARRIENDO:
            categoria_arriendo_id = cat_id

        # Obtener meta si aplica
        # NOTA: Solo Crédito tiene meta real. Ahorro y Arriendo usan total_real como "meta"
        meta = None
        if cat.tiene_meta:
            if cat.slug == TipoCategoria.CREDITO:
                meta = period.metas_categorias.credito_usable
            else:
                # Para Ahorro y Arriendo, la "meta" es el total_real calculado
                meta = total_real

        categories_summary.append(
            CategorySummary(
                categoria_id=cat_id,
                categoria_slug=cat.slug,
                categoria_nombre=cat.nombre,
                total_gastos=total_gastos,
                total_aportes=total_aportes,
                total_real=total_real,
                meta=meta
            )
        )

    # Calcular liquidez
    liquidez_calculada = 0.0
    if period.tipo_periodo == TipoPeriodo.MENSUAL_ESTANDAR and categoria_arriendo_id:
        liquidez_calculada = await period_crud.calculate_liquidez(
            str(current_user.id),
            period,
            categoria_arriendo_id
        )

    return PeriodSummaryResponse(
        period=PeriodResponse(
            _id=str(period.id),
            user_id=str(period.user_id),
            tipo_periodo=period.tipo_periodo,
            fecha_inicio=period.fecha_inicio,
            fecha_fin=period.fecha_fin,
            sueldo=period.sueldo,
            metas_categorias=period.metas_categorias,
            estado=period.estado,
            total_gastado=period.total_gastado,
            created_at=period.created_at,
            updated_at=period.updated_at
        ),
        categories_summary=categories_summary,
        liquidez_calculada=liquidez_calculada
    )


@router.put("/{period_id}", response_model=PeriodResponse)
async def update_period(
    period_id: str,
    period_update: PeriodUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Actualizar un período
    Permite editar sueldo, metas, estado y total_gastado
    """
    period_crud = PeriodCRUD(db)
    updated = await period_crud.update(str(current_user.id), period_id, period_update)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )

    return PeriodResponse(
        _id=str(updated.id),
        user_id=str(updated.user_id),
        tipo_periodo=updated.tipo_periodo,
        fecha_inicio=updated.fecha_inicio,
        fecha_fin=updated.fecha_fin,
        sueldo=updated.sueldo,
        metas_categorias=updated.metas_categorias,
        estado=updated.estado,
        total_gastado=updated.total_gastado,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )


@router.post("/{period_id}/close", response_model=PeriodResponse)
async def close_period(
    period_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Cerrar un período (marcar como CERRADO)

    Un período cerrado se mantiene para historial y sus gastos/aportes fijos
    se copian al crear el siguiente período.
    """
    period_crud = PeriodCRUD(db)
    closed = await period_crud.close_period(str(current_user.id), period_id)

    if not closed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )

    return PeriodResponse(
        _id=str(closed.id),
        user_id=str(closed.user_id),
        tipo_periodo=closed.tipo_periodo,
        fecha_inicio=closed.fecha_inicio,
        fecha_fin=closed.fecha_fin,
        sueldo=closed.sueldo,
        metas_categorias=closed.metas_categorias,
        estado=closed.estado,
        total_gastado=closed.total_gastado,
        created_at=closed.created_at,
        updated_at=closed.updated_at
    )


@router.delete("/{period_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_period(
    period_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Eliminar un período

    NOTA: En producción, probablemente NO se deberían eliminar períodos
    para mantener historial.
    """
    period_crud = PeriodCRUD(db)
    deleted = await period_crud.delete(str(current_user.id), period_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )

    return None
