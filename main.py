from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = FastAPI()
app.mount("/estilos", StaticFiles(directory="estilos"), name="estilos")
app.mount("/paginas", StaticFiles(directory="paginas"), name="paginas")

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

class ReservationRequest(BaseModel):
    property_id: int
    user_id: int
    in_time: str
    out_time: str

# Rutas
@app.get("/")
def home():
    return FileResponse("paginas/page.html")

@app.post("/register")
async def register(user: RegisterRequest):
    try:
        # Verificar si el usuario ya existe
        existing_user = supabase.table("Users").select("*").eq("email", user.email).execute()
        if existing_user.data:
            return JSONResponse(content={"message": "El usuario ya existe"}, status_code=400)

        # Crear nuevo usuario
        new_user = {
            "name": user.name,
            "email": user.email,
            "password": user.password  # En un caso real, esto debería estar hasheado
        }
        response = supabase.table("Users").insert(new_user).execute()
        if response.status_code != 201:
            return JSONResponse(content={"message": "Error al registrar el usuario"}, status_code=500)
        
        return JSONResponse(content={"message": "Usuario registrado con éxito"}, status_code=201)
    except Exception as e:
        print(f"Error al registrar el usuario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al registrar el usuario: {str(e)}")

@app.post("/login")
async def login(user: LoginRequest):
    try:
        # Buscar usuario
        result = supabase.table("Users").select("*").eq("email", user.email).eq("password", user.password).execute()
        if not result.data:
            return JSONResponse(content={"message": "Correo o contraseña incorrectos"}, status_code=400)
        return JSONResponse(content={"message": "Inicio de sesión exitoso", "user_id": result.data[0]['id']}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reserve")
async def reserve(reservation: ReservationRequest):
    try:
        # Verificar si el usuario existe
        user = supabase.table("Users").select("*").eq("id", reservation.user_id).execute()
        if not user.data:
            return JSONResponse(content={"message": "Usuario no encontrado"}, status_code=404)

        # Convertir las fechas de string a datetime
        in_time = datetime.strptime(reservation.in_time, "%Y-%m-%d")
        out_time = datetime.strptime(reservation.out_time, "%Y-%m-%d")

        # Verificar que las fechas no sean anteriores al día actual
        if in_time < datetime.now() or out_time < datetime.now():
            return JSONResponse(content={"message": "No puedes reservar fechas pasadas"}, status_code=400)

        # Verificar si ya existe una reserva para la propiedad en esas fechas
        existing_reservation = supabase.table("Bookings").select("*").eq("property_id", reservation.property_id).gte("in_time", in_time.isoformat()).lte("out_time", out_time.isoformat()).execute()
        if existing_reservation.data:
            return JSONResponse(content={"message": "La propiedad ya está reservada en esas fechas"}, status_code=400)

        # Insertar la reserva en la base de datos
        new_reservation = {
            "property_id": reservation.property_id,
            "user_id": reservation.user_id,
            "in_time": in_time.isoformat(),
            "out_time": out_time.isoformat()
        }
        response = supabase.table("Bookings").insert(new_reservation).execute()

        if response.status_code != 201:
            return JSONResponse(content={"message": "Error al realizar la reserva"}, status_code=500)

        return JSONResponse(content={"message": "Reserva realizada con éxito"}, status_code=201)
    except Exception as e:
        print(f"Error al realizar la reserva: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al realizar la reserva: {str(e)}")