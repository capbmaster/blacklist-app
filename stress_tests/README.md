# Pruebas de Estrés - Análisis New Relic

## Instalación

```bash
pip install -r stress_tests/requirements.txt
```

## Ejecución

Reemplaza `<TU_URL_AWS>` con la URL de tu servicio en AWS (ECS/EB).

### 1. Prueba completa (todos los escenarios) - UI Web

```bash
locust -f stress_tests/locustfile.py --host=http://<TU_URL_AWS>
```

Abre http://localhost:8089 en el navegador y configura:
- **Number of users**: 50
- **Spawn rate**: 5 users/s
- **Run time**: 5m

### 2. Prueba headless (sin UI) - Carga moderada

```bash
locust -f stress_tests/locustfile.py \
  --host=http://<TU_URL_AWS> \
  --headless \
  --users 30 \
  --spawn-rate 5 \
  --run-time 3m
```

### 3. Prueba de pico (para disparar alertas en New Relic)

```bash
locust -f stress_tests/locustfile.py \
  --host=http://<TU_URL_AWS> \
  --headless \
  --users 100 \
  --spawn-rate 20 \
  --run-time 2m
```

### 4. Solo escenarios de errores

```bash
locust -f stress_tests/locustfile.py \
  --host=http://<TU_URL_AWS> \
  --headless \
  --users 20 \
  --spawn-rate 5 \
  --run-time 2m \
  --tags errors
```

### 5. Solo escenarios de tiempo de respuesta

```bash
locust -f stress_tests/locustfile.py \
  --host=http://<TU_URL_AWS> \
  --headless \
  --users 40 \
  --spawn-rate 10 \
  --run-time 3m \
  --tags response_time
```

## Orden recomendado para el análisis en New Relic

1. **Ejecutar prueba moderada (30 users, 3min)** → revisar en NR:
   - APM > Summary: tiempo de respuesta por transacción
   - APM > Databases: tiempo de respuesta de queries PostgreSQL
   - APM > Summary: Apdex score

2. **Ejecutar prueba de errores (20 users, 2min)** → revisar en NR:
   - APM > Errors: tasa de errores, tipos (401, 400, 409)
   - APM > Error analytics: agrupación por clase de error

3. **Ejecutar prueba de pico (100 users, 2min)** → revisar en NR:
   - Alerts: verificar que se disparen las alertas configuradas
   - APM > Summary: degradación del Apdex bajo carga
   - Infrastructure: uso de CPU/memoria del contenedor
