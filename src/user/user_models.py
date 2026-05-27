from sqlalchemy import Column,String,Integer,Boolean
from sqlalchemy.orm import relationship
from src.utils.db import Base

class UserModel(Base):
    __tablename__ = "user"

    id = Column(Integer,primary_key=True)
    username = Column(String(255), nullable = False, unique=True)
    email =  Column(String(255), nullable = False, unique=True)
    password =  Column(String(255), nullable = False)
    is_active = Column(Boolean, default = False)
    is_staff = Column(Boolean, default=False)
    order = relationship('OrderModel', back_populates='user')

    def __repr__(self):
        return f"<Username: {self.username}>"

