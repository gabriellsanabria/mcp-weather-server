#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar funcionalidades do servidor MCP.
Executa testes básicos sem precisar do Claude Desktop.
"""

import asyncio
import os
import sys
from pathlib import Path
from server import WeatherFilesServer

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configurar API key para testes (substitua pela sua)
os.environ["WEATHER_API_KEY"] = os.getenv("WEATHER_API_KEY", "")


async def test_weather():
    """Testa a funcionalidade de clima."""
    print("\nTestando get_weather...")
    server = WeatherFilesServer()
    
    try:
        result = await server._get_weather("São Paulo", "BR")
        print(result)
        print("Teste de clima concluído com sucesso.")
    except Exception as e:
        print(f"Teste de clima falhou: {e}")
    finally:
        await server.cleanup()


async def test_read_file():
    """Testa a leitura de arquivos."""
    print("\nTestando read_file...")
    server = WeatherFilesServer()
    
    # Criar arquivo de teste
    test_file = Path("test_file.txt")
    test_file.write_text("Este é um arquivo de teste para o MCP server!")
    
    try:
        result = await server._read_file(str(test_file))
        print(result)
        print("Teste de leitura concluído com sucesso.")
    except Exception as e:
        print(f"Teste de leitura falhou: {e}")
    finally:
        # Limpar
        if test_file.exists():
            test_file.unlink()
        await server.cleanup()


async def test_list_directory():
    """Testa a listagem de diretórios."""
    print("\nTestando list_directory...")
    server = WeatherFilesServer()
    
    try:
        result = await server._list_directory(".")
        print(result)
        print("Teste de listagem concluído com sucesso.")
    except Exception as e:
        print(f"Teste de listagem falhou: {e}")
    finally:
        await server.cleanup()


async def test_location_facts():
    """Testa os fatos geográficos."""
    print("\nTestando get_location_facts...")
    server = WeatherFilesServer()
    
    try:
        result = await server._get_location_facts("Brazil")
        print(result)
        print("Teste de fatos geográficos concluído com sucesso.")
    except Exception as e:
        print(f"Teste de fatos geográficos falhou: {e}")
    finally:
        await server.cleanup()


async def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("Iniciando Suite de Testes - MCP Weather & Files AI Server")
    print("=" * 60)
    
    await test_location_facts()
    await test_list_directory()
    await test_read_file()
    await test_weather()  # Por último pois requer API key
    
    print("\n" + "=" * 60)
    print("Testes finalizados.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
