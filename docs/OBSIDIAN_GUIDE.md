# Guía de Integración de Synapse 4D para Obsidian

Esta guía detalla el proceso completo para integrar **Synapse 4D** con tu bóveda de Obsidian, habilitando la consolidación cognitiva autónoma, búsqueda semántica local y resolución bi-temporal de hechos directamente desde el editor.

---

## 1. Requisitos Previos

Antes de instalar el plugin en Obsidian, asegúrate de contar con:
- **Obsidian v1.4.0** o superior instalado.
- **Python 3.10+** instalado en tu sistema (con `synapse4d` instalado mediante `pip install -e .` o el ejecutable standalone compilado en tu `PATH`).
- Una bóveda con la estructura CoALA estándar:
  - `00_Memoria_de_Trabajo/` (o `00_Working_Memory/`)
  - `10_Memoria_Episodica/` (o `10_Episodic_Memory/`)
  - `20_Memoria_Semantica/` (o `20_Semantic_Memory/`)
  - `30_Memoria_Procedimental/` (o `30_Procedural_Memory/`)
  - `90_Meta_Sistema/` (o `90_Meta_System/`)

---

## 2. Instalación vía BRAT (Recomendada para Betas)

La forma más rápida de mantener actualizado el plugin es mediante **BRAT** (*Beta Reviewer's Auto-update Tool*):

1. **Instalar BRAT:** Ve a *Ajustes > Plugins de la comunidad > Explorar*, busca **BRAT** e instálalo y actívalo.
2. **Abrir BRAT:** En la barra lateral de ajustes, accede a las opciones de *BRAT*.
3. **Añadir el repositorio:** Pulsa en el botón **"Add Beta plugin"** e ingresa la URL del repositorio:
   ```text
   https://github.com/synapse4d/synapse4d-obsidian
   ```
4. **Activar el plugin:** Una vez descargado por BRAT, ve a *Plugins de la comunidad* y activa la casilla de verificación junto a **Synapse 4D**.

---

## 3. Instalación Manual (Paso a Paso)

Si prefieres instalar el plugin sin dependencias externas:

1. **Descargar los artefactos:** Ve a la pestaña de *Releases* del repositorio y descarga los archivos:
   - `main.js`
   - `manifest.json`
   - `styles.css`
2. **Localizar la carpeta de plugins:** Abre el explorador de archivos en la ruta de tu bóveda de Obsidian y navega a la carpeta oculta:
   ```text
   <Tu_Boveda>/.obsidian/plugins/
   ```
3. **Crear el directorio de Synapse:** Crea una nueva carpeta con el nombre `synapse4d`:
   ```text
   <Tu_Boveda>/.obsidian/plugins/synapse4d/
   ```
4. **Copiar los archivos:** Pega `main.js`, `manifest.json` y `styles.css` dentro de la carpeta creada.
5. **Recargar y Activar:** Abre Obsidian, dirígete a *Ajustes > Plugins de la comunidad*, haz clic en **"Recargar plugins"** (icono de flecha circular) y activa el interruptor de **Synapse 4D**.

---

## 4. Primeros Pasos y Flujo de Trabajo

### A. Consolidar Memoria (Ciclo 4D)

Para absorber las bitácoras del día (`10_Memoria_Episodica/`) y convertirlas en hechos de largo plazo:
- **Desde Obsidian:** Abre la paleta de comandos (`Ctrl+P` o `Cmd+P`) y ejecuta:
  ```text
  Synapse 4D: Consolidate Memory
  ```
- **Desde la Terminal:**
  ```bash
  synapse consolidate --vault "C:\Ruta\A\Tu_Boveda"
  ```
El motor procesará las notas nuevas, detectará contradicciones mediante supersesión bi-temporal y actualizará el grafo en `.synapse/synapse_state.db`.

---

### B. Búsqueda Semántica de Hechos

Para consultar el estado actual de conocimientos sin depender de coincidencias exactas de palabras:
- **Desde Obsidian:** Ejecuta el comando `Synapse 4D: Search Memory` e introduce tu consulta conceptual (e.g., *"estrategia de base de datos"*).
- **Desde la Terminal:**
  ```bash
  synapse search "persistencia de base de datos" --vault "C:\Ruta\A\Tu_Boveda"
  ```

---

### C. Reversión Determinista (Undo)

Si una sesión de consolidación introdujo hechos erróneos o no deseados:
- **Desde Obsidian:** Ejecuta el comando `Synapse 4D: Rollback Last Session`.
- **Desde la Terminal:**
  ```bash
  synapse undo <SESSION_ID> --vault "C:\Ruta\A\Tu_Boveda"
  ```
El estado relacional restaurará de inmediato los hechos sustituidos y marcará los nuevos como invalidados.

---

## 5. Solución de Problemas (Troubleshooting)

### Problema 1: El plugin no arranca o la consola muestra errores

- **Diagnóstico:** Abre la consola de herramientas de desarrollo de Obsidian (`Ctrl+Shift+I` en Windows/Linux, `Cmd+Option+I` en macOS) y revisa la pestaña *Console*.
- **Causa común:** El plugin no puede comunicarse con el motor local o los permisos de archivo en `.synapse/` están bloqueados.
- **Solución:** Verifica que el directorio `.synapse/synapse.lock` no haya quedado bloqueado por un proceso huérfano. Si el fichero de bloqueo persiste tras reiniciar tu equipo, puedes eliminarlo con seguridad de `.synapse/synapse.lock`.

---

### Problema 2: "Binario no encontrado" o `synapse: command not found`

- **Causa común:** El entorno donde se ejecuta Obsidian no hereda las variables de entorno de tu terminal (`PATH`).
- **Solución:**
  1. Accede a *Ajustes de Obsidian > Synapse 4D*.
  2. En el campo **"Synapse CLI Path"**, en lugar de `synapse`, introduce la ruta absoluta al ejecutable de Python o del script:
     - Windows: `C:\Users\<Usuario>\AppData\Local\Programs\Python\Python310\Scripts\synapse.exe`
     - macOS/Linux: `/usr/local/bin/synapse` o el `bin/synapse` de tu virtualenv.

---

### Problema 3: Rutas con espacios en blanco (ej. `C:\Users\ANGEL RUIZ\...`)

- **Causa común:** Sistemas operativos Windows con nombres de usuario o carpetas que contienen espacios pueden romper la invocación por línea de comandos si no están adecuadamente escapadas.
- **Solución:**
  - En la configuración del plugin y en tus llamadas por CLI, **encapsula siempre la ruta de la bóveda entre comillas dobles**:
    ```bash
    synapse consolidate --vault "C:\Users\ANGEL RUIZ\Desktop\os ai"
    ```
  - Evita el uso de comillas simples en terminales de PowerShell para rutas con espacios, prefiriendo siempre `"` dobles.
