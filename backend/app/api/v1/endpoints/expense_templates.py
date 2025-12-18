from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_database
from app.api.dependencies import get_current_user
from app.crud.expense_template import ExpenseTemplateCRUD
from app.models.user import UserInDB
from app.models.expense_template import ExpenseTemplateCreate, ExpenseTemplateUpdate, ExpenseTemplateResponse

router = APIRouter()


@router.post("/", response_model=ExpenseTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: ExpenseTemplateCreate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Crear una nueva plantilla de gasto fijo.

    Esta plantilla se usará para generar gastos automáticamente
    al inicio de cada período.
    """
    template_crud = ExpenseTemplateCRUD(db)

    # TODO: Validar que la categoría exista y pertenezca al usuario

    template = await template_crud.create(str(current_user.id), template_data)

    return ExpenseTemplateResponse(
        _id=str(template.id),
        user_id=str(template.user_id),
        nombre=template.nombre,
        valor=template.valor,
        categoria_id=str(template.categoria_id),
        subcategoria_nombre=template.subcategoria_nombre,
        dia_cargo=template.dia_cargo,
        metodo_pago=template.metodo_pago,
        activa=template.activa,
        notas=template.notas,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.get("/", response_model=List[ExpenseTemplateResponse])
async def get_templates(
    activa: Optional[bool] = None,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Obtener todas las plantillas del usuario.

    Opcionalmente filtrar por estado activo/inactivo.
    """
    template_crud = ExpenseTemplateCRUD(db)
    templates = await template_crud.get_all(str(current_user.id), activa)

    return [
        ExpenseTemplateResponse(
            _id=str(tmpl.id),
            user_id=str(tmpl.user_id),
            nombre=tmpl.nombre,
            valor=tmpl.valor,
            categoria_id=str(tmpl.categoria_id),
            subcategoria_nombre=tmpl.subcategoria_nombre,
            dia_cargo=tmpl.dia_cargo,
            metodo_pago=tmpl.metodo_pago,
            activa=tmpl.activa,
            notas=tmpl.notas,
            created_at=tmpl.created_at,
            updated_at=tmpl.updated_at
        )
        for tmpl in templates
    ]


@router.get("/{template_id}", response_model=ExpenseTemplateResponse)
async def get_template(
    template_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Obtener una plantilla específica por ID.
    """
    template_crud = ExpenseTemplateCRUD(db)
    template = await template_crud.get_by_id(template_id, str(current_user.id))

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla no encontrada"
        )

    return ExpenseTemplateResponse(
        _id=str(template.id),
        user_id=str(template.user_id),
        nombre=template.nombre,
        valor=template.valor,
        categoria_id=str(template.categoria_id),
        subcategoria_nombre=template.subcategoria_nombre,
        dia_cargo=template.dia_cargo,
        metodo_pago=template.metodo_pago,
        activa=template.activa,
        notas=template.notas,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.put("/{template_id}", response_model=ExpenseTemplateResponse)
async def update_template(
    template_id: str,
    update_data: ExpenseTemplateUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Actualizar una plantilla existente.

    Esto solo afecta futuros períodos, no los gastos ya generados.
    """
    template_crud = ExpenseTemplateCRUD(db)
    template = await template_crud.update(template_id, str(current_user.id), update_data)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla no encontrada"
        )

    return ExpenseTemplateResponse(
        _id=str(template.id),
        user_id=str(template.user_id),
        nombre=template.nombre,
        valor=template.valor,
        categoria_id=str(template.categoria_id),
        subcategoria_nombre=template.subcategoria_nombre,
        dia_cargo=template.dia_cargo,
        metodo_pago=template.metodo_pago,
        activa=template.activa,
        notas=template.notas,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.patch("/{template_id}/toggle", response_model=ExpenseTemplateResponse)
async def toggle_template(
    template_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Activar/desactivar una plantilla.

    Las plantillas inactivas no generan gastos en nuevos períodos.
    """
    template_crud = ExpenseTemplateCRUD(db)
    template = await template_crud.toggle_active(template_id, str(current_user.id))

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla no encontrada"
        )

    return ExpenseTemplateResponse(
        _id=str(template.id),
        user_id=str(template.user_id),
        nombre=template.nombre,
        valor=template.valor,
        categoria_id=str(template.categoria_id),
        subcategoria_nombre=template.subcategoria_nombre,
        dia_cargo=template.dia_cargo,
        metodo_pago=template.metodo_pago,
        activa=template.activa,
        notas=template.notas,
        created_at=template.created_at,
        updated_at=template.updated_at
    )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db=Depends(get_database)
):
    """
    Eliminar una plantilla.

    Esto no afecta los gastos ya generados de esta plantilla.
    """
    template_crud = ExpenseTemplateCRUD(db)
    deleted = await template_crud.delete(template_id, str(current_user.id))

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla no encontrada"
        )

    return None
