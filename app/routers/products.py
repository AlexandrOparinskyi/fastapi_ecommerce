from typing import Annotated

from fastapi import APIRouter, Depends, status
from slugify import slugify
from sqlalchemy import select, insert, update
from sqlalchemy.orm import Session

from app.backend.db_depends import get_db
from app.models import *
from app.schemas import CreateProduct

router = APIRouter(prefix='/products', tags=['products'])


@router.get("/")
async def get_all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(Product.is_active == True and Product.stock > 0)).all()
    if not products:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "transaction": "There are no product"
        }
    return products


@router.post("/create")
async def create_product(db: Annotated[Session, Depends(get_db)],
                         create_product: CreateProduct):
    db.execute(insert(Product).values(name=create_product.name,
                                      slug=slugify(create_product.name),
                                      description=create_product.description,
                                      price=create_product.price,
                                      image_url=create_product.image_url,
                                      stock=create_product.stock,
                                      category_id=create_product.category_id))
    db.commit()
    return {
        "status": status.HTTP_201_CREATED,
        "transaction": "Successful"
    }


@router.get("/{category_slug}")
async def get_product_by_category(category_slug: str,
                                  db: Annotated[Session, Depends(get_db)]):
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "transaction": "Category not found"
        }
    subcategories = db.scalars(select(Category).where(Category.parent_id == category.id)).all() + [category]
    products = db.scalars(select(Product).where(Product.category_id.in_(s.id for s in subcategories))).all()
    prods = db.scalars(select(Product)).all()
    print([s.category for s in prods])
    print(subcategories)
    return products


@router.get("/detail/{product_slug}")
async def product_detail(product_slug: str,
                         db: Annotated[Session, Depends(get_db)]):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "transaction": "Product not found"
        }
    return product


@router.put("/detail/{product_slug}")
async def update_product(product_slug: str,
                         db: Annotated[Session, Depends(get_db)],
                         update_product: CreateProduct):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "transaction": "Product not found"
        }
    db.execute(update(Product).where(Product.slug == product_slug).values(
        name=update_product.name,
        slug=slugify(update_product.name),
        description=update_product.description,
        price=update_product.price,
        image_url=update_product.image_url,
        stock=update_product.stock,
        category_id=update_product.category_id
    ))
    db.commit()
    return {
        "status": status.HTTP_200_OK,
        "transaction": "Product update is successful"
    }


@router.delete("/delete/{product_slug}")
async def delete_product(product_slug: str,
                         db: Annotated[Session, Depends(get_db)]):
    product = db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "transaction": "Product not found"
        }
    db.execute(update(Product).where(Product.slug == product_slug).values(
        is_active=False
    ))
    db.commit()
    return {
        "status_code": status.HTTP_200_OK,
        "transaction": "Product delete is successful"
    }
