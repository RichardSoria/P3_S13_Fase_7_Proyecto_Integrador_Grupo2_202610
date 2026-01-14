# 📘 Sistema de Gestión Parroquial de Catequesis (Edición NoSQL)

## 📝 Descripción del Proyecto

Este proyecto implementa un **Sistema Web de Gestión Parroquial de Catequesis**, desarrollado con **Django**, cuya principal característica es la **migración de un modelo relacional tradicional hacia una arquitectura NoSQL basada en documentos**, utilizando **MongoDB Atlas**.

La aplicación aprovecha la flexibilidad de los documentos NoSQL para manejar **estructuras de datos complejas**, como subdocumentos embebidos y arreglos dinámicos de historial.  
Debido a las limitaciones nativas de compatibilidad entre el ORM de Django y MongoDB, se implementa un **parche de serialización personalizado (`djongo_patch.py`)**, permitiendo una integración funcional y estable.

---

## ✨ Características Principales

- **Arquitectura Documental**
  - Uso de `EmbeddedField` para subdocumentos (ej. Representante).
  - Uso de `ArrayField` para listas dinámicas (Historial de Traslados).

- **Parche de Compatibilidad NoSQL**
  - Implementación de `djongo_patch.py` para:
    - Serialización correcta de `ObjectId`.
    - Manejo de objetos anidados.
    - Conversión adecuada de tipos `date` a `datetime`.

- **Validación Robusta**
  - Uso de `RegexValidator` para garantizar la integridad de:
    - Cédulas
    - Nombres
    - Correos electrónicos

- **Conexión en la Nube**
  - Integración con **MongoDB Atlas** mediante:
    - Conexión SRV (`mongodb+srv`)
    - Autenticación técnica segura

- **Admin Personalizado**
  - Interfaz administrativa extendida con:
    - `AdminDateWidget`
    - Organización avanzada mediante `fieldsets`

---

## 🛠️ Tecnologías Utilizadas

| Componente        | Tecnología              |
|------------------|--------------------------|
| Lenguaje         | Python 3.14+             |
| Framework Web    | Django 4.1.x             |
| Base de Datos    | MongoDB (NoSQL)          |
| Conector ORM     | Djongo                   |
| Librerías Extra  | `dnspython`, `pymongo`   |

---

## 🚀 Instalación y Configuración

### 1️⃣ Instalación de Dependencias

```bash
pip install django djongo dnspython
```

## 2️⃣ Configuración de la Base de Datos (Seguridad)

Cree un archivo llamado **`db_config.json`** en la raíz del proyecto para desacoplar las credenciales de **MongoDB Atlas** y evitar exponer información sensible en el repositorio.

```json
{
    "ENGINE": "djongo",
    "NAME": "NOMBRE_DE_TU_COLECCION",
    "ENFORCE_SCHEMA": false,
    "CLIENT": {
        "host": "mongodb+srv://USUARIO:PASSWORD@cluster.mongodb.net/?retryWrites=true&w=majority"
    }
}
```
## 3️⃣ Parche de Serialización (`djongo_patch.py`)

Para garantizar el correcto funcionamiento de las operaciones **CRUD** sobre documentos complejos en MongoDB, el proyecto incluye un **parche de serialización personalizado**.

Este archivo debe ubicarse en la **raíz del proyecto** y ser importado al inicio de la ejecución, ya sea desde `settings.py` o `manage.py`, asegurando que las correcciones se apliquen antes de cualquier interacción con la base de datos.

### 🧩 Problemas que Corrige el Parche

El archivo `djongo_patch.py` soluciona limitaciones conocidas de la integración entre Django y MongoDB, incluyendo:

- `TypeError: argument after ** must be a mapping`
- Serialización incorrecta de fechas (`date` → `datetime`)
- Conversión adecuada de `ObjectId` para su uso en `CharField`

### ⚙️ Consideraciones Técnicas

Este enfoque permite:
- Mantener la compatibilidad con el **Django Admin**.
- Manipular subdocumentos y arreglos embebidos sin errores de persistencia.
- Reducir la fricción entre un ORM orientado a SQL y un motor NoSQL basado en documentos.

> 📌 **Nota:** El código completo del parche se encuentra incluido en el repositorio y se aplica automáticamente al iniciar el proyecto.

## 🚀 4. Inicialización y Despliegue

Una vez configurado el entorno y el archivo `db_config.json`, ejecute los siguientes comandos en la terminal para poner en marcha el sistema:

```bash
# 1. Sincronizar colecciones internas de Django (auth_user, sessions, etc.) en MongoDB
python manage.py migrate

# 2. Crear el acceso administrativo (Superusuario)
python manage.py createsuperuser

# 3. Ejecutar el servidor de desarrollo local
python manage.py runserver
```
---

**Acceso al sistema:** [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 🎓 Lección Aprendida: Desajuste de Impedancia

Una de las mayores lecciones de este proyecto fue enfrentar el **"Impedance Mismatch"** (Desajuste de Impedancia) entre Django y MongoDB. 



Se aprendió que cuando un framework SQL-nativo se conecta a NoSQL, el desarrollador debe intervenir en la lógica de bajo nivel del driver para armonizar ambos mundos, logrando una herramienta potente que combina la **seguridad de Django** con la **flexibilidad de MongoDB**. Esta experiencia técnica subraya la importancia de entender cómo los datos deben ser transformados y validados cuando se cruzan paradigmas relacionales y documentales.


