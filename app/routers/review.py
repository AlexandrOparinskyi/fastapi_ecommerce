import statistics
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, insert, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models import *
from app.routers.auth import get_current_user
from app.schemas import CreateReview

router = APIRouter(prefix="/review", tags=['review'])


@router.get("/")
async def get_all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    if not reviews.all():
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "transaction": "There are no product"
        }
    return reviews.all()


@router.get("/product")
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)],
                           product_id: int):
    product = await db.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    reviews = await db.scalars(select(Review).where(Review.is_active == True and Review.product_id == product_id))
    if not reviews.all():
        return {
            "status": status.HTTP_404_NOT_FOUND,
            "transaction": "There are no product"
        }
    return reviews.all()


@router.post("/create")
async def add_review(db: Annotated[AsyncSession, Depends(get_db)],
                     create_review: CreateReview,
                     get_user: Annotated[dict, Depends(get_current_user)]):
    if await db.scalar(select(User).where(User.id == get_user.get('id') and User.is_active is True)):
        if not await db.scalar(select(Product).where(Product.id == create_review.product_id)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No product id"
            )
        rating = await db.execute(insert(Rating).values(user_id=get_user.get('id'),
                                                        product_id=create_review.product_id,
                                                        grade=create_review.grade).returning(text('id')))
        await db.execute(insert(Review).values(user_id=get_user.get('id'),
                                               product_id=create_review.product_id,
                                               comment=create_review.comment,
                                               rating_id=rating.scalar()))
        rating_for_product = await db.scalars(select(Rating).where(Rating.product_id == create_review.product_id
                                                                   and Rating.is_active == True))
        await db.execute(update(Product).where(Product.id == create_review.product_id).values(
            rating=statistics.mean([i.grade for i in rating_for_product.all()])
        ))
        await db.commit()
        return {
            "status": status.HTTP_201_CREATED,
            "detail": "Successful"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have admin permission"
        )


@router.delete("/delete")
async def delete_review(db: Annotated[AsyncSession, Depends(get_db)],
                        review_id: int,
                        get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        product_id = await db.scalar(select(Review.product_id).where(Review.id == review_id))
        if not await db.scalar(select(Product).where(Product.id == product_id)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        rating = await db.execute(update(Review).where(Review.id == review_id).values(is_active=False).returning(text('rating_id')))
        await db.execute(update(Rating).where(Rating.id == rating.scalar()).values(is_active=False))
        rating_for_product = await db.scalars(select(Rating).where(Rating.product_id == product_id
                                                                   and Rating.is_active == True))
        await db.execute(update(Product).where(Product.id == product_id).values(
            rating=statistics.mean([i.grade for i in rating_for_product.all()])
        ))
        await db.commit()
        return {
            "status": status.HTTP_200_OK,
            "detail": "Review deleted!"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have admin permission"
        )
