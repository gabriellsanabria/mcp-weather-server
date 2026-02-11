#!/usr/bin/env python3
"""
MCP Weather & Files Server
Um servidor MCP avançado que conecta Claude/Gemini a APIs externas e sistemas locais.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-weather-server")

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI SDK não instalado")

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic SDK não instalado")


# Carregar variáveis de ambiente
load_dotenv()

# Configurações
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_API_BASE = "https://api.openweathermap.org/data/2.5"

# Configurações de IA
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Validações
if not WEATHER_API_KEY:
    logger.warning("WEATHER_API_KEY não configurada. Funcionalidade de clima limitada.")

if not OPENAI_API_KEY and not ANTHROPIC_API_KEY:
    logger.warning("Nenhuma API de IA configurada. Funcionalidade de análise limitada.")
elif OPENAI_API_KEY:
    logger.info("OpenAI configurada como provedor primário")
elif ANTHROPIC_API_KEY:
    logger.info("Anthropic configurada como provedor único")


class WeatherFilesServer:
    """Servidor MCP que oferece clima, arquivos e fatos geográficos."""
    
    def __init__(self):
        self.server = Server("weather-files-ai-server")
        self.http_client: Optional[httpx.AsyncClient] = None
        
        # Configurar clientes de IA
        self.openai_client: Optional[AsyncOpenAI] = None
        self.anthropic_client: Optional[AsyncAnthropic] = None
        
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            
        if ANTHROPIC_AVAILABLE and ANTHROPIC_API_KEY:
            self.anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura os handlers do servidor MCP."""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """Lista todas as ferramentas disponíveis."""
            return [
                Tool(
                    name="get_weather",
                    description=(
                        "Obtém informações meteorológicas em tempo real para qualquer cidade. "
                        "Retorna temperatura, condições, umidade e velocidade do vento."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "Nome da cidade (ex: 'São Paulo', 'New York')"
                            },
                            "country_code": {
                                "type": "string",
                                "description": "Código do país opcional (ex: 'BR', 'US')",
                                "default": ""
                            }
                        },
                        "required": ["city"]
                    }
                ),
                Tool(
                    name="read_file",
                    description=(
                        "Lê o conteúdo de um arquivo local. "
                        "Suporta arquivos de texto (txt, json, py, md, etc.)."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Caminho completo ou relativo do arquivo"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="list_directory",
                    description=(
                        "Lista todos os arquivos e pastas em um diretório. "
                        "Útil para explorar o sistema de arquivos antes de ler arquivos específicos."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Caminho do diretório a ser listado"
                            }
                        },
                        "required": ["directory_path"]
                    }
                ),
                Tool(
                    name="get_location_facts",
                    description=(
                        "Retorna fatos interessantes sobre um país, incluindo "
                        "população, capital, idiomas, moeda e região."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "country": {
                                "type": "string",
                                "description": "Nome do país (ex: 'Brasil', 'Japan')"
                            }
                        },
                        "required": ["country"]
                    }
                ),
                Tool(
                    name="analyze_with_ai",
                    description=(
                        "Usa IA generativa (OpenAI primária, Anthropic fallback) para analisar, "
                        "responder perguntas complexas, fazer recomendações ou processar dados. "
                        "Ideal para análises de clima, interpretação de dados geográficos, sugestões de viagem, etc."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Pergunta ou prompt de análise"
                            },
                            "context": {
                                "type": "string",
                                "description": "Contexto adicional ou dados para análise (opcional)",
                                "default": ""
                            }
                        },
                        "required": ["prompt"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Executa uma ferramenta específica."""
            try:
                if name == "get_weather":
                    result = await self._get_weather(
                        arguments.get("city"),
                        arguments.get("country_code", "")
                    )
                elif name == "read_file":
                    result = await self._read_file(arguments.get("file_path"))
                elif name == "list_directory":
                    result = await self._list_directory(arguments.get("directory_path"))
                elif name == "get_location_facts":
                    result = await self._get_location_facts(arguments.get("country"))
                elif name == "analyze_with_ai":
                    result = await self._analyze_with_ai(
                        arguments.get("prompt"),
                        arguments.get("context", "")
                    )
                else:
                    result = f"Erro: Ferramenta '{name}' não encontrada"
                
                return [TextContent(type="text", text=result)]
            
            except Exception as e:
                logger.error(f"Erro ao executar {name}: {str(e)}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Erro ao executar {name}: {str(e)}"
                )]
    
    async def _get_weather(self, city: str, country_code: str = "") -> str:
        """Obtém dados meteorológicos da OpenWeatherMap."""
        if not WEATHER_API_KEY:
            return "WEATHER_API_KEY não configurada. Configure a variável de ambiente."
        
        try:
            # Construir query
            query = f"{city},{country_code}" if country_code else city
            
            # Fazer requisição
            url = f"{WEATHER_API_BASE}/weather"
            params = {
                "appid": WEATHER_API_KEY,
                "q": query,
                "units": "metric",
                "lang": "pt_br"
            }
            
            if not self.http_client:
                self.http_client = httpx.AsyncClient(timeout=10.0)
            
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Processar dados
            name = data.get("name", city)
            sys = data.get("sys", {})
            country = sys.get("country", "")
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            wind = data.get("wind", {})
            
            # Converter timezone de segundos para formato legível
            # OpenWeather não envia hora local formatada, apenas o offset da timezone
            
            result = f"""
**Clima em {name}, {country}**

Localização: {name}, {country}

**Temperatura**
- Atual: {main.get('temp')}°C
- Sensação: {main.get('feels_like')}°C
- Mínima: {main.get('temp_min')}°C
- Máxima: {main.get('temp_max')}°C

**Condições**
- {weather.get('description', 'N/A').capitalize()}
- Umidade: {main.get('humidity')}%
- Vento: {wind.get('speed')} m/s ({wind.get('deg')}°)
- Pressão: {main.get('pressure')} hPa
- Visibilidade: {data.get('visibility', 0) / 1000} km
            """.strip()
            
            logger.info(f"Clima obtido com sucesso para {city}")
            return result
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f" Cidade '{city}' não encontrada no OpenWeatherMap. Verifique o nome."
            return f" Erro na API OpenWeatherMap (HTTP {e.response.status_code})"
        except Exception as e:
            logger.error(f"Erro ao obter clima: {str(e)}")
            return f" Erro ao obter clima: {str(e)}"
    
    async def _read_file(self, file_path: str) -> str:
        """Lê o conteúdo de um arquivo de forma segura."""
        try:
            # Normalizar caminho
            path = Path(file_path).resolve()
            
            # Validações de segurança
            if not path.exists():
                return f" Arquivo não encontrado: {file_path}"
            
            if not path.is_file():
                return f" O caminho não é um arquivo: {file_path}"
            
            # Ler arquivo
            content = path.read_text(encoding='utf-8', errors='replace')
            
            # Limitar tamanho da resposta
            max_chars = 10000
            if len(content) > max_chars:
                content = content[:max_chars] + f"\n\n... (truncado, arquivo tem {len(content)} caracteres)"
            
            result = f"""
**Arquivo: {path.name}**
Caminho: {path}
Tamanho: {path.stat().st_size} bytes

---
{content}
            """.strip()
            
            logger.info(f"Arquivo lido com sucesso: {file_path}")
            return result
        
        except PermissionError:
            return f" Sem permissão para ler o arquivo: {file_path}"
        except UnicodeDecodeError:
            return f" Arquivo não é de texto ou usa encoding não suportado: {file_path}"
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {str(e)}")
            return f" Erro ao ler arquivo: {str(e)}"
    
    async def _list_directory(self, directory_path: str) -> str:
        """Lista conteúdo de um diretório."""
        try:
            path = Path(directory_path).resolve()
            
            if not path.exists():
                return f" Diretório não encontrado: {directory_path}"
            
            if not path.is_dir():
                return f" O caminho não é um diretório: {directory_path}"
            
            # Listar conteúdo
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            if not items:
                return f"Diretório vazio: {path}"
            
            # Formatar resultado
            lines = [f"**Conteúdo de: {path}**\n"]
            
            for item in items[:100]:  # Limitar a 100 itens
                prefix = "[DIR]" if item.is_dir() else "[FILE]"
                size = ""
                if item.is_file():
                    size_bytes = item.stat().st_size
                    if size_bytes < 1024:
                        size = f" ({size_bytes} bytes)"
                    elif size_bytes < 1024 * 1024:
                        size = f" ({size_bytes / 1024:.1f} KB)"
                    else:
                        size = f" ({size_bytes / (1024 * 1024):.1f} MB)"
                
                lines.append(f"{prefix} {item.name}{size}")
            
            if len(list(path.iterdir())) > 100:
                lines.append(f"\n... e mais {len(list(path.iterdir())) - 100} itens")
            
            logger.info(f"Diretório listado com sucesso: {directory_path}")
            return "\n".join(lines)
        
        except PermissionError:
            return f" Sem permissão para acessar o diretório: {directory_path}"
        except Exception as e:
            logger.error(f"Erro ao listar diretório: {str(e)}")
            return f" Erro ao listar diretório: {str(e)}"
    
    async def _get_location_facts(self, country: str) -> str:
        """Obtém fatos sobre um país usando RestCountries API."""
        try:
            if not self.http_client:
                self.http_client = httpx.AsyncClient(timeout=10.0)
            
            # Buscar informações do país
            url = f"https://restcountries.com/v3.1/name/{country}"
            response = await self.http_client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return f" País '{country}' não encontrado"
            
            # Pegar o primeiro resultado
            info = data[0]
            
            # Extrair dados
            name = info["name"]["common"]
            official_name = info["name"]["official"]
            capital = info.get("capital", ["N/A"])[0]
            population = info.get("population", 0)
            area = info.get("area", 0)
            region = info.get("region", "N/A")
            subregion = info.get("subregion", "N/A")
            
            # Idiomas
            languages = info.get("languages", {})
            lang_str = ", ".join(languages.values()) if languages else "N/A"
            
            # Moedas
            currencies = info.get("currencies", {})
            currency_list = []
            for code, curr_info in currencies.items():
                currency_list.append(f"{curr_info['name']} ({curr_info.get('symbol', code)})")
            curr_str = ", ".join(currency_list) if currency_list else "N/A"
            
            # Bandeira emoji
            flag = info.get("flag", "🏴")
            
            result = f"""
**{name}**

**Informações Gerais**
- Nome Oficial: {official_name}
- Capital: {capital}
- Região: {region} ({subregion})

**Demografia**
- População: {population:,}
- Área: {area:,} km²
- Densidade: {population/area:.1f} hab/km²

**Idiomas**
- {lang_str}

**Moeda**
- {curr_str}

**Outros**
- Código: {info.get('cca2', 'N/A')} / {info.get('cca3', 'N/A')}
- Fuso Horário: {', '.join(info.get('timezones', ['N/A'])[:3])}
            """.strip()
            
            logger.info(f"Fatos obtidos com sucesso para {country}")
            return result
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return f" País '{country}' não encontrado. Verifique o nome."
            return f" Erro na API (HTTP {e.response.status_code})"
        except Exception as e:
            logger.error(f"Erro ao obter fatos: {str(e)}")
            return f" Erro ao obter fatos: {str(e)}"
    
    async def _analyze_with_ai(self, prompt: str, context: str = "") -> str:
        """Usa IA generativa para análise (OpenAI primária, Anthropic fallback)."""
        
        # Construir mensagem completa
        full_prompt = prompt
        if context:
            full_prompt = f"Contexto: {context}\n\nPergunta: {prompt}"
        
        # Tentar OpenAI primeiro
        if self.openai_client:
            try:
                logger.info("🤖 Usando OpenAI para análise...")
                response = await self.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Você é um assistente inteligente especializado em análise de dados, "
                                "clima, geografia e recomendações de viagem. Forneça respostas claras, "
                                "concisas e úteis em português."
                            )
                        },
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                result = response.choices[0].message.content
                logger.info("✅ Análise OpenAI concluída com sucesso")
                
                return f"""**Análise de IA (OpenAI {OPENAI_MODEL})**

{result}

---
Nota: Resposta gerada por IA - verifique informações críticas.""".strip()
            
            except Exception as e:
                logger.warning(f"OpenAI falhou, tentando fallback: {str(e)}")
                
                # Fallback para Anthropic
                if self.anthropic_client:
                    try:
                        logger.info("🤖 Usando Anthropic (fallback)...")
                        response = await self.anthropic_client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=1000,
                            messages=[
                                {"role": "user", "content": full_prompt}
                            ]
                        )
                        
                        result = response.content[0].text
                        logger.info("✅ Análise Anthropic concluída com sucesso")
                        
                        return f"""🤖 **Análise de IA (Claude via Anthropic - Fallback)**

{result}

---
💡 *Resposta gerada por IA - sempre verifique informações críticas*""".strip()
                    
                    except Exception as e2:
                        logger.error(f"Anthropic fallback também falhou: {str(e2)}")
                        return f" Erro em ambos provedores de IA:\nOpenAI: {str(e)}\nAnthropic: {str(e2)}"
                
                return f" OpenAI falhou e não há fallback configurado: {str(e)}"
        
        # Se não tem OpenAI, tentar Anthropic diretamente
        elif self.anthropic_client:
            try:
                logger.info("🤖 Usando Anthropic...")
                response = await self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ]
                )
                
                result = response.content[0].text
                logger.info("✅ Análise Anthropic concluída com sucesso")
                
                return f"""🤖 **Análise de IA (Claude via Anthropic)**

{result}

---
💡 *Resposta gerada por IA - sempre verifique informações críticas*""".strip()
            
            except Exception as e:
                logger.error(f"Erro ao usar Anthropic: {str(e)}")
                return f" Erro ao usar Anthropic: {str(e)}"
        
        else:
            return " Nenhum provedor de IA configurado. Configure OPENAI_API_KEY ou ANTHROPIC_API_KEY."
    
    async def run(self):
        """Executa o servidor MCP."""
        logger.info("Iniciando MCP Weather & Files AI Server...")
        logger.info(f"Weather API: {'Configurada' if WEATHER_API_KEY else 'Não configurada'}")
        
        # Status dos provedores de IA
        if self.openai_client:
            logger.info(f"OpenAI: Primária ({OPENAI_MODEL})")
        if self.anthropic_client:
            status = "Fallback" if self.openai_client else "Única"
            logger.info(f"Anthropic: {status}")
        if not self.openai_client and not self.anthropic_client:
            logger.warning("IA: Nenhum provedor configurado")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    async def cleanup(self):
        """Limpa recursos."""
        if self.http_client:
            await self.http_client.aclose()
        
        # Fechar clientes de IA se necessário
        if self.openai_client:
            await self.openai_client.close()
        if self.anthropic_client:
            await self.anthropic_client.close()


async def main():
    """Função principal."""
    server = WeatherFilesServer()
    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        await server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
