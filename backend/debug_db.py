"""
Script de debug para ver qué hay en la base de datos
"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def check_db():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['emo_finance']

    # Obtener el último período mensual
    periods = await db.periods.find({"tipo_periodo": "mensual_estandar"}).sort("created_at", -1).to_list(1)
    if periods:
        period = periods[0]
        print(f"\n=== PERÍODO MENSUAL ===")
        print(f"ID: {period['_id']}")
        print(f"User ID: {period['user_id']}")
        print(f"Sueldo: ${period['sueldo']}")

        # Buscar gastos de este período
        expenses = await db.expenses.find({"periodo_id": period['_id']}).to_list(None)
        print(f"\n=== GASTOS EN ESTE PERÍODO ===")
        print(f"Total gastos: {len(expenses)}")
        for exp in expenses:
            print(f"  - {exp['nombre']}: ${exp['monto']} (categoria_id: {exp['categoria_id']})")

        # Buscar aportes de este período
        aportes = await db.aportes.find({"periodo_id": period['_id']}).to_list(None)
        print(f"\n=== APORTES EN ESTE PERÍODO ===")
        print(f"Total aportes: {len(aportes)}")
        for ap in aportes:
            print(f"  - {ap['nombre']}: ${ap['monto']} (categoria_id: {ap['categoria_id']})")

        # Mostrar categorías
        categories = await db.categories.find({"user_id": period['user_id']}).to_list(None)
        print(f"\n=== CATEGORÍAS DEL USUARIO ===")
        for cat in categories:
            print(f"  - {cat['nombre']} (slug: {cat['slug']}): ID={cat['_id']}")
    else:
        print("No se encontró ningún período mensual")

    await client.close()

if __name__ == "__main__":
    asyncio.run(check_db())
