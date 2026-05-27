from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.user.user_schema import UserResponse
from src.order.order_models import OrderModel
from src.user.user_models import UserModel
from src.order.order_schema import OrderSchema, PatchOrder, OrderStatusUpdate

async def place_order(order:OrderSchema, user:UserResponse, db:Session):
    new_order = OrderModel(
        quantity = order.quantity,
        pizza_size = order.pizza_size,
        user_id = user.id
    )
    
    db.add(new_order)       
    db.commit()        
    db.refresh(new_order)  
    
    return new_order


async def get_all_orders(user:UserResponse, db:Session):
    user = db.query(UserModel).filter(UserModel.id == user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= "User not found")
    role = user.is_staff
    if not role:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized to perfrom the action")
    
    orders = db.query(OrderModel).all()

    return orders

async def fetch_user_orders(user_id:int, user:UserResponse, db:Session):
    user = db.query(UserModel).filter(UserModel.id == user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= "User not found")
    role = user.is_staff
    if not role:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized to perfrom the action")
    
    orders = db.query(OrderModel).filter(OrderModel.user_id == user_id).all()

    return orders

async def fetch_specific_user_orders(order_id: int, user:UserResponse, db:Session):
    user = db.query(UserModel).filter(UserModel.id == user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= "User not found")
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != user.id and not user.is_staff:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized to perfrom the action")
    

    return order


async def patch_order(order_id, data:PatchOrder, user:UserResponse, db: Session):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != user.id and not user.is_staff:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized to perfrom the action")
    
    update_data = data.model_dump(exclude_unset=True)

    for key,value in update_data.items():
        setattr(order, key, value)

    db.commit()
    db.refresh(order)

    return order

    
async def patch_order_status(
                             order_id: int,
                             data:OrderStatusUpdate,
                             user: UserResponse,
                             db: Session
):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()

    if not order:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                      detail="Order not found")
        
    if not user.is_staff:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized to perform the action")
    order.order_status = data.order_status
    db.commit()
    db.refresh(order)
    return order


async def remove_order(order_id: int, user:UserResponse, db:Session):
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized to perform the action")
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")
    db.delete(order)
    db.commit()
    return None


