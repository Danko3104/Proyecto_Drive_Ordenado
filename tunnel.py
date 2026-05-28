#!/usr/bin/env python3
"""
Script para iniciar túnel Cloudflare con URL visible
Muestra la URL de forma destacada para fácil acceso
"""

import subprocess
import sys
import time
import re
import threading

def print_banner():
    """Imprime banner de inicio"""
    print("\n" + "="*50)
    print("       🚀 INICIANDO TÚNEL CLOUDFLARE")
    print("="*50)
    print("\n⏳  Generando URL segura...")
    print("   (Esto puede tomar unos segundos)\n")

def print_url(url):
    """Imprime la URL de forma destacada"""
    print("\n" + "🎉"*25)
    print("\n" + " "*10 + "✅ TÚNEL LISTO")
    print("\n" + "="*50)
    print("           🌐 TU URL PÚBLICA:")
    print("")
    print(f"    {url}")
    print("")
    print("="*50)
    print("     📋 Copia y comparte esta URL")
    print("        para acceder desde cualquier")
    print("        dispositivo con internet")
    print("="*50)
    print("\n   Presiona Ctrl+C para detener\n")

def monitor_output(process):
    """Monitorea la salida del proceso para encontrar la URL"""
    url_found = False
    url_pattern = r'https://[a-z0-9-]+\.trycloudflare\.com'

    for line in iter(process.stdout.readline, ''):
        line = line.strip()

        # Buscar la URL en la línea
        if not url_found:
            match = re.search(url_pattern, line)
            if match:
                url = match.group(0)
                print_url(url)
                url_found = True

        # Imprimir líneas importantes
        if 'INF' in line and ('Tunnel' in line or 'connection' in line):
            print(f"   [OK] {line.split('INF')[-1].strip()}")

    process.stdout.close()

def main():
    print_banner()

    try:
        # Iniciar cloudflared
        process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', 'http://localhost:5000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Monitorear salida en un hilo separado
        monitor_thread = threading.Thread(target=monitor_output, args=(process,))
        monitor_thread.daemon = True
        monitor_thread.start()

        # Esperar al proceso
        process.wait()

    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo túnel...")
        if 'process' in locals():
            process.terminate()
            process.wait(timeout=5)
        print("✅ Túnel detenido")
        sys.exit(0)

    except FileNotFoundError:
        print("\n❌ Error: cloudflared no está instalado")
        print("   Instálalo con: pip install cloudflared")
        sys.exit(1)

if __name__ == '__main__':
    main()
