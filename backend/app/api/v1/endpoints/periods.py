from typing import List, Optional
from datetime import datetime
from calendar import monthrange
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from bson import ObjectId
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
    PeriodCloseRequest,
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

    return period_to_response(created)


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

    return period_to_response(period)


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

    return [period_to_response(per) for per in periods]


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

    return period_to_response(period)


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
    categoria_ahorro_id = None
    categoria_arriendo_id = None
    categoria_liquidez_id = None

    # Obtener el período de crédito activo para calcular gastos de crédito
    periodo_credito = await period_crud.get_active(
        str(current_user.id),
        TipoPeriodo.CICLO_CREDITO
    )

    for cat in categories:
        cat_id = str(cat.id)

        # Para Crédito, usar el período de crédito; para el resto, usar el período mensual
        periodo_para_gastos = period_id
        if cat.slug == TipoCategoria.CREDITO and periodo_credito:
            periodo_para_gastos = str(periodo_credito.id)

        # Calcular totales
        total_gastos = await expense_crud.calculate_total_by_categoria(
            str(current_user.id), periodo_para_gastos, cat_id
        )

        total_aportes = await aporte_crud.calculate_total_by_categoria(
            str(current_user.id), periodo_para_gastos, cat_id
        )

        total_real = total_gastos - total_aportes

        # DEBUG: Log de totales por categoría
        print(f"DEBUG: Categoría {cat.nombre} ({cat.slug}): periodo_usado={periodo_para_gastos}, gastos=${total_gastos}, aportes=${total_aportes}, total_real=${total_real}")

        # Guardar IDs de categorías ahorro, arriendo y liquidez para calcular liquidez
        if cat.slug == TipoCategoria.AHORRO:
            categoria_ahorro_id = cat_id
        elif cat.slug == TipoCategoria.ARRIENDO:
            categoria_arriendo_id = cat_id
        elif cat.slug == TipoCategoria.LIQUIDEZ:
            categoria_liquidez_id = cat_id

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
    if period.tipo_periodo == TipoPeriodo.MENSUAL_ESTANDAR and categoria_ahorro_id and categoria_arriendo_id:
        liquidez_calculada = await period_crud.calculate_liquidez(
            str(current_user.id),
            period,
            categoria_ahorro_id,
            categoria_arriendo_id,
            categoria_liquidez_id
        )

    return PeriodSummaryResponse(
        period=period_to_response(period),
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

    return period_to_response(updated)


@router.post("/{period_id}/close", response_model=PeriodResponse)
async def close_period(
    period_id: str,
    close_request: Optional[PeriodCloseRequest] = None,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Cerrar un período (marcar como CERRADO)

    Un período cerrado se mantiene para historial y sus gastos/aportes fijos
    se copian al crear el siguiente período.

    Opcionalmente se puede especificar una fecha_fin personalizada para ajustar
    el día de cierre (útil para diferentes fechas de cierre de tarjetas de crédito).
    """
    period_crud = PeriodCRUD(db)
    fecha_fin_custom = close_request.fecha_fin if close_request else None
    closed = await period_crud.close_period(str(current_user.id), period_id, fecha_fin_custom)

    if not closed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )

    return period_to_response(closed)


class RepairResult(BaseModel):
    """Resultado de la reparación del período mensual"""
    repaired: bool = False
    fechas: Optional[str] = None
    sueldo: Optional[str] = None
    fijos_copiados: Optional[str] = None
    error: Optional[str] = None


@router.post("/repair", response_model=RepairResult)
async def repair_current_periods(
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Reparar el período mensual activo del usuario.

    Recalcula de base el mes actual manteniendo el sueldo:
    1. Verifica y corrige las fechas del período mensual
    2. Recupera sueldo del período anterior si el actual está en 0
    3. Copia gastos fijos y aportes fijos del período anterior si faltan
       (ahorro, arriendo, etc. heredan sus fijos del mes pasado)

    La liquidez se recalcula automáticamente al consultar el summary,
    restando ahorro, arriendo y el último crédito cerrado.
    """
    expense_crud = ExpenseCRUD(db)
    aporte_crud = AporteCRUD(db)
    period_crud = PeriodCRUD(db, expense_crud=expense_crud, aporte_crud=aporte_crud)
    user_id = str(current_user.id)

    result = RepairResult()

    try:
        mensual = await period_crud.get_active(user_id, TipoPeriodo.MENSUAL_ESTANDAR)
        if not mensual:
            result.error = "No se encontró período mensual activo"
            return result

        mensual_id = str(mensual.id)

        # 1. Corregir fechas del período
        now = datetime.utcnow()
        expected_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = monthrange(now.year, now.month)[1]
        expected_end = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

        if mensual.fecha_inicio != expected_start or mensual.fecha_fin != expected_end:
            await period_crud.collection.update_one(
                {"_id": mensual.id, "user_id": ObjectId(user_id)},
                {"$set": {
                    "fecha_inicio": expected_start,
                    "fecha_fin": expected_end,
                    "updated_at": datetime.utcnow()
                }}
            )
            result.fechas = f"Corregidas: {expected_start.date()} - {expected_end.date()}"
        else:
            result.fechas = f"OK: {mensual.fecha_inicio.date()} - {mensual.fecha_fin.date()}"

        # 2. Recuperar sueldo del período anterior si el actual es 0
        previous = await period_crud._get_previous_period(user_id, TipoPeriodo.MENSUAL_ESTANDAR)

        if mensual.sueldo == 0 and previous and previous.sueldo > 0:
            await period_crud.collection.update_one(
                {"_id": mensual.id, "user_id": ObjectId(user_id)},
                {"$set": {
                    "sueldo": previous.sueldo,
                    "metas_categorias": previous.metas_categorias.model_dump(),
                    "updated_at": datetime.utcnow()
                }}
            )
            result.sueldo = f"Recuperado: ${previous.sueldo:,.0f}"
        elif mensual.sueldo > 0:
            result.sueldo = f"OK: ${mensual.sueldo:,.0f}"
        else:
            result.sueldo = "Sin sueldo configurado"

        # 3. Copiar gastos fijos y aportes fijos del período anterior si faltan
        if previous:
            previous_id = str(previous.id)
            gastos_copiados = 0
            aportes_copiados = 0

            # Contar gastos fijos del período actual
            gastos_fijos_count = len(await expense_crud.get_fijos_permanentes(user_id, mensual_id))
            gastos_fijos_count += len(await expense_crud.get_fijos_temporales_activos(user_id, mensual_id))

            # Si no hay fijos en el actual pero sí en el anterior, copiarlos
            prev_fijos_perm = await expense_crud.get_fijos_permanentes(user_id, previous_id)
            prev_fijos_temp = await expense_crud.get_fijos_temporales_activos(user_id, previous_id)
            prev_aportes_fijos = await aporte_crud.get_fijos(user_id, previous_id)

            if gastos_fijos_count == 0 and (len(prev_fijos_perm) > 0 or len(prev_fijos_temp) > 0):
                # Copiar gastos fijos del período anterior
                await period_crud._copy_fixed_items(user_id, previous, mensual)
                gastos_copiados = len(prev_fijos_perm) + len(prev_fijos_temp)
                aportes_copiados = len(prev_aportes_fijos)
            else:
                # Verificar aportes fijos por separado
                aportes_fijos_count = len(await aporte_crud.get_fijos(user_id, mensual_id))
                if aportes_fijos_count == 0 and len(prev_aportes_fijos) > 0:
                    # Solo copiar aportes fijos
                    from app.models.aporte import AporteCreate
                    for aporte in prev_aportes_fijos:
                        aporte_create = AporteCreate(
                            nombre=aporte.nombre,
                            monto=aporte.monto,
                            categoria_id=aporte.categoria_id,
                            es_fijo=True,
                            descripcion=aporte.descripcion
                        )
                        await aporte_crud.create(user_id, mensual_id, aporte_create)
                        aportes_copiados += 1

            if gastos_copiados > 0 or aportes_copiados > 0:
                result.fijos_copiados = f"{gastos_copiados} gastos fijos + {aportes_copiados} aportes fijos copiados"
            else:
                result.fijos_copiados = "OK: fijos ya presentes"
        else:
            result.fijos_copiados = "Sin período anterior"

        result.repaired = True

    except Exception as e:
        result.error = f"Error: {str(e)}"

    return result


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
