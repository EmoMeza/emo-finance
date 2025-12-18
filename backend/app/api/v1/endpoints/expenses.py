from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.core.database import get_database
from app.api.dependencies import get_current_user
from app.crud.expense import ExpenseCRUD
from app.models.user import UserInDB
from app.models.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, TipoGasto, EstadoGasto

router = APIRouter()


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Crear un nuevo gasto.

    - El gasto se asigna al período especificado
    - Se valida que el período y la categoría existan y pertenezcan al usuario
    """
    expense_crud = ExpenseCRUD(db)

    # TODO: Validar que el período y la categoría existan y pertenezcan al usuario

    expense = await expense_crud.create(str(current_user.id), expense_data)

    return ExpenseResponse(
        _id=str(expense.id),
        user_id=str(expense.user_id),
        periodo_id=str(expense.periodo_id),
        plantilla_id=str(expense.plantilla_id) if expense.plantilla_id else None,
        nombre=expense.nombre,
        valor=expense.valor,
        fecha=expense.fecha,
        categoria_id=str(expense.categoria_id),
        subcategoria_nombre=expense.subcategoria_nombre,
        tipo=expense.tipo,
        metodo_pago=expense.metodo_pago,
        estado=expense.estado,
        notas=expense.notas,
        created_at=expense.created_at,
        updated_at=expense.updated_at
    )


@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    periodo_id: Optional[str] = None,
    categoria_id: Optional[str] = None,
    tipo: Optional[TipoGasto] = None,
    estado: Optional[EstadoGasto] = None,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Obtener gastos con filtros opcionales.

    - Filtrar por período, categoría, tipo y/o estado
    """
    expense_crud = ExpenseCRUD(db)

    if periodo_id:
        expenses = await expense_crud.get_by_period(
            str(current_user.id),
            periodo_id,
            tipo=tipo,
            estado=estado
        )
    elif categoria_id:
        expenses = await expense_crud.get_by_category(
            str(current_user.id),
            categoria_id
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar al menos periodo_id o categoria_id"
        )

    return [
        ExpenseResponse(
            _id=str(exp.id),
            user_id=str(exp.user_id),
            periodo_id=str(exp.periodo_id),
            plantilla_id=str(exp.plantilla_id) if exp.plantilla_id else None,
            nombre=exp.nombre,
            valor=exp.valor,
            fecha=exp.fecha,
            categoria_id=str(exp.categoria_id),
            subcategoria_nombre=exp.subcategoria_nombre,
            tipo=exp.tipo,
            metodo_pago=exp.metodo_pago,
            estado=exp.estado,
            notas=exp.notas,
            created_at=exp.created_at,
            updated_at=exp.updated_at
        )
        for exp in expenses
    ]


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Obtener un gasto específico por ID.
    """
    expense_crud = ExpenseCRUD(db)
    expense = await expense_crud.get_by_id(expense_id, str(current_user.id))

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )

    return ExpenseResponse(
        _id=str(expense.id),
        user_id=str(expense.user_id),
        periodo_id=str(expense.periodo_id),
        plantilla_id=str(expense.plantilla_id) if expense.plantilla_id else None,
        nombre=expense.nombre,
        valor=expense.valor,
        fecha=expense.fecha,
        categoria_id=str(expense.categoria_id),
        subcategoria_nombre=expense.subcategoria_nombre,
        tipo=expense.tipo,
        metodo_pago=expense.metodo_pago,
        estado=expense.estado,
        notas=expense.notas,
        created_at=expense.created_at,
        updated_at=expense.updated_at
    )


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    update_data: ExpenseUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Actualizar un gasto existente.

    Nota: Si el gasto viene de una plantilla, solo se actualiza la instancia del mes,
    no la plantilla original.
    """
    expense_crud = ExpenseCRUD(db)
    expense = await expense_crud.update(expense_id, str(current_user.id), update_data)

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )

    return ExpenseResponse(
        _id=str(expense.id),
        user_id=str(expense.user_id),
        periodo_id=str(expense.periodo_id),
        plantilla_id=str(expense.plantilla_id) if expense.plantilla_id else None,
        nombre=expense.nombre,
        valor=expense.valor,
        fecha=expense.fecha,
        categoria_id=str(expense.categoria_id),
        subcategoria_nombre=expense.subcategoria_nombre,
        tipo=expense.tipo,
        metodo_pago=expense.metodo_pago,
        estado=expense.estado,
        notas=expense.notas,
        created_at=expense.created_at,
        updated_at=expense.updated_at
    )


@router.patch("/{expense_id}/mark-paid", response_model=ExpenseResponse)
async def mark_expense_as_paid(
    expense_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Marcar un gasto como pagado.
    """
    expense_crud = ExpenseCRUD(db)
    expense = await expense_crud.mark_as_paid(expense_id, str(current_user.id))

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )

    return ExpenseResponse(
        _id=str(expense.id),
        user_id=str(expense.user_id),
        periodo_id=str(expense.periodo_id),
        plantilla_id=str(expense.plantilla_id) if expense.plantilla_id else None,
        nombre=expense.nombre,
        valor=expense.valor,
        fecha=expense.fecha,
        categoria_id=str(expense.categoria_id),
        subcategoria_nombre=expense.subcategoria_nombre,
        tipo=expense.tipo,
        metodo_pago=expense.metodo_pago,
        estado=expense.estado,
        notas=expense.notas,
        created_at=expense.created_at,
        updated_at=expense.updated_at
    )


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Eliminar un gasto.
    """
    expense_crud = ExpenseCRUD(db)
    deleted = await expense_crud.delete(expense_id, str(current_user.id))

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gasto no encontrado"
        )

    return None
