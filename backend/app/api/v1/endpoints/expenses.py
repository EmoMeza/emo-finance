from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.database import get_database
from app.api.dependencies import get_current_active_user
from app.crud.expense import ExpenseCRUD
from app.crud.period import PeriodCRUD
from app.models.user import UserInDB
from app.models.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    TipoGasto
)

router = APIRouter()


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseCreate,
    periodo_id: str = Query(..., description="ID del período al que pertenece"),
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Crear un nuevo gasto

    Tipos de gastos:
    - FIJO + es_permanente=True: Se copia cada período (ej: Netflix, Spotify)
    - FIJO + es_permanente=False: Se copia mientras periodos_restantes > 0 (ej: cuotas)
    - VARIABLE: Gasto único del período, no se copia (ej: pizza, regalo)
    """
    # Verificar que el período existe y pertenece al usuario
    period_crud = PeriodCRUD(db)
    period = await period_crud.get_by_id(str(current_user.id), periodo_id)

    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )

    expense_crud = ExpenseCRUD(db)
    created = await expense_crud.create(str(current_user.id), periodo_id, expense)

    # Si es un período de crédito, actualizar total_gastado
    if period.tipo_periodo == "ciclo_credito":
        period_crud.expense_crud = expense_crud
        await period_crud.update_total_gastado(str(current_user.id), periodo_id)

    return ExpenseResponse(
        _id=str(created.id),
        user_id=str(created.user_id),
        periodo_id=str(created.periodo_id),
        categoria_id=str(created.categoria_id),
        nombre=created.nombre,
        monto=created.monto,
        tipo=created.tipo,
        es_permanente=created.es_permanente,
        periodos_restantes=created.periodos_restantes,
        descripcion=created.descripcion,
        fecha_registro=created.fecha_registro,
        created_at=created.created_at,
        updated_at=created.updated_at
    )


@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    periodo_id: str = Query(..., description="ID del período"),
    tipo: Optional[TipoGasto] = Query(None, description="Filtrar por tipo (fijo o variable)"),
    categoria_id: Optional[str] = Query(None, description="Filtrar por categoría"),
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener todos los gastos de un período

    Filtros opcionales:
    - tipo: TipoGasto.FIJO o TipoGasto.VARIABLE
    - categoria_id: ID de la categoría
    """
    expense_crud = ExpenseCRUD(db)
    expenses = await expense_crud.get_by_periodo(
        str(current_user.id),
        periodo_id,
        tipo=tipo,
        categoria_id=categoria_id
    )

    return [
        ExpenseResponse(
            _id=str(exp.id),
            user_id=str(exp.user_id),
            periodo_id=str(exp.periodo_id),
            categoria_id=str(exp.categoria_id),
            nombre=exp.nombre,
            monto=exp.monto,
            tipo=exp.tipo,
            es_permanente=exp.es_permanente,
            periodos_restantes=exp.periodos_restantes,
            descripcion=exp.descripcion,
            fecha_registro=exp.fecha_registro,
            created_at=exp.created_at,
            updated_at=exp.updated_at
        )
        for exp in expenses
    ]


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Obtener un gasto por ID
    """
    expense_crud = ExpenseCRUD(db)
    expense = await expense_crud.get_by_id(str(current_user.id), expense_id)

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    return ExpenseResponse(
        _id=str(expense.id),
        user_id=str(expense.user_id),
        periodo_id=str(expense.periodo_id),
        categoria_id=str(expense.categoria_id),
        nombre=expense.nombre,
        monto=expense.monto,
        tipo=expense.tipo,
        es_permanente=expense.es_permanente,
        periodos_restantes=expense.periodos_restantes,
        descripcion=expense.descripcion,
        fecha_registro=expense.fecha_registro,
        created_at=expense.created_at,
        updated_at=expense.updated_at
    )


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    expense_update: ExpenseUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Actualizar un gasto
    Solo permite editar nombre, monto y descripción
    """
    expense_crud = ExpenseCRUD(db)

    # Obtener gasto antes de actualizar para saber su período
    old_expense = await expense_crud.get_by_id(str(current_user.id), expense_id)
    if not old_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    updated = await expense_crud.update(str(current_user.id), expense_id, expense_update)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Si es un período de crédito, actualizar total_gastado
    period_crud = PeriodCRUD(db)
    period = await period_crud.get_by_id(str(current_user.id), str(old_expense.periodo_id))

    if period and period.tipo_periodo == "ciclo_credito":
        period_crud.expense_crud = expense_crud
        await period_crud.update_total_gastado(str(current_user.id), str(old_expense.periodo_id))

    return ExpenseResponse(
        _id=str(updated.id),
        user_id=str(updated.user_id),
        periodo_id=str(updated.periodo_id),
        categoria_id=str(updated.categoria_id),
        nombre=updated.nombre,
        monto=updated.monto,
        tipo=updated.tipo,
        es_permanente=updated.es_permanente,
        periodos_restantes=updated.periodos_restantes,
        descripcion=updated.descripcion,
        fecha_registro=updated.fecha_registro,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
    db=Depends(get_database)
):
    """
    Eliminar un gasto
    """
    expense_crud = ExpenseCRUD(db)

    # Obtener gasto antes de eliminar para saber su período
    expense = await expense_crud.get_by_id(str(current_user.id), expense_id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    deleted = await expense_crud.delete(str(current_user.id), expense_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    # Si es un período de crédito, actualizar total_gastado
    period_crud = PeriodCRUD(db)
    period = await period_crud.get_by_id(str(current_user.id), str(expense.periodo_id))

    if period and period.tipo_periodo == "ciclo_credito":
        period_crud.expense_crud = expense_crud
        await period_crud.update_total_gastado(str(current_user.id), str(expense.periodo_id))

    return None
