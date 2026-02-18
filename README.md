# 🎬 Transmission Renamer

Script de Python para **renombrar automáticamente películas en Transmission** siguiendo un formato estandarizado y limpio.

## ✨ Características

- 🔍 **Parseo inteligente** de nombres de películas detectando:
  - Título de la película
  - Año (1900-2099)
  - Resolución (4K, 1080p, 720p, 480p)
  - Formatos especiales (UHDRemux, BDRemux, Remux)
  - HDR/Dolby Vision
  - Extensiones de video válidas

- 🔄 **Renombrado interactivo** en Transmission:
  - Conexión vía RPC a tu servidor Transmission
  - Muestra sugerencias de renombrado antes de aplicar cambios
  - Permite confirmar, omitir, editar manualmente o cancelar cada cambio
  - Ordena torrents por fecha de adición (más recientes primero)

- 🧪 **Modo de prueba** para testear el parser sin conectar a Transmission

## 📋 Formato de salida

```
Título (Año) - Resolución HDR.ext
```

**Ejemplos:**
- `The Matrix (1999) - 1080p HDR.mkv`
- `Inception (2010) - 4K.mkv`
- `Interstellar (2014) - 1080p Remux.mkv`

## 🚀 Instalación

### Requisitos previos
- Python 3.x
- Transmission con RPC habilitado

### Instalar dependencias

```bash
pip3 install transmission-rpc
```

## 💻 Uso

Ejecuta el script:

```bash
python3 transmission-renamer.py
```

Se te presentarán dos opciones:

### 1️⃣ Renombrar torrents en Transmission

El script te pedirá la configuración de conexión:
- **Host** (por defecto: `localhost`)
- **Puerto** (por defecto: `9091`)
- **Usuario** (opcional, si tienes autenticación)
- **Contraseña** (opcional, si tienes autenticación)

Luego te mostrará cada torrent con su nombre actual y el nombre sugerido.

**Opciones disponibles para cada torrent:**
- `s` / `si` / `yes` - Aceptar el renombrado sugerido
- `n` / `no` - Omitir este torrent
- `e` / `editar` - Introducir un nombre personalizado
- `c` / `cancelar` - Cancelar todo el proceso

### 2️⃣ Modo de prueba (solo parseo)

Prueba cómo se renombrarían archivos sin conectar a Transmission. Introduce nombres de archivos y verás el resultado sugerido.

```
Nombre original: Nombre.de.la.Pelicula.2024.1080p.BluRay.x264.mkv
→ Nombre de la Pelicula (2024) - 1080p.mkv
```

Escribe `salir` para terminar el modo de prueba.

## 📝 Notas

- El script mantiene la extensión original del archivo
- Solo procesa archivos de video con extensiones válidas (`.mkv`, `.mp4`, `.avi`, etc.)
- Los torrents se procesan de más reciente a más antiguo
- Puedes interrumpir el proceso en cualquier momento con `Ctrl+C`

## 🤝 Contribuir

Este script te permitirá renombrar tus contenidos a través de Transmission para seguir compartiendo de manera organizada.
