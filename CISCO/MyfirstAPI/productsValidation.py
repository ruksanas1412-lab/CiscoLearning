
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

app = FastAPI()


# ==========================================
# STEP 1: GLOBAL EXCEPTION HANDLING
# ==========================================

class ProductException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code


@app.exception_handler(ProductException)
async def globalExceptionHandler(request: Request, exc: ProductException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )


# Global Validation Exception Handler
@app.exception_handler(RequestValidationError)
async def validationExceptionHandler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation Failed",
            "errors": [
                {
                    "field": ".".join(str(x) for x in error["loc"]),
                    "message": error["msg"]
                }
                for error in exc.errors()
            ]
        }
    )


# ==========================================
# STEP 2: PRODUCT CLASS WITH VALIDATION
# ==========================================

class Product(BaseModel):
    id: int = Field(gt=0, description="ID must be greater than 0")

    name: str = Field(min_length=3, max_length=30,
                      description="Name must be 3 to 30 characters")

    category: str = Field(min_length=3, max_length=20,
                          description="Category must be 3 to 20 characters")

    price: float = Field(gt=0, description="Price must be greater than 0")

    quantity: int = Field(ge=0, description="Quantity cannot be negative")


class PriceUpdate(BaseModel):
    price: float = Field(gt=0, description="Price must be greater than 0")


# ==========================================
# STEP 3: STORE PRODUCTS IN LIST
# ==========================================

products = []


# API 1: Home
@app.get("/")
def home():
    return {"message": "Welcome to Product Management"}


# API 2: Add Product
@app.post("/addProduct", status_code=201)
def addProduct(product: Product):

    for p in products:
        if p.id == product.id:
            raise ProductException("Product ID Already Exists", 400)

    products.append(product)
    return {"message": "Product Added Successfully"}


# API 3: Get All Products
@app.get("/getAllProducts")
def getAllProducts():

    if len(products) == 0:
        raise ProductException("No Products Available", 404)

    return products


# API 4: Get Product By ID
@app.get("/productByID/{id}")
def getProductByID(id: int):

    for p in products:
        if p.id == id:
            return p

    raise ProductException("Product Not Found", 404)


# API 5: Get Product By Name
@app.get("/productByName/{name}")
def getProductByName(name: str):

    for p in products:
        if p.name.lower() == name.lower():
            return p

    raise ProductException("Product Name Not Found", 404)


# API 6: Get Products By Category
@app.get("/productByCategory/{category}")
def getProductByCategory(category: str):

    result = []

    for p in products:
        if p.category.lower() == category.lower():
            result.append(p)

    if len(result) == 0:
        raise ProductException("Category Not Found", 404)

    return result


# API 7: Update Product
@app.put("/updateProduct/{id}")
def updateProduct(id: int, product: Product):

    for i in range(len(products)):
        if products[i].id == id:

            if product.id != id:
                raise ProductException("Product ID Cannot Be Changed", 400)

            products[i] = product
            return {"message": "Product Updated Successfully"}

    raise ProductException("Product Not Found", 404)


# API 8: Update Product Price
@app.patch("/updatePrice/{id}")
def updatePrice(id: int, data: PriceUpdate):

    for p in products:
        if p.id == id:
            p.price = data.price
            return {"message": "Price Updated Successfully"}

    raise ProductException("Product Not Found", 404)


# API 9: Delete Product
@app.delete("/deleteProduct/{id}")
def deleteProduct(id: int):

    for p in products:
        if p.id == id:
            products.remove(p)
            return {"message": "Product Deleted Successfully"}

    raise ProductException("Product Not Found", 404)


# API 10: Delete All Products
@app.delete("/deleteAllProducts")
def deleteAllProducts():

    if len(products) == 0:
        raise ProductException("No Products Available to Delete", 404)

    products.clear()
    return {"message": "All Products Deleted Successfully"}
