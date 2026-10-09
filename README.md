# TatiVision

Catálogo local de películas y series para Windows. La aplicación usa SQLite
para el catálogo, TMDb para metadatos y el reproductor elegido para reproducir
videos.

## Ejecutar la versión portable

Abrí `dist\TatiVision\TatiVision.exe`. La carpeta portable contiene el
ejecutable y sus dependencias, y mantiene junto a ellos la configuración,
la base `database\catalog.db` y los pósteres de `cache\posters`.

Una compilación nueva no copia `.env`, `settings.json`, la base de datos ni los
pósteres del entorno de desarrollo. Así no se distribuyen por accidente la
clave API, las rutas personales o el catálogo local. Al primer inicio, cada
computadora configura sus propias carpetas y reproductor. Al recompilar en la
misma carpeta `dist\TatiVision`, se conservan la configuración, el catálogo y
la caché de pósteres que ya existían allí.

Usá el ícono de tuerca en la parte inferior izquierda para elegir el
reproductor de Windows, configurar la clave API de TMDb o borrar el catálogo.
El logo de TMDB junto a Ajustes abre el sitio oficial. TatiVision usa TMDB y
sus API, pero no está respaldado, certificado ni aprobado por TMDB.
La sección **Biblioteca** permite crear varias bibliotecas con carpetas
independientes para películas y series. Elegir otra biblioteca cambia el
contenido y los géneros mostrados; al crear una se analizan sus carpetas.
El botón × de una biblioteca la quita de la configuración, pero conserva los
registros y metadatos del catálogo. La aplicación se inicia maximizada en una ventana.
Los datos se guardan en `settings.json` y en la base local junto a la
aplicación. El primer inicio solicita elegir un reproductor y muestra la
Biblioteca vacía hasta que se agregue una.
Ese archivo contiene la clave de TMDb en texto claro: no lo publiques ni lo
compartas sin quitar antes la clave y las rutas personales.

Las actualizaciones de metadatos usan automáticamente la primera coincidencia
de TMDb. Si una película se identificó mal, abrí su ficha y usá el botón de
lápiz para consultar de nuevo TMDb y seleccionar la coincidencia correcta
solo para esa película.

El archivo `.env` puede usarse en desarrollo como configuración inicial, pero
no se incorpora al portable. Mantenelo privado, ya que puede contener la clave
de TMDb y rutas personales.

**Borrar base de datos** elimina el catálogo local, los metadatos, las
bibliotecas configuradas y los pósteres almacenados por TatiVision. No borra
los archivos de video ni modifica el reproductor o la clave API.

## Incorporar íconos propios

Los íconos propios van dentro de `assets\icons`:

- `assets\icons\executable.ico`: ícono del archivo `.exe`; se aplica al
  ejecutar de nuevo `build_portable.ps1`.
- `assets\icons\app.ico`: ícono de la ventana principal, diálogos y barra de
  tareas.
- `assets\icons\ui\`: íconos de botones y otros controles, en SVG, PNG o ICO.
  El nombre del archivo es su identificador en la interfaz; los nombres
  actuales incluyen `setting`, `movie`, `view`, `edit`, `add`, `arrow`,
  `delete`, `library`, `fav` y `play`.

La compilación portable incluye automáticamente los archivos de `assets`.
Para cargar un ícono de la interfaz desde Python, usá
`app.ui.icon_utils.load_ui_icon("nombre")`.

“Predeterminado de Windows” abre el video con la aplicación asociada. También
podés elegir un reproductor multimedia detectado en el sistema o usar
“Buscar otro reproductor en Windows…” para seleccionar su ejecutable `.exe`.
El reproductor elegido se guarda en `settings.json` y TatiVision lo invoca
directamente; esto no cambia las asociaciones globales de Windows.

Si un póster quedó en la caché local con el nombre de la película pero su ruta
no está registrada en el catálogo, TatiVision también intenta encontrarlo por
título antes de mostrar el marcador vacío.

En películas, **Analizar y cargar películas** busca videos nuevos y carga
automáticamente los metadatos pendientes desde TMDb; **Carga forzada** vuelve
a consultar toda la biblioteca. En series, **Analizar y cargar series** busca
series y episodios y carga los metadatos pendientes; **Carga forzada de
series** vuelve a consultar toda la biblioteca. El botón **Cancelar** detiene
el análisis entre archivos y series, y detiene la carga de metadatos al
terminar la solicitud TMDb que esté en curso; los cambios ya procesados se
conservan.

## Compilar

La compilación debe hacerse en Windows desde el entorno virtual del proyecto:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m pip install -r requirements-build.txt
powershell -ExecutionPolicy Bypass -File .\build_portable.ps1
```

El resultado queda en `dist\TatiVision`. Se distribuye la carpeta completa,
no solamente `TatiVision.exe`.
Para crear una salida de prueba nueva sin configuración, base ni caché, usá
una carpeta que todavía no exista:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_portable.ps1 `
  -OutputDirectory .\dist\TatiVision-clean-test -RequireFreshOutput
```
