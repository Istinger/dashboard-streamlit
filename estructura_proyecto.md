# Estructura del Proyecto — Ecosistema de Microservicios

## Árbol de directorios

```
seguridad_nacional/
│
├── nodo_maestro/                  # Servicio Pyro4
│   ├── servidor_pyro.py           # Registro en Name Server y lógica del servicio
│   ├── gestor_datos.py            # Carga, conversión xlsx→csv y métodos de datos
│   ├── datos/
│   │   └── homicidios.xlsx        # Archivo fuente (NO subir al repo si es sensible)
│   └── requirements.txt
│
├── nodo_analitica/                # Servicio gRPC
│   ├── servidor_grpc.py           # Implementación del servidor gRPC
│   ├── cliente_pyro.py            # Conexión al nodo maestro vía Pyro4
│   ├── proto/
│   │   └── analitica.proto        # Contrato de la interfaz gRPC
│   ├── analitica_pb2.py           # Generado con protoc
│   ├── analitica_pb2_grpc.py      # Generado con protoc
│   └── requirements.txt
│
├── dashboard/                     # Servicio Streamlit
│   ├── app.py                     # UI principal y orquestador
│   ├── cliente_grpc.py            # Conexión al nodo analítica vía gRPC
│   ├── componentes/
│   │   ├── graficos.py            # Funciones de visualización (barras, pastel)
│   │   └── monitor_red.py         # Verificación de estado de los servicios
│   └── requirements.txt
│
├── tests/
│   ├── test_nodo_maestro.py       # Pruebas del servicio Pyro4
│   ├── test_nodo_analitica.py     # Pruebas del servicio gRPC
│   └── test_dashboard.py          # Pruebas de conectividad del dashboard
│
└── README.md
```

---

## Paso 1 — Nodo Maestro (`nodo_maestro/`)

### Responsabilidades
- Convertir `homicidios.xlsx` → `homicidios.csv` (separador `;`)
- Cargar el CSV en memoria (pandas)
- Registrarse en el **Pyro Name Server**
- Exponer métodos remotos:
  - `filtrar_por_anios(anio_inicio, anio_fin)` → DataFrame filtrado
  - `conteo_por_categoria()` → dict con totales de Homicidio, Asesinato, Sicariato, Femicidio

### Orden de arranque
```bash
# Terminal 1 — Levantar el Name Server de Pyro4
python -m Pyro4.naming

# Terminal 2 — Levantar el nodo maestro
python nodo_maestro/servidor_pyro.py
```

---

## Paso 2 — Nodo Analítica (`nodo_analitica/`)

### Responsabilidades
- Conectarse al Nodo Maestro usando el Name Server de Pyro4
- Exponer servicios gRPC definidos en `analitica.proto`:
  - `GetDistribucionPorProvincia(FiltroRequest)` → lista de provincia + frecuencia
  - `GetFrecuenciaPorArma(FiltroRequest)` → lista de tipo arma + frecuencia

### Generar los stubs de gRPC
```bash
python -m grpc_tools.protoc \
  -I nodo_analitica/proto \
  --python_out=nodo_analitica/ \
  --grpc_python_out=nodo_analitica/ \
  nodo_analitica/proto/analitica.proto
```

### Orden de arranque
```bash
# Terminal 3 — Levantar el servidor gRPC (requiere que el Nodo Maestro ya esté activo)
python nodo_analitica/servidor_grpc.py
```

---

## Paso 3 — Dashboard (`dashboard/`)

### Responsabilidades
- Actuar como cliente gRPC hacia el Nodo Analítica
- Mostrar gráficos de barras/pastel por provincia y tipo de arma
- Selector de variable de frecuencia (provincia o arma)
- Selector de rango de años
- Indicador de estado de conexión de ambos nodos

### Orden de arranque
```bash
# Terminal 4
streamlit run dashboard/app.py
```

---

## Paso 4 — Tests (`tests/`)

Cada archivo de prueba debe verificar:

| Archivo                    | Qué prueba                                                  |
|----------------------------|-------------------------------------------------------------|
| `test_nodo_maestro.py`     | Conexión Pyro4, filtrado por años, conteo por categoría     |
| `test_nodo_analitica.py`   | Conexión gRPC, respuesta de distribución provincia y arma   |
| `test_dashboard.py`        | Que el cliente gRPC recibe datos y el monitor detecta caídas|

```bash
# Correr todos los tests
python -m pytest tests/ -v
```

---

## Flujo de datos

```
homicidios.xlsx
      │
      ▼
[Nodo Maestro — Pyro4]
      │  filtra y agrega
      ▼
[Nodo Analítica — gRPC]
      │  distribuye por provincia / arma
      ▼
[Dashboard — Streamlit]
      │  visualiza e interactúa
      ▼
    Usuario
```

---

## Notas de Clean Code a tener en cuenta

- Usa nombres descriptivos: `filtrar_por_anios` no `f1`, `conteo_por_categoria` no `calc`.
- Cada archivo tiene **una sola responsabilidad**.
- No mezcles lógica de negocio con la capa de comunicación (Pyro4/gRPC).
- Maneja excepciones en cada punto de comunicación remota y muestra alertas claras en el dashboard.
- No subas el `.env` ni archivos `.xlsx` si contienen datos sensibles.
