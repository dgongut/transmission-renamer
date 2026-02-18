import re
import sys
import warnings

# Suprimir el warning de urllib3 sobre OpenSSL/LibreSSL
warnings.filterwarnings('ignore', message='.*urllib3 v2 only supports OpenSSL.*')

try:
    import transmission_rpc
except ImportError:
    print("❌ Error: Se requiere la librería transmission-rpc")
    print("Instálala con: pip install transmission-rpc")
    sys.exit(1)


def parse_name(filename: str):
    # Extensiones de video válidas
    valid_extensions = {'mkv', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mpg', 'mpeg', 'm4v', 'ts', 'm2ts'}

    # Separar extensión solo si es válida
    ext = ""
    name = filename

    if "." in filename:
        potential_name, potential_ext = filename.rsplit(".", 1)
        if potential_ext.lower() in valid_extensions:
            name = potential_name
            ext = potential_ext
        else:
            # No tiene extensión de video válida, retornar None
            return None
    else:
        # No tiene extensión, retornar None
        return None

    # Buscar año (puede estar entre paréntesis o no)
    year_match = re.search(r'\(?(19|20)\d{2}\)?', name)
    if not year_match:
        return None

    year = re.search(r'(19|20)\d{2}', year_match.group()).group()

    # Parte del título antes del año
    title_part = name[:year_match.start()]

    # Limpiar separadores y paréntesis del título
    title = re.sub(r'[._]', ' ', title_part)
    title = re.sub(r'\s+', ' ', title).strip()
    # Eliminar paréntesis sobrantes al final del título
    title = re.sub(r'\s*\(\s*$', '', title).strip()

    # Detectar REMUX primero (tiene prioridad sobre resolución)
    remux_match = re.search(r'(UHD)?\.?remux', name, re.IGNORECASE)

    resolution = ""
    if remux_match:
        # Es un remux
        if remux_match.group(1):  # UHDRemux
            resolution = "UHDRemux"
        else:  # BDRemux o simplemente Remux
            if re.search(r'BD\.?remux', name, re.IGNORECASE):
                resolution = "BDRemux"
            else:
                resolution = "Remux"
    else:
        # Resolución normal (añadido 1080i, 720i, 480p, etc.)
        if re.search(r'2160p|4k|uhd', name, re.IGNORECASE):
            resolution = "4K"
        elif re.search(r'1080[pi]', name, re.IGNORECASE):
            resolution = "1080p"
        elif re.search(r'720[pi]', name, re.IGNORECASE):
            resolution = "720p"
        elif re.search(r'480[pi]', name, re.IGNORECASE):
            resolution = "480p"

    # HDR
    hdr = ""
    if re.search(r'HDR|HDR10|Dolby.?Vision|DV', name, re.IGNORECASE):
        hdr = " HDR"

    # Construcción final (siempre con extensión porque ya validamos antes)
    if resolution:
        result = f"{title} ({year}) - {resolution}{hdr}.{ext}"
    else:
        # Si no hay resolución, no poner el guión
        result = f"{title} ({year}){hdr}.{ext}" if hdr else f"{title} ({year}).{ext}"

    return result


def rename_transmission_torrents(host, port, username=None, password=None):
    """Conecta a Transmission y renombra torrents de manera interactiva"""

    print("🔄 Conectando a Transmission en {}:{}...".format(host, port))

    try:
        if username and password:
            client = transmission_rpc.Client(host=host, port=port, username=username, password=password)
        else:
            client = transmission_rpc.Client(host=host, port=port)
        print("✅ Conectado correctamente\n")
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return

    # Obtener todos los torrents ordenados por fecha de adición (más recientes primero)
    try:
        torrents = client.get_torrents()
        # Intentar ordenar por addedDate, si no existe usar el orden por defecto
        try:
            torrents.sort(key=lambda t: t.addedDate if hasattr(t, 'addedDate') else t.id, reverse=True)
        except:
            pass  # Si falla, mantener el orden original
        print(f"📦 Se encontraron {len(torrents)} torrents\n")
    except Exception as e:
        print(f"❌ Error al obtener torrents: {e}")
        return

    # Procesar cada torrent
    renamed_count = 0
    skipped_count = 0

    try:
        for torrent in torrents:
            original_name = torrent.name

            # Intentar parsear el nombre
            new_name = parse_name(original_name)

            # Si no se pudo parsear o el nombre es igual, saltar
            if not new_name or new_name == original_name:
                continue

            print("─" * 60)
            print(f"📁 Original: {original_name}")
            print(f"✨ Nuevo:    {new_name}")
            print()

            while True:
                response = input("¿Es correcto? (s/n/editar/cancelar): ").strip().lower()

                if response in ['s', 'si', 'sí', 'y', 'yes']:
                    # Renombrar el torrent
                    try:
                        client.rename_torrent_path(torrent.id, original_name, new_name)
                        print("✅ Renombrado correctamente\n")
                        renamed_count += 1
                        break
                    except Exception as e:
                        print(f"❌ Error al renombrar: {e}\n")
                        skipped_count += 1
                        break

                elif response in ['n', 'no']:
                    print("❌ Omitido\n")
                    skipped_count += 1
                    break

                elif response in ['e', 'editar', 'edit']:
                    custom_name = input("Introduce el nuevo nombre: ").strip()
                    if custom_name:
                        try:
                            client.rename_torrent_path(torrent.id, original_name, custom_name)
                            print("✅ Renombrado correctamente\n")
                            renamed_count += 1
                            break
                        except Exception as e:
                            print(f"❌ Error al renombrar: {e}\n")
                            skipped_count += 1
                            break
                    else:
                        print("❌ Nombre vacío, omitido\n")
                        skipped_count += 1
                        break

                elif response in ['c', 'cancelar', 'cancel']:
                    print("\n❌ Proceso cancelado por el usuario")
                    print("=" * 60)
                    print(f"✅ Renombrados hasta ahora: {renamed_count}")
                    print(f"⏭️  Omitidos: {skipped_count}")
                    return

                else:
                    print("⚠️  Opción no válida. Usa: s/n/editar/cancelar")

    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        print("=" * 60)
        print(f"✅ Renombrados hasta ahora: {renamed_count}")
        print(f"⏭️  Omitidos: {skipped_count}")
        return

    print("=" * 60)
    print(f"✅ Renombrados: {renamed_count}")
    print(f"⏭️  Omitidos: {skipped_count}")
    print(f"📊 Total procesados: {renamed_count + skipped_count}")


def interactive_mode():
    """Modo interactivo para probar el parser"""
    print("Renombrador de películas - Modo de prueba")
    print("Escribe 'salir' para terminar\n")

    try:
        while True:
            text = input("Nombre original: ").strip()

            if text.lower() == "salir":
                break

            new_name = parse_name(text)

            if new_name:
                print("→", new_name)
            else:
                print("❌ No se pudo procesar")

            print()
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo del modo de prueba...")
        return


if __name__ == "__main__":
    try:
        print("=" * 60)
        print("🎬 Renombrador de Películas para Transmission")
        print("=" * 60)
        print()
        print("Selecciona una opción:")
        print("1. Renombrar torrents en Transmission")
        print("2. Modo de prueba (probar nombres)")
        print()

        choice = input("Opción (1/2): ").strip()
        print()

        if choice == "1":
            # Pedir configuración de Transmission
            print("Configuración de Transmission:")
            print("-" * 60)
            host = input("Host (por defecto: localhost): ").strip() or "localhost"
            port_input = input("Puerto (por defecto: 9091): ").strip()
            port = int(port_input) if port_input else 9091

            username = input("Usuario (dejar vacío si no tiene): ").strip() or None
            password = None
            if username:
                password = input("Contraseña: ").strip() or None

            print()
            rename_transmission_torrents(host, port, username, password)
        elif choice == "2":
            interactive_mode()
        else:
            print("❌ Opción no válida")

    except KeyboardInterrupt:
        print("\n\n👋 Programa cancelado por el usuario. ¡Hasta luego!")
        sys.exit(0)
