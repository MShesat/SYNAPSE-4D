---
name: Bug Report
about: Informar sobre un fallo, error o comportamiento inesperado en Synapse 4D
title: "[BUG]: "
labels: ["bug"]
assignees: ""
---

### Descripción del Error
Una descripción concisa y clara de cuál es el problema detectado.

### Información del Entorno
- **Versión de Synapse 4D:** (ej. `2.0.0` o salida de `synapse --version`)
- **Sistema Operativo:** (ej. Windows 11 x64, macOS Sonoma M2, Ubuntu 22.04 LTS)
- **Versión de Python:** (ej. `Python 3.10.12` / `Python 3.11.8` - salida de `python --version`)
- **Tipo de Bóveda / Almacenamiento:** (Local SSD, red, ruta con espacios, etc.)

### Pasos para Reproducir
Indica los pasos exactos para reproducir el fallo:
1. Ejecutar comando `synapse ...` o realizar acción en Obsidian.
2. Estado previo de la bóveda (archivos en `10_Episodic_Memory/`, etc.).
3. Observar el error en la terminal o interfaz.

### Comportamiento Esperado
Describe qué debería haber ocurrido de acuerdo con la especificación del motor.

### Salida del Comando de Auditoría (`synapse audit`)
Por favor, ejecuta `synapse audit --vault <RUTA_BOVEDA>` y pega la salida JSON / texto aquí:
```json
{
  // Pega aquí la salida de 'synapse audit'
}
```

### Log de Error / Traza de la Excepción (Traceback)
Si obtuviste un mensaje de error o traceback de Python en consola, pégalo a continuación:
```text
// Pega aquí la traza de error completa
```

### Contexto Adicional
Cualquier otro detalle sobre la configuración, plugins activos de Obsidian, o eventos concurrentes en el momento del fallo.
