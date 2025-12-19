from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.database import get_database
from app.api.dependencies import get_current_user
from app.crud.period import PeriodCRUD
from app.models.user import UserInDB
from app.models.period import (
    PeriodCreate,
    PeriodUpdate,
    PeriodResponse,
    PeriodSummary,
    EstadoPeriodo,
    TipoPeriodo
)
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=PeriodResponse, status_code=status.HTTP_201_CREATED)
async def create_period(
    period_data: PeriodCreate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Crear un nuevo período.

    - Valida que no exista otro período activo del mismo tipo
    - Calcula automáticamente el líquido
    - Asigna el período al usuario actual
    """
    period_crud = PeriodCRUD(db)

    # Verificar si ya existe un período activo del mismo tipo
    has_active = await period_crud.has_active_period(
        str(current_user.id),
        period_data.tipo_periodo
    )

    if has_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un período activo de tipo {period_data.tipo_periodo}"
        )

    # Validar que la suma de metas no exceda el sueldo
    total_metas = (
        period_data.metas_categorias.ahorro +
        period_data.metas_categorias.arriendo +
        period_data.metas_categorias.credito_usable
    )

    if total_metas > period_data.sueldo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La suma de metas (${total_metas}) excede el sueldo (${period_data.sueldo})"
        )

    # Crear el período
    period = await period_crud.create(str(current_user.id), period_data)

    # Calcular líquido
    liquido = period_crud.calculate_liquido(
        period.sueldo,
        period.metas_categorias.model_dump()
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
        liquido_calculado=liquido,
        created_at=period.created_at,
        updated_at=period.updated_at
    )


@router.get("/", response_model=List[PeriodResponse])
async def get_periods(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: Optional[EstadoPeriodo] = None,
    tipo_periodo: Optional[TipoPeriodo] = None,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Obtener todos los períodos del usuario con paginación y filtros.
    """
    period_crud = PeriodCRUD(db)
    periods = await period_crud.get_all(
        str(current_user.id),
        skip=skip,
        limit=limit,
        estado=estado,
        tipo_periodo=tipo_periodo
    )

    result = []
    for period in periods:
        liquido = period_crud.calculate_liquido(
            period.sueldo,
            period.metas_categorias.model_dump()
        )

        result.append(PeriodResponse(
            _id=str(period.id),
            user_id=str(period.user_id),
            tipo_periodo=period.tipo_periodo,
            fecha_inicio=period.fecha_inicio,
            fecha_fin=period.fecha_fin,
            sueldo=period.sueldo,
            metas_categorias=period.metas_categorias,
            estado=period.estado,
            liquido_calculado=liquido,
            created_at=period.created_at,
            updated_at=period.updated_at
        ))

    return result


@router.get("/active", response_model=PeriodResponse)
async def get_active_period(
    tipo_periodo: Optional[TipoPeriodo] = None,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Obtener el período activo del usuario.

    - Si se especifica tipo_periodo, busca el período activo de ese tipo
    - Si no, devuelve el primer período activo encontrado
    """
    period_crud = PeriodCRUD(db)
    period = await period_crud.get_active_period(str(current_user.id), tipo_periodo)

    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay período activo"
        )

    # Para períodos mensuales, obtener la deuda del período de crédito anterior
    deuda_credito_anterior = 0
    if period.tipo_periodo == TipoPeriodo.MENSUAL_ESTANDAR:
        previous_credit = await period_crud.get_previous_credit_period(str(current_user.id))
        if previous_credit:
            deuda_credito_anterior = previous_credit.total_gastado

    liquido = period_crud.calculate_liquido(
        period.sueldo,
        period.metas_categorias.model_dump(),
        deuda_credito_anterior
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
        liquido_calculado=liquido,
        created_at=period.created_at,
        updated_at=period.updated_at
    )


@router.get("/{period_id}", response_model=PeriodResponse)
async def get_period(
    period_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Obtener un período específico por ID.
    """
    period_crud = PeriodCRUD(db)
    period = await period_crud.get_by_id(period_id, str(current_user.id))

    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Período no encontrado"
        )

    liquido = period_crud.calculate_liquido(
        period.sueldo,
        period.metas_categorias.model_dump()
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
        liquido_calculado=liquido,
        created_at=period.created_at,
        updated_at=period.updated_at
    )


@router.put("/{period_id}", response_model=PeriodResponse)
async def update_period(
    period_id: str,
    update_data: PeriodUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Actualizar un período existente.

    - Solo se pueden actualizar períodos activos o proyectados
    - Valida que la suma de metas no exceda el sueldo
    """
    period_crud = PeriodCRUD(db)

    # Verificar que el período existe
    existing_period = await period_crud.get_by_id(period_id, str(current_user.id))
    if not existing_period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Período no encontrado"
        )

    # No permitir actualizar períodos cerrados
    if existing_period.estado == EstadoPeriodo.CERRADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede actualizar un período cerrado"
        )

    # Validar suma de metas si se están actualizando
    if update_data.metas_categorias or update_data.sueldo:
        sueldo = update_data.sueldo if update_data.sueldo else existing_period.sueldo
        metas = update_data.metas_categorias if update_data.metas_categorias else existing_period.metas_categorias

        total_metas = metas.ahorro + metas.arriendo + metas.credito_usable

        if total_metas > sueldo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La suma de metas (${total_metas}) excede el sueldo (${sueldo})"
            )

    # Actualizar
    period = await period_crud.update(period_id, str(current_user.id), update_data)

    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Período no encontrado"
        )

    liquido = period_crud.calculate_liquido(
        period.sueldo,
        period.metas_categorias.model_dump()
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
        liquido_calculado=liquido,
        created_at=period.created_at,
        updated_at=period.updated_at
    )


@router.post("/{period_id}/close", response_model=PeriodResponse)
async def close_period(
    period_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Cerrar un período.

    - Cambia el estado a 'cerrado'
    - No se puede reabrir un período cerrado
    """
    period_crud = PeriodCRUD(db)
    period = await period_crud.close_period(period_id, str(current_user.id))

    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Período no encontrado"
        )

    liquido = period_crud.calculate_liquido(
        period.sueldo,
        period.metas_categorias.model_dump()
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
        liquido_calculado=liquido,
        created_at=period.created_at,
        updated_at=period.updated_at
    )


@router.delete("/{period_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_period(
    period_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Eliminar un período.

    - Solo se pueden eliminar períodos que no estén cerrados
    - Se eliminarán en cascada todos los gastos asociados
    """
    period_crud = PeriodCRUD(db)

    # Verificar que existe y no está cerrado
    period = await period_crud.get_by_id(period_id, str(current_user.id))
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Período no encontrado"
        )

    if period.estado == EstadoPeriodo.CERRADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un período cerrado"
        )

    deleted = await period_crud.delete(period_id, str(current_user.id))

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Período no encontrado"
        )

    return None
