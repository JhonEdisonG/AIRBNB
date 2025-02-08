from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from supabase import create_client, Client
import os

app = FastAPI()
SUPABASE_URL = "https://otaedzxedjzadltjtvzu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im90YWVkenhlZGp6YWRsdGp0dnp1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkwNTA1NDUsImV4cCI6MjA1NDYyNjU0NX0.mPZLDBWtfzcq-rEatzAlzWGrwggABZlmLP4EyL1VfZ4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
@app.get("/")
def home():
    return FileResponse("PAGINAS/page.html")

#------------------------------------------------------------------




@app.get("/propiedades")
def get_propiedades():
    response = supabase.table("propiedades").select("*").execute()
    return response
