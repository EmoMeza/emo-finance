# Instrucciones para Reconstruir los Contenedores

## El Problema
El endpoint `/api/v1/categories` existe en el código pero responde 404 en producción.

## La Solución

En el servidor de producción, ejecuta estos comandos:

```bash
# Detener los contenedores actuales
docker-compose down

# Reconstruir las imágenes (importante: usar --no-cache para asegurar una construcción limpia)
docker-compose build --no-cache

# Iniciar los contenedores
docker-compose up -d

# Verificar que estén corriendo
docker-compose ps

# Ver los logs para confirmar que todo está bien
docker-compose logs -f backend
```

## Verificación

Después de reconstruir, verifica que el endpoint funcione:

```bash
# Debería devolver "Not authenticated" (esto es correcto, significa que el endpoint existe)
curl https://financeapi.emomeza.com/api/v1/categories
```

## Notas Importantes

1. El `--no-cache` asegura que Docker no use versiones antiguas en caché
2. El `-d` en `docker-compose up` ejecuta los contenedores en segundo plano
3. Los logs te mostrarán si hay errores de importación o problemas de inicio

## Si el Problema Persiste

Si después de reconstruir sigue el error 404, verifica:

1. Que el archivo `backend/app/api/v1/endpoints/categories.py` existe
2. Que el archivo `backend/app/api/v1/api.py` incluye la línea:
   ```python
   api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
   ```
3. Revisa los logs del backend para errores de importación:
   ```bash
   docker-compose logs backend | grep -i error
   ```
