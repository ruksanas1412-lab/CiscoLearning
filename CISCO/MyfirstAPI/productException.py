
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    quantity: int

products = []
@app.post("/addProduct", status_code=201)
def addProduct(product: Product):
    for p in products:
        if p.id == product.id:
            raise HTTPException(
                status_code=400,
                detail="Product ID Already Exists"
            )

    products.append(product)
    return {"message": "Product Added Successfully"}


@app.get("/getAllProducts")
def getAllProducts():
    if len(products) == 0:
        raise HTTPException(
            status_code=404,
            detail="No Products Available"
        )
    return products


@app.get("/productByID/{id}")
def getProductByID(id: int):
    for p in products:
        if p.id == id:
            return p

    raise HTTPException(
        status_code=404,
        detail="Product Not Found"
    )


@app.get("/productByName/{name}")
def getProductByName(name: str):
    for p in products:
        if p.name == name:
            return p

    raise HTTPException(
        status_code=404,
        detail="Product Name Not Found"
    )


@app.get("/productByCategory/{category}")
def getProductByCategory(category: str):
    result = []
    for p in products:
        if p.category == category:
            result.append(p)

    if len(result) == 0:
        raise HTTPException(
            status_code=404,
            detail="Category Not Found"
        )
    return result


@app.put("/updateProduct/{id}")
def updateProduct(id: int, product: Product):
    for i in range(len(products)):
        if products[i].id == id:
            if product.id != id:
                raise HTTPException(
                    status_code=400,
                    detail="Product ID Cannot Be Changed"
                )

            products[i] = product

            return {"message": "Product Updated Successfully"}

    raise HTTPException(
        status_code=404,
        detail="Product Not Found"
    )


@app.patch("/updatePrice/{id}")
def updatePrice(id: int, price: float):
    for p in products:
        if p.id == id:
            p.price = price
            return {"message": "Price Updated Successfully"}

    raise HTTPException(
        status_code=404,
        detail="Product Not Found"
    )


@app.delete("/deleteProduct/{id}")
def deleteProduct(id: int):
    for p in products:
        if p.id == id:
            products.remove(p)
            return {"message": "Product Deleted Successfully"}

    raise HTTPException(
        status_code=404,
        detail="Product Not Found"
    )


@app.delete("/deleteAllProducts")
def deleteAllProducts():
    if len(products) == 0:
        raise HTTPException(
            status_code=404,
            detail="No Products Available to Delete"
        )

    products.clear()
    return {"message": "All Products Deleted Successfully"}
