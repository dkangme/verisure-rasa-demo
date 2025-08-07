# Verisure Rasa Demo

Este es un demo de chatbot para Verisure que maneja consultas de facturación usando Rasa Pro con CALM (Conversational AI with Language Models).

## Características

- ✅ Flujo conversacional completo basado en diagrama Mermaid
- ✅ Integración con base de datos MariaDB
- ✅ Manejo inteligente de respuestas con CALM
- ✅ Sistema de fallbacks robusto
- ✅ Registro de interacciones en base de datos
- ✅ Soporte multilingüe (Español/Inglés)

## Instalación

### 1. Configurar Variables de Entorno

Copia el archivo de ejemplo y configura tus variables:

```bash
cp env.example .env
```

Edita el archivo `.env` con tus credenciales:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=verisure_demo
OPENAI_API_KEY=tu_openai_api_key
```

### 2. Instalar Dependencias

```bash
pip install rasa mysql-connector-python python-dotenv
```

### 3. Configurar Base de Datos

Ejecuta el script de configuración de la base de datos:

```bash
python database_config.py
```

### 4. Entrenar el Modelo

```bash
rasa train
```

## Uso

### Iniciar el Servidor de Acciones

```bash
rasa run actions
```

### Iniciar el Servidor Principal

```bash
rasa run
```

### Probar el Chatbot

```bash
rasa shell
```

## Flujo Conversacional

El chatbot implementa el siguiente flujo basado en el diagrama Mermaid:

1. **Saludo e Identificación**: Verifica si habla con Dennis Kangme
2. **Información de Factura**: Informa sobre factura pendiente de $55.000
3. **Respuesta del Cliente**: Maneja sí/no/pregunta sobre fecha
4. **Clasificación de Razones**: Categoriza diferentes tipos de respuestas
5. **Respuesta Final**: Proporciona respuesta apropiada según el caso

## Estructura de Base de Datos

### Tabla: customers
- `id`: ID único del cliente
- `name`: Nombre del cliente
- `email`: Email del cliente
- `phone`: Teléfono del cliente

### Tabla: invoices
- `id`: ID único de la factura
- `customer_id`: Referencia al cliente
- `invoice_number`: Número de factura
- `amount`: Monto de la factura
- `issue_date`: Fecha de emisión
- `due_date`: Fecha de vencimiento
- `status`: Estado (pending/paid/overdue)

### Tabla: interactions
- `id`: ID único de la interacción
- `session_id`: ID de la sesión
- `customer_id`: Referencia al cliente
- `interaction_type`: Tipo de interacción
- `data`: Datos adicionales
- `timestamp`: Fecha y hora

## Archivos Principales

- `data/flows.yml`: Definición de flujos conversacionales
- `data/nlu.yml`: Datos de entrenamiento para NLU
- `data/rules.yml`: Reglas de conversación
- `domain.yml`: Configuración del dominio
- `actions/actions.py`: Acciones personalizadas
- `config.yml`: Configuración de Rasa Pro
- `database_config.py`: Configuración de base de datos

## Personalización

### Agregar Nuevos Flujos

1. Edita `data/flows.yml` para agregar nuevos flujos
2. Agrega ejemplos de entrenamiento en `data/nlu.yml`
3. Define reglas en `data/rules.yml`
4. Agrega respuestas en `domain.yml`

### Modificar Base de Datos

1. Edita `database_config.py` para agregar nuevas tablas
2. Actualiza las acciones en `actions/actions.py`
3. Reentrena el modelo con `rasa train`

## Troubleshooting

### Error de Conexión a Base de Datos
- Verifica que MariaDB esté ejecutándose
- Confirma las credenciales en `.env`
- Ejecuta `python database_config.py` para crear las tablas

### Error de Entrenamiento
- Verifica que todos los archivos YAML estén correctamente formateados
- Asegúrate de que las intenciones estén definidas en `domain.yml`
- Ejecuta `rasa train --debug` para más información

### Error de Acciones
- Verifica que el servidor de acciones esté ejecutándose
- Confirma que las acciones estén registradas en `domain.yml`
- Revisa los logs del servidor de acciones

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles. 