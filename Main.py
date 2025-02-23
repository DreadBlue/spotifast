from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
        key: int
        nombre: str
        correo: str
        contrasena: str
        canciones: list[str]
        
class Cancion(BaseModel):
        key: int
        nombre: str
        artista: str

@app.get("/api/productos/{cancion}")
def obtener_cancion(cancion: str):
    url = 'https://accounts.spotify.com/api/token'
