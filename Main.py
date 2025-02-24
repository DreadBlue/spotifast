from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import base64
import json

app = FastAPI()
registro = "registro.json"

class User(BaseModel):
        key: int
        nombre: str
        correo: str
        contrasena: str
        
class CancionRequest(BaseModel):
        cancion: str
        correo: str

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

@app.post("/api/usuario")
def crear_usuario(usuario: User):
    newUser = usuario.dict()
    try: 
        with open(registro, 'r') as file:
          registros = json.load(file)

    except json.JSONDecodeError:
         registros = []
    
    registros.append(newUser)

    with open(registro, 'w') as file:
          json.dump(registros, file, indent=4)

    return {"message": "usuario agregado"}

@app.get("/api/usuarios")
def obtener_usuarios():
    try:
        with open(registro, 'r') as file:
            registros = json.load(file)
        return registros
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.get("/api/usuario/{correo}")
def obtener_usuario(correo: str):
    try:
        with open(registro, 'r') as file:
            registros = json.load(file)
        for user in registros:
            if user["correo"] == correo:
                return user
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except (FileNotFoundError, json.JSONDecodeError):
        return {"message": "No hay usuarios registrados"}

@app.put("/api/usuario/{correo}")
def actualizar_usuario(correo: str, usuario_actualizado: User):
    try:
        with open(registro, 'r') as file:
            registros = json.load(file)
        
        for i, user in enumerate(registros):
            if user["correo"] == correo:
                registros[i] = usuario_actualizado.dict()
                with open(registro, 'w') as file:
                    json.dump(registros, file, indent=4)
                return {"message": "Usuario actualizado"}
        
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except (FileNotFoundError, json.JSONDecodeError):
        return {"message": "No hay usuarios registrados"}

@app.delete("/api/usuario/{correo}")
def eliminar_usuario(correo: str):
    try:
        with open(registro, 'r') as file:
            registros = json.load(file)

        for i, user in enumerate(registros):
            if user["correo"] == correo:
                del registros[i]
                with open(registro, 'w') as file:
                    json.dump(registros, file, indent=4)
                return {"message": "Usuario eliminado"}

        return {"message": "Usuario no encontrado"}
    
    except (FileNotFoundError, json.JSONDecodeError):
        return {"message": "No hay usuarios registrados"}
    
@app.post("/api/cancion/")
def agregar_cancion(cancionRequest: CancionRequest):
    cancion = cancionRequest.cancion
    correo = cancionRequest.correo 
    url = 'https://accounts.spotify.com/api/token'
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    token_info = response.json().get("access_token")

    if not token_info:
        return {"message": "No se ha podido obtener el token"}

    search_url = f"https://api.spotify.com/v1/search?q={cancion}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {token_info}"}

    response = requests.get(search_url, headers=headers)
    data = response.json()

    cancion_data = data["tracks"]["items"][0]
    cancion_info = {
        "nombre": cancion_data["name"],
        "artista": cancion_data["artists"][0]["name"],
        "url": cancion_data["external_urls"]["spotify"]
    }

    with open(registro, 'r') as file:
        registros = json.load(file)
    
    for user in registros:
         if user["correo"] == correo:
            if "canciones" not in user:
                user["canciones"] = []
            user["canciones"].append(cancion_info)
            break

    with open(registro, 'w') as file:
          json.dump(registros, file, indent=4)

    return {"message": "cancion agregada con exito"}