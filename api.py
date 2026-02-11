import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Any
from server import WeatherFilesServer
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MCP Weather & Files AI Dashboard API")

# Configuração de CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar o servidor MCP (reutilizando a lógica)
mcp_server = WeatherFilesServer()

class ToolRequest(BaseModel):
    tool_name: str
    arguments: dict

@app.get("/api/tools")
async def list_tools():
    """Lista as ferramentas disponíveis no servidor."""
    # Como não temos um objeto direto fácil sem rodar o server.run(), 
    # vamos retornar uma lista estática baseada na definição do server.py
    return [
        {
            "name": "get_weather",
            "description": "Dados meteorológicos em tempo real",
            "params": ["city", "country_code"]
        },
        {
            "name": "read_file",
            "description": "Leitura segura de arquivos locais",
            "params": ["file_path"]
        },
        {
            "name": "list_directory",
            "description": "Navegação em diretórios locais",
            "params": ["directory_path"]
        },
        {
            "name": "get_location_facts",
            "description": "Informações geográficas de países",
            "params": ["country"]
        },
        {
            "name": "analyze_with_ai",
            "description": "Análise inteligente com provedores de IA",
            "params": ["prompt", "context"]
        }
    ]

@app.post("/api/execute")
async def execute_tool(request: ToolRequest):
    """Executa uma ferramenta MCP via HTTP."""
    try:
        name = request.tool_name
        args = request.arguments
        
        if name == "get_weather":
            result = await mcp_server._get_weather(args.get("city"), args.get("country_code", ""))
        elif name == "read_file":
            result = await mcp_server._read_file(args.get("file_path"))
        elif name == "list_directory":
            result = await mcp_server._list_directory(args.get("directory_path"))
        elif name == "get_location_facts":
            result = await mcp_server._get_location_facts(args.get("country"))
        elif name == "analyze_with_ai":
            result = await mcp_server._analyze_with_ai(args.get("prompt"), args.get("context", ""))
        else:
            raise HTTPException(status_code=404, detail="Ferramenta não encontrada")
            
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Servir arquivos estáticos do dashboard (será criado a seguir)
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
