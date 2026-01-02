from typing import List, Optional
from datetime import datetime, timedelta
from calendar import monthrange
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.period import (
    PeriodCreate,
    PeriodUpdate,
    PeriodInDB,
    TipoPeriodo,
    EstadoPeriodo,
    MetasCategorias
)
from app.models.expense import ExpenseCreate, TipoGasto
from app.models.aporte import AporteCreate


class PeriodCRUD:
    """
    CRUD operations para Periods según LOGICA_SISTEMA.md

    Implementa toda la lógica de:
    - Creación automática de períodos
    - Copia de gastos fijos (permanentes y temporales)
    - Copia de aportes fijos
    - Cálculo de liquidez
    - Gestión de períodos mensuales y de crédito
    """

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        expense_crud=None,
        aporte_crud=None
    ):
        self.collection = db["periods"]
        self.db = db  # Guardar referencia a la base de datos para acceder a otras colecciones
        self.expense_crud = expense_crud
        self.aporte_crud = aporte_crud

    async def create(self, user_id: str, period: PeriodCreate) -> PeriodInDB:
        """
        Crear un nuevo período
        """
        period_dict = period.model_dump(exclude_none=True)
        period_dict["user_id"] = ObjectId(user_id)
        period_dict["created_at"] = datetime.utcnow()
        period_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(period_dict)
        period_dict["_id"] = result.inserted_id

        return PeriodInDB(**period_dict)

    async def get_by_id(self, user_id: str, period_id: str) -> Optional[PeriodInDB]:
        """
        Obtener período por ID
        """
        period = await self.collection.find_one({
            "_id": ObjectId(period_id),
            "user_id": ObjectId(user_id)
        })

        return PeriodInDB(**period) if period else None

    async def get_active(
        self,
        user_id: str,
        tipo_periodo: TipoPeriodo
    ) -> Optional[PeriodInDB]:
        """
        Obtener el período activo de un tipo específico

        Si no existe, lo crea automáticamente
        """
        period = await self.collection.find_one({
            "user_id": ObjectId(user_id),
            "tipo_periodo": tipo_periodo,
            "estado": EstadoPeriodo.ACTIVO
        })

        if period:
            return PeriodInDB(**period)

        # No existe período activo, crear uno nuevo
        return await self._create_current_period(user_id, tipo_periodo)

    async def get_all(
        self,
        user_id: str,
        tipo_periodo: Optional[TipoPeriodo] = None,
        estado: Optional[EstadoPeriodo] = None
    ) -> List[PeriodInDB]:
        """
        Obtener todos los períodos con filtros opcionales
        """
        query = {"user_id": ObjectId(user_id)}

        if tipo_periodo:
            query["tipo_periodo"] = tipo_periodo

        if estado:
            query["estado"] = estado

        cursor = self.collection.find(query).sort("fecha_inicio", -1)
        periods = await cursor.to_list(length=None)

        return [PeriodInDB(**per) for per in periods]

    async def update(self, user_id: str, period_id: str, period_update: PeriodUpdate) -> Optional[PeriodInDB]:
        """
        Actualizar un período
        Permite editar sueldo, metas, estado y total_gastado
        """
        update_data = period_update.model_dump(exclude_none=True)

        if not update_data:
            return await self.get_by_id(user_id, period_id)

        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(period_id), "user_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True
        )

        return PeriodInDB(**result) if result else None

    async def close_period(self, user_id: str, period_id: str) -> Optional[PeriodInDB]:
        """
        Cerrar un período (marcar como CERRADO)
        """
        return await self.update(
            user_id,
            period_id,
            PeriodUpdate(estado=EstadoPeriodo.CERRADO)
        )

    async def delete(self, user_id: str, period_id: str) -> bool:
        """
        Eliminar un período
        NOTA: En producción, probablemente NO se deberían eliminar períodos
        """
        result = await self.collection.delete_one({
            "_id": ObjectId(period_id),
            "user_id": ObjectId(user_id)
        })

        return result.deleted_count > 0

    # ====================
    # LÓGICA DE CREACIÓN AUTOMÁTICA
    # ====================

    async def _get_user_categories(self, user_id: str) -> List[ObjectId]:
        """
        Obtener los IDs de las 4 categorías del usuario
        """
        categories = await self.db["categories"].find(
            {"user_id": ObjectId(user_id)}
        ).to_list(length=None)

        return [cat["_id"] for cat in categories]

    async def _create_current_period(
        self,
        user_id: str,
        tipo_periodo: TipoPeriodo
    ) -> PeriodInDB:
        """
        Crear el período actual según el tipo

        Flujo:
        1. Calcular fechas según tipo de período
        2. Obtener categorías del usuario
        3. Buscar período anterior cerrado
        4. Si existe anterior, copiar gastos/aportes fijos
        5. Si es período mensual y existe período de crédito cerrado, obtener deuda
        """
        now = datetime.utcnow()

        if tipo_periodo == TipoPeriodo.MENSUAL_ESTANDAR:
            fecha_inicio, fecha_fin = self._calculate_mensual_dates(now)
        else:  # CICLO_CREDITO
            fecha_inicio, fecha_fin = self._calculate_credito_dates(now)

        # Obtener categorías del usuario
        categorias = await self._get_user_categories(user_id)

        # Buscar período anterior
        previous_period = await self._get_previous_period(user_id, tipo_periodo)

        # Crear período base
        period_dict = {
            "user_id": ObjectId(user_id),
            "tipo_periodo": tipo_periodo,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "sueldo": 0,
            "metas_categorias": MetasCategorias().model_dump(),
            "estado": EstadoPeriodo.ACTIVO,
            "categorias": categorias,  # Añadir referencias a las 4 categorías
            "total_gastado": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Si hay período anterior, copiar metas, sueldo y categorías
        if previous_period:
            period_dict["sueldo"] = previous_period.sueldo
            period_dict["metas_categorias"] = previous_period.metas_categorias.model_dump()
            # Si el período anterior tiene categorías, usarlas (para compatibilidad)
            if hasattr(previous_period, 'categorias') and previous_period.categorias:
                period_dict["categorias"] = previous_period.categorias

        result = await self.collection.insert_one(period_dict)
        period_dict["_id"] = result.inserted_id

        new_period = PeriodInDB(**period_dict)

        # Copiar gastos fijos y aportes fijos del período anterior
        if previous_period and self.expense_crud and self.aporte_crud:
            await self._copy_fixed_items(user_id, previous_period, new_period)

        return new_period

    async def _get_previous_period(
        self,
        user_id: str,
        tipo_periodo: TipoPeriodo
    ) -> Optional[PeriodInDB]:
        """
        Obtener el período anterior cerrado más reciente del mismo tipo
        """
        period = await self.collection.find_one(
            {
                "user_id": ObjectId(user_id),
                "tipo_periodo": tipo_periodo,
                "estado": EstadoPeriodo.CERRADO
            },
            sort=[("fecha_fin", -1)]
        )

        return PeriodInDB(**period) if period else None

    async def _copy_fixed_items(
        self,
        user_id: str,
        previous_period: PeriodInDB,
        new_period: PeriodInDB
    ):
        """
        Copiar gastos fijos y aportes fijos del período anterior al nuevo

        Según LOGICA_SISTEMA.md:
        1. Copiar gastos fijos permanentes (es_permanente=True)
        2. Copiar gastos fijos temporales si periodos_restantes > 0 (decrementando el contador)
        3. Copiar aportes fijos (es_fijo=True)
        4. NO copiar gastos variables
        5. NO copiar aportes variables
        """
        previous_id = str(previous_period.id)
        new_id = str(new_period.id)

        # 1. Copiar gastos fijos permanentes
        fijos_permanentes = await self.expense_crud.get_fijos_permanentes(user_id, previous_id)

        for gasto in fijos_permanentes:
            expense_create = ExpenseCreate(
                nombre=gasto.nombre,
                monto=gasto.monto,
                categoria_id=gasto.categoria_id,
                tipo=TipoGasto.FIJO,
                es_permanente=True,
                descripcion=gasto.descripcion
            )
            await self.expense_crud.create(user_id, new_id, expense_create)

        # 2. Copiar gastos fijos temporales con períodos > 0
        fijos_temporales = await self.expense_crud.get_fijos_temporales_activos(user_id, previous_id)

        for gasto in fijos_temporales:
            # Decrementar períodos restantes
            new_periodos = gasto.periodos_restantes - 1

            # Solo copiar si quedan períodos restantes
            if new_periodos >= 0:
                expense_create = ExpenseCreate(
                    nombre=gasto.nombre,
                    monto=gasto.monto,
                    categoria_id=gasto.categoria_id,
                    tipo=TipoGasto.FIJO,
                    es_permanente=False,
                    periodos_restantes=new_periodos,
                    descripcion=gasto.descripcion
                )
                await self.expense_crud.create(user_id, new_id, expense_create)

        # 3. Copiar aportes fijos
        aportes_fijos = await self.aporte_crud.get_fijos(user_id, previous_id)

        for aporte in aportes_fijos:
            aporte_create = AporteCreate(
                nombre=aporte.nombre,
                monto=aporte.monto,
                categoria_id=aporte.categoria_id,
                es_fijo=True,
                descripcion=aporte.descripcion
            )
            await self.aporte_crud.create(user_id, new_id, aporte_create)

    def _calculate_mensual_dates(self, reference_date: datetime) -> tuple:
        """
        Calcular fechas para período mensual estándar (1 al último día del mes)
        """
        # Primer día del mes
        fecha_inicio = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Último día del mes
        last_day = monthrange(reference_date.year, reference_date.month)[1]
        fecha_fin = reference_date.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

        return fecha_inicio, fecha_fin

    def _calculate_credito_dates(self, reference_date: datetime) -> tuple:
        """
        Calcular fechas para período de crédito (25 al 24)

        Lógica:
        - Si estamos entre el 1 y el 24, el período va del 25 del mes anterior al 24 del mes actual
        - Si estamos entre el 25 y el 31, el período va del 25 del mes actual al 24 del mes siguiente
        """
        if reference_date.day >= 25:
            # Período actual: del 25 de este mes al 24 del siguiente
            fecha_inicio = reference_date.replace(day=25, hour=0, minute=0, second=0, microsecond=0)

            # Mes siguiente
            if reference_date.month == 12:
                next_month = 1
                next_year = reference_date.year + 1
            else:
                next_month = reference_date.month + 1
                next_year = reference_date.year

            fecha_fin = reference_date.replace(
                year=next_year,
                month=next_month,
                day=24,
                hour=23,
                minute=59,
                second=59,
                microsecond=999999
            )
        else:
            # Período actual: del 25 del mes anterior al 24 de este mes
            # Mes anterior
            if reference_date.month == 1:
                prev_month = 12
                prev_year = reference_date.year - 1
            else:
                prev_month = reference_date.month - 1
                prev_year = reference_date.year

            fecha_inicio = reference_date.replace(
                year=prev_year,
                month=prev_month,
                day=25,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            fecha_fin = reference_date.replace(day=24, hour=23, minute=59, second=59, microsecond=999999)

        return fecha_inicio, fecha_fin

    # ====================
    # CÁLCULOS SEGÚN LOGICA_SISTEMA.md
    # ====================

    async def calculate_total_real_categoria(
        self,
        user_id: str,
        periodo_id: str,
        categoria_id: str
    ) -> float:
        """
        Calcular el total REAL de una categoría según LOGICA_SISTEMA.md

        Fórmula: total_categoria = suma(gastos_fijos) + suma(gastos_variables) - suma(aportes)
        """
        if not self.expense_crud or not self.aporte_crud:
            return 0.0

        total_gastos = await self.expense_crud.calculate_total_by_categoria(
            user_id, periodo_id, categoria_id
        )

        total_aportes = await self.aporte_crud.calculate_total_by_categoria(
            user_id, periodo_id, categoria_id
        )

        return total_gastos - total_aportes

    async def calculate_liquidez(
        self,
        user_id: str,
        period: PeriodInDB,
        categoria_ahorro_id: str,
        categoria_arriendo_id: str,
        categoria_liquidez_id: Optional[str] = None
    ) -> float:
        """
        Calcular liquidez según LOGICA_SISTEMA.md

        Fórmula completa:
        1. liquidez_inicial = sueldo - total_ahorro_real - total_arriendo_real - credito_periodo_anterior
        2. liquidez_disponible = liquidez_inicial - gastos_liquidez + aportes_liquidez

        Donde:
        - total_ahorro_real = gastos_ahorro - aportes_ahorro
        - total_arriendo_real = gastos_arriendo - aportes_arriendo
        - credito_periodo_anterior = total_gastado del período de crédito cerrado más reciente
        - gastos_liquidez = gastos fijos + gastos variables de la categoría liquidez
        - aportes_liquidez = aportes a la categoría liquidez

        NOTA: Ahorro NO tiene meta, se calcula como suma de gastos - aportes
        """
        # Obtener total real de ahorro
        total_ahorro_real = await self.calculate_total_real_categoria(
            user_id,
            str(period.id),
            categoria_ahorro_id
        )

        # Obtener total real de arriendo
        total_arriendo_real = await self.calculate_total_real_categoria(
            user_id,
            str(period.id),
            categoria_arriendo_id
        )

        # Obtener crédito del período anterior
        # El crédito a pagar en este mes es el del período de crédito que termina durante este mes
        # Primero intentar buscar un período cerrado (flujo normal después del primer mes)
        previous_credit_period = await self._get_previous_period(user_id, TipoPeriodo.CICLO_CREDITO)

        # Si no hay período cerrado (caso del primer mes), buscar el período de crédito
        # cuya fecha_fin esté dentro del período mensual actual
        if not previous_credit_period:
            # Buscar período de crédito que termina en este mes (puede estar ACTIVO o CERRADO)
            credit_period = await self.collection.find_one(
                {
                    "user_id": ObjectId(user_id),
                    "tipo_periodo": TipoPeriodo.CICLO_CREDITO,
                    "fecha_fin": {
                        "$gte": period.fecha_inicio,
                        "$lte": period.fecha_fin
                    }
                }
            )
            if credit_period:
                previous_credit_period = PeriodInDB(**credit_period)

        credito_anterior = previous_credit_period.total_gastado if previous_credit_period else 0.0

        # Calcular liquidez inicial
        liquidez_inicial = (
            period.sueldo -
            total_ahorro_real -
            total_arriendo_real -
            credito_anterior
        )

        # Si se proporciona categoria_liquidez_id, calcular liquidez disponible
        if categoria_liquidez_id and self.expense_crud and self.aporte_crud:
            # Obtener gastos de liquidez (fijos + variables)
            gastos_liquidez = await self.expense_crud.calculate_total_by_categoria(
                user_id,
                str(period.id),
                categoria_liquidez_id
            )

            # Obtener aportes de liquidez
            aportes_liquidez = await self.aporte_crud.calculate_total_by_categoria(
                user_id,
                str(period.id),
                categoria_liquidez_id
            )

            # liquidez_disponible = liquidez_inicial - gastos + aportes
            liquidez = liquidez_inicial - gastos_liquidez + aportes_liquidez
        else:
            # Si no se proporciona categoría liquidez, devolver solo liquidez inicial
            liquidez = liquidez_inicial

        return liquidez

    async def update_total_gastado(self, user_id: str, periodo_id: str) -> Optional[PeriodInDB]:
        """
        Actualizar el total_gastado de un período de crédito

        Se llama automáticamente cuando se crea/modifica/elimina un gasto
        """
        if not self.expense_crud:
            return None

        total = await self.expense_crud.calculate_total_periodo(user_id, periodo_id)

        return await self.update(
            user_id,
            periodo_id,
            PeriodUpdate(total_gastado=total)
        )
