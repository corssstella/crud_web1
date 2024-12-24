from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import asyncpg
from contextlib import asynccontextmanager

class Cake(BaseModel):
    id: int
    name: str
    description: str
    price: float

class Service(BaseModel):
    id: int
    name: str
    description: str

class Contact(BaseModel):
    address: str
    phone: str
    email: str

DATABASE_URL = "postgresql://postgres:2702@localhost:5432/CRUD_db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the BestCake API!"}

@app.get("/cakes/")
async def read_cakes():
    async with app.state.pool.acquire() as connection:
        cakes = await connection.fetch("SELECT * FROM cakes")
        return [{"id": cake["id"], "name": cake["name"], "description": cake["description"], "price": cake["price"]} for cake in cakes]

@app.get("/cakes/{id}")
async def read_cake(id: int):
    async with app.state.pool.acquire() as connection:
        cake = await connection.fetchrow("SELECT * FROM cakes WHERE id = $1", id)
        if cake:
            return {"id": cake["id"], "name": cake["name"], "description": cake["description"], "price": cake["price"]}
        raise HTTPException(status_code=404, detail="Торт не найден")

@app.post("/cakes/")
async def create_cake(cake: Cake):
    async with app.state.pool.acquire() as connection:
        await connection.execute("INSERT INTO cakes (name, description, price) VALUES ($1, $2, $3)", cake.name, cake.description, cake.price)
        return {"detail": "Торт успешно добавлен"}

@app.put("/cakes/{id}")
async def update_cake(id: int, updated_cake: Cake):
    async with app.state.pool.acquire() as connection:
        result = await connection.execute("UPDATE cakes SET name = $1, description = $2, price = $3 WHERE id = $4", updated_cake.name, updated_cake.description, updated_cake.price, id)
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Торт не найден")
        return {"detail": "Торт успешно обновлен"}

@app.delete("/cakes/{id}")
async def delete_cake(id: int):
    async with app.state.pool.acquire() as connection:
        result = await connection.execute("DELETE FROM cakes WHERE id = $1", id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Торт не найден")
        return {"detail": "Торт успешно удален"}

@app.get("/services/")
async def read_services():
    async with app.state.pool.acquire() as connection:
        services = await connection.fetch("SELECT * FROM services")
        return [{"id": service["id"], "name": service["name"], "description": service["description"]} for service in services]

@app.get("/services/{id}")
async def read_service(id: int):
    async with app.state.pool.acquire() as connection:
        service = await connection.fetchrow("SELECT * FROM services WHERE id = $1", id)
        if service:
            return {"id": service["id"], "name": service["name"], "description": service["description"]}
        raise HTTPException(status_code=404, detail="Услуга не найдена")

@app.post("/services/")
async def create_service(service: Service):
    async with app.state.pool.acquire() as connection:
        await connection.execute("INSERT INTO services (name, description) VALUES ($1, $2)", service.name, service.description)
        return {"detail": "Услуга успешно добавлена"}

@app.put("/services/{id}")
async def update_service(id: int, updated_service: Service):
    async with app.state.pool.acquire() as connection:
        result = await connection.execute("UPDATE services SET name = $1, description = $2 WHERE id = $3", updated_service.name, updated_service.description, id)
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Услуга не найдена")
        return {"detail": "Услуга успешно обновлена"}

@app.delete("/services/{id}")
async def delete_service(id: int):
    async with app.state.pool.acquire() as connection:
        result = await connection.execute("DELETE FROM services WHERE id = $1", id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Услуга не найдена")
        return {"detail": "Услуга успешно удалена"}

@app.get("/contact/")
def read_contact():
    return {
        "address": "ул. Университетская 31, г. Сургут",
        "phone": "+7 (954) 356-5555",
        "email": "bestcake222@gmail.com"
    }

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)