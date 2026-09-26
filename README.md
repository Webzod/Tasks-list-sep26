# Guía de rutas de la aplicación de tareas

Este documento explica en detalle cómo funciona `tasks/urls.py`, cómo se conecta con la configuración principal de Django y qué ocurre cuando alguien visita la página de inicio del proyecto.

## Resumen

`tasks/urls.py` es la configuración de URLs de la aplicación `tasks`. Declara una ruta: la ruta vacía (`''`), que apunta a `TaskListView`. Como el proyecto incluye esta configuración en la raíz del sitio, esa ruta corresponde a:

```text
GET /
```

La vista consulta el modelo `Task` y renderiza la plantilla `templates/tasks-list.html`. En su estado actual, la aplicación muestra una lista de tareas; esta ruta no crea, edita ni elimina tareas.

## Archivo documentado

La configuración actual de `tasks/urls.py` es:

```python
from django.urls import path
from .views import TaskListView

urlpatterns = [
    path('', TaskListView.as_view(), name='tasks-list'),
]
```

### Desglose línea por línea

| Elemento | Función |
| --- | --- |
| `from django.urls import path` | Importa el constructor de rutas de Django. `path()` asocia un patrón de URL con una vista. |
| `from .views import TaskListView` | Importa la vista de la aplicación actual. El punto inicial indica una importación relativa desde el paquete `tasks`. |
| `urlpatterns` | Lista que Django inspecciona para resolver las URLs declaradas en este módulo. El nombre debe escribirse exactamente así. |
| `path('', ...)` | Declara el patrón vacío. Una vez incluido este módulo en la raíz del sitio, coincide con `/`. |
| `TaskListView.as_view()` | Convierte la vista basada en clase en la función invocable que espera el sistema de enrutamiento de Django. |
| `name='tasks-list'` | Asigna un nombre estable a la ruta para poder referenciarla sin escribir la URL manualmente. |

## Recorrido de una petición

Cuando un navegador solicita `http://127.0.0.1:8000/`, el recorrido es:

1. Django lee `ROOT_URLCONF`, configurado como `django_base.urls`.
2. `django_base/urls.py` comprueba sus patrones en orden. La ruta `admin/` sirve el panel administrativo y el patrón vacío incluye `tasks.urls`.
3. Django continúa la resolución dentro de `tasks/urls.py`.
4. El patrón `''` coincide con la raíz y selecciona `TaskListView`.
5. `TaskListView`, una subclase de `django.views.generic.ListView`, obtiene objetos del modelo `Task`.
6. Django renderiza `templates/tasks-list.html` con el contexto de la lista.
7. La plantilla recorre `task_list` y muestra el campo `title` de cada tarea.

Representación simplificada:

```text
GET /
  -> django_base.urls
  -> include('tasks.urls')
  -> tasks.urls: path('', ...)
  -> TaskListView
  -> modelo Task
  -> templates/tasks-list.html
  -> respuesta HTML
```

El contexto `task_list` es el nombre predeterminado que `ListView` proporciona para una lista de instancias de `Task`. La plantilla actual usa ese nombre directamente:

```django
{% for homework in task_list %}
    <li>{{ homework.title }}</li>
{% endfor %}
```

El nombre local `homework` dentro del bucle no cambia el nombre del modelo ni de la ruta; simplemente representa el elemento actual durante cada iteración.

## Cómo se monta la ruta

La configuración principal del proyecto contiene, en esencia:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks.urls')),
]
```

El prefijo `''` significa que las rutas de la aplicación se montan desde la raíz del dominio. Por eso `path('', ...)` en `tasks/urls.py` termina resolviendo `/`, no `/tasks/`.

Si más adelante se quisiera servir la aplicación bajo `/tasks/`, habría que cambiar el prefijo de inclusión en `django_base/urls.py` a `path('tasks/', include('tasks.urls'))`. En ese caso, el patrón vacío de la aplicación resolvería `/tasks/`. No es así como está configurado actualmente.

## Nombre de la ruta y referencias

El nombre `tasks-list` permite generar enlaces mediante el sistema de resolución inversa de Django. Así se evita duplicar la ruta literal en plantillas o vistas.

En una plantilla:

```django
<a href="{% url 'tasks-list' %}">Ver tareas</a>
```

En Python:

```python
from django.urls import reverse

