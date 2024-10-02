from pydantic import BaseModel


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str | None
    stock: int
    category_id: int | None


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class CreateReview(BaseModel):
    comment: str
    grade: float
    product_id: int
