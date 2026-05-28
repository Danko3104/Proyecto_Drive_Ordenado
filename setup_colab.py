#!/usr/bin/env python3
"""
Setup automático para Drive Ordenado en Google Colab
Ejecuta este script y listo - hace todo automáticamente
"""

import subprocess
import os
import sys
import time

def run_command(cmd, description, shell=False):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n{'='*60}")
    print(f"⏳ {description}")
    print('='*60)

    try:
        if shell:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {description} - OK")
            if result.stdout:
                print(result.stdout[:500])  # Solo mostrar primeros 500 chars
            return True
        else:
            print(f"❌ Error en: {description}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           🚀 DRIVE ORDENADO - SETUP AUTOMÁTICO              ║
    ║                                                              ║
    ║   Este script hará todo por ti. Solo espera y listo 😉      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Paso 1: Verificar si estamos en el directorio correcto
    if not os.path.exists('app.py'):
        print("❌ Error: No estás en el directorio del proyecto")
        print("💡 Tip: Ejecuta primero: cd Proyecto_Drive_Ordenado")
        return

    # Paso 2: Instalar dependencias
    if not run_command([sys.executable, '-m', 'pip', 'install', '-q', 'flask', 'pandas', 'numpy'],
                      "Instalando dependencias"):
        return

    # Paso 3: Descargar cloudflared si no existe
    if not os.path.exists('./cloudflared-linux-amd64'):
        if not run_command(['wget', '-q', 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64'],
                          "Descargando cloudflared"):
            return
        run_command(['chmod', '+x', './cloudflared-linux-amd64'], "Dando permisos a cloudflared")
    else:
        print("\n✅ Cloudflared ya está descargado")

    # Paso 4: Iniciar Flask
    print(f"\n{'='*60}")
    print("⏳ Iniciando servidor Flask...")
    print('='*60)

    # Matar procesos previos
    subprocess.run(['pkill', '-f', 'python.*app.py'], capture_output=True)
    time.sleep(1)

    # Iniciar Flask en background
    flask_process = subprocess.Popen(
        [sys.executable, 'app.py'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(3)

    # Verificar que Flask está corriendo
    try:
        import urllib.request
        urllib.request.urlopen('http://localhost:5000', timeout=5)
        print("✅ Servidor Flask iniciado correctamente")
    except:
        print("❌ Error: Flask no respondió. Intenta ejecutar manualmente: python3 app.py")
        return

    # Paso 5: Crear túnel
    print(f"\n{'='*60}")
    print("⏳ Creando túnel público...")
    print("   Espera unos segundos...")
    print('='*60)

    import re

    tunnel_process = subprocess.Popen(
        ['./cloudflared-linux-amd64', 'tunnel', '--url', 'http://localhost:5000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    url = None
    timeout = 30
    start_time = time.time()

    for line in tunnel_process.stdout:
        if time.time() - start_time > timeout:
            break

        match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
        if match:
            url = match.group(0)
            break

    if url:
        print("\n" + "🎉"*25)
        print("\n" + "="*60)
        print("   ✅ ¡TODO LISTO! ABRE ESTA URL:")
        print("="*60)
        print(f"\n       {url}\n")
        print("="*60)
        print("   📝 Guárdala bien, es tu acceso a la app")
        print("="*60 + "\n")

        print("""
    ⚠️  INSTRUCCIONES IMPORTANTES:

    1. ✅ La URL de arriba está activa y funcionando
    2. 🌐 Ábrela en tu navegador (Chrome, Firefox, etc.)
    3. ⏳ Esta celda se queda corriendo - NO LA CIERRES
    4. 🛑 Cuando termines, puedes detener esta celda\n""")

        # Mantener el proceso corriendo
        try:
            for line in tunnel_process.stdout:
                if 'INF' in line and ('connection' in line.lower() or 'tunnel' in line.lower()):
                    print(f"  [OK] {line.strip()}")
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo túnel...")
            tunnel_process.terminate()
            flask_process.terminate()
    else:
        print("❌ No se pudo obtener la URL. Intenta ejecutar el script de nuevo.")
        tunnel_process.terminate()
        flask_process.terminate()

if __name__ == '__main__':
    main()
