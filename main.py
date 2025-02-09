from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from supabase import create_client, Client
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS para permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las origenes (en producción, especifica los dominios permitidos)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = "https://otaedzxedjzadltjtvzu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90YWVkenhlZGp6YWRsdGp0dnp1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkwNTA1NDUsImV4cCI6MjA1NDYyNjU0NX0.mPZLDBWtfzcq-rEatzAlzWGrwggABZlmLP4EyL1VfZ4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Modelos Pydantic
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# Rutas
@app.get("/")
def home():
    return FileResponse("PAGINAS/page.html")

@app.post("/register")
async def register(user: RegisterRequest):
    try:
        # Verificar si el usuario ya existe
        existing_user = supabase.table("usuarios").select("*").eq("email", user.email).execute()
        if existing_user.data:
            return JSONResponse(content={"message": "El usuario ya existe"}, status_code=400)

        # Crear nuevo usuario
        new_user = {
            "nombre": user.name,
            "email": user.email,
            "password": user.password  # En un caso real, esto debería estar hasheado
        }
        supabase.table("usuarios").insert(new_user).execute()
        return JSONResponse(content={"message": "Usuario registrado con éxito"}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
async def login(user: LoginRequest):
    try:
        # Buscar usuario
        result = supabase.table("usuarios").select("*").eq("email", user.email).eq("password", user.password).execute()
        if not result.data:
            return JSONResponse(content={"message": "Correo o contraseña incorrectos"}, status_code=400)
        return JSONResponse(content={"message": "Inicio de sesión exitoso"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))