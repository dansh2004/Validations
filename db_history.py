from typing import Annotated
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from sqlalchemy import String, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from fastapi import Depends

engine = create_async_engine('sqlite+aiosqlite:///history.db')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


class StatusEnum(str, Enum):
    CORRECT = "Верный ввод"
    ERROR = "Ошибка"

class ValidationEnum(str, Enum):
    Telephon_numbers = "Номер телефона"
    INN = "ИНН"
    SNILS = "СНИЛС"
    OMS = "Полис ОМС"
    Car_numbers = "Номер автомобиля"
    Mail_addresses = "Адрес электронной почты"


class AddHistory(BaseModel):
    validation_type: ValidationEnum
    input_text: str
    status: StatusEnum

class Istoriya(DeclarativeBase):
    pass


class History(Istoriya):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    validation_type: Mapped[ValidationEnum] = mapped_column(String(50))
    input_text: Mapped[str] = mapped_column(String(500))
    status: Mapped[StatusEnum] = mapped_column(String(50))
    time: Mapped[str] = mapped_column(String(20), default=lambda: datetime.now().strftime("%d-%m-%Y %H:%M"))