url = reverse('tasks-list')
```

Con la configuración presente, ambos ejemplos generan `/`.

La aplicación no declara `app_name`, así que el nombre no está namespaced. Si se incorpora un namespace en el futuro, las referencias deberán actualizarse, por ejemplo, a `tasks:tasks-list`.

## Qué hace y qué no hace esta ruta

**Sí hace:**

- Atiende la página raíz del sitio.
- Usa una vista genérica de listado para consultar tareas.
- Renderiza la plantilla `tasks-list.html`.
- Expone el nombre `tasks-list` para enlaces y redirecciones.

**No hace por sí sola:**

- Define la estructura ni las reglas de validación de `Task`; eso corresponde a `tasks/models.py`.
- Define la consulta personalizada o el nombre de la plantilla; eso corresponde a `tasks/views.py`.
- Crea, actualiza o elimina tareas.
- Define rutas independientes para cada tarea.
- Restringe el acceso mediante autenticación.

Actualmente, si no hay tareas, el bucle de la plantilla no imprime elementos `<li>`. No hay un mensaje de estado vacío configurado.

## Añadir otra URL

Para añadir una ruta, se importa la vista correspondiente y se agrega otro `path()` a `urlpatterns`. Por ejemplo, una ruta futura para una página de ayuda podría tener esta forma:

```python
from django.urls import path
from .views import TaskListView, help_page

urlpatterns = [
    path('', TaskListView.as_view(), name='tasks-list'),
    path('ayuda/', help_page, name='tasks-help'),
]
```

Este ejemplo es ilustrativo: `help_page` tendría que existir en `tasks/views.py` antes de poder importarlo. Cada nombre de ruta debería ser descriptivo y único dentro de la configuración correspondiente.

Al añadir patrones, conviene:

- Mantener las rutas de una misma aplicación en `tasks/urls.py`.
- Dar a cada ruta un nombre para poder usar `{% url %}` o `reverse()`.
- Elegir un patrón con barra final de manera consistente con el resto del proyecto.
- Usar `include()` en la configuración principal para montar las rutas de la aplicación bajo un prefijo si el proyecto crece.
- Verificar que la vista y su plantilla existan y estén registradas correctamente.

## Ejecutar y comprobar el proyecto

Desde la carpeta que contiene `manage.py`, en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver
```

Después, abre `http://127.0.0.1:8000/`. El panel de administración está montado en `http://127.0.0.1:8000/admin/`.

Si ya tienes el entorno virtual activo y las dependencias instaladas, los comandos esenciales para comprobar el proyecto son:

```powershell
python manage.py check
python manage.py test tasks
```

`check` valida la configuración de Django. `test tasks` ejecuta las pruebas de la aplicación; actualmente `tasks/tests.py` contiene el archivo base, pero todavía no define pruebas de resolución de URLs.

## Prueba de URL recomendada

Una prueba pequeña puede confirmar que el nombre de ruta sigue resolviendo a la página de listado. Por ejemplo, en `tasks/tests.py`:

```python
from django.test import TestCase
from django.urls import reverse


class TaskListUrlTests(TestCase):
    def test_named_route_resolves_to_root(self):
        self.assertEqual(reverse('tasks-list'), '/')

    def test_root_displays_task_list(self):
        response = self.client.get(reverse('tasks-list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks-list.html')
```

Esta prueba es una propuesta, no está añadida al proyecto. La primera protege el contrato del nombre `tasks-list`; la segunda comprueba que la petición llega a la vista y que se usa la plantilla esperada.

## Problemas habituales

| Síntoma | Qué revisar |
| --- | --- |
| La raíz devuelve 404 | Comprueba que `django_base/urls.py` incluye `tasks.urls` con el prefijo esperado y que el patrón vacío está en `urlpatterns`. |
| `NoReverseMatch` al usar `tasks-list` | Verifica que el nombre esté escrito exactamente igual y que no se haya agregado un namespace. |
| Error al importar `TaskListView` | Comprueba que la clase exista en `tasks/views.py` y que no haya errores de importación en sus dependencias. |
| Error de plantilla no encontrada | Comprueba `template_name` en la vista y que `templates/tasks-list.html` esté disponible según la configuración `TEMPLATES` del proyecto. |
| La página carga, pero no muestra tareas | Confirma que existen registros `Task` en la base de datos y que la plantilla itera sobre `task_list`. |
| Django no reconoce la aplicación | Comprueba que `tasks` aparece en `INSTALLED_APPS` y que estás ejecutando comandos desde la carpeta correcta. |

## Referencias del proyecto

- `tasks/urls.py`: patrones de URL propios de la aplicación.
- `django_base/urls.py`: montaje de las rutas de la aplicación y del panel de administración.
- `tasks/views.py`: implementación de `TaskListView`.
- `tasks/models.py`: modelo `Task` y sus campos.
- `templates/tasks-list.html`: presentación HTML de la lista.
- `tasks/tests.py`: pruebas de la aplicación.
- `requirements.txt`: dependencias de Python del proyecto.