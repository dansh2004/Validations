import uvicorn
from fastapi import FastAPI, Request
from sqlalchemy import select, text
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from db_history import History, SessionDep, engine, Istoriya, AddHistory, ValidationEnum, StatusEnum
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


#Номера телефонов: +7(___)___-__-__
@app.get("/telephon/{number}",
         name="Телефон",
         tags=["Валидаторы"])
async def Telephon_numbers(number: str, session: SessionDep):
    if len(number)==16 and \
        number.startswith("+7(") and \
        number[6]==")" and \
        number[10]==number[13]=="-" and \
        number[3:].replace(")","").replace("-","").isdigit():
            await add_history(AddHistory(
            validation_type=ValidationEnum.Telephon_numbers,
            input_text=number,
            status=StatusEnum.CORRECT
            ), session=session)
            return {"status":True}

    else:
            await add_history(AddHistory(
            validation_type=ValidationEnum.Telephon_numbers,
            input_text=number,
            status=StatusEnum.ERROR
            ), session=session)
            return {"status":False}


#ИНН
@app.get("/INN/{number}",
         name="ИНН",
         tags=["Валидаторы"])
async def INN(number: str, session: SessionDep):
    # Физическое лицо
    if len(number) == 12 and \
            number.isdigit() and \
            (number[0:2] in [str(region).zfill(2) for region in range(1, 88)] or number[0:2] in ["89", "92", "94"]):
        await add_history(AddHistory(
            validation_type=ValidationEnum.INN,
            input_text=number,
            status=StatusEnum.CORRECT
        ), session=session)
        return {"status":True, "type":"Fiz_litso"}
    # Отечественное юидическое лицо
    if len(number) == 10 and \
            number.isdigit() and \
            (number[0:2] in [str(region).zfill(2) for region in range(1, 88)] or number[0:2] in ["89", "92", "94"]):
        await add_history(AddHistory(
            validation_type=ValidationEnum.INN,
            input_text=number,
            status=StatusEnum.CORRECT
        ), session=session)
        return {"status":True, "type":"Ur_ot_litso"}
    # Иностранное юидическое лицо
    if len(number) == 10 and \
            number.isdigit() and \
            number[0:4] == "9909":
        await add_history(AddHistory(
            validation_type=ValidationEnum.INN,
            input_text=number,
            status=StatusEnum.CORRECT
        ), session=session)
        return {"status":True, "type":"Ur_in_litso"}
    # Неверный ввод
    else:
        await add_history(AddHistory(
            validation_type=ValidationEnum.INN,
            input_text=number,
            status=StatusEnum.ERROR
        ), session=session)
        return {"status":False}

#СНИЛС: ___-___-___ __
@app.get("/SNILS/{number}",
         name="СНИЛС",
         tags=["Валидаторы"])
async def SNILS(number: str, session: SessionDep):
    if len(number)==14 and \
        number[3]==number[7]=="-" and \
        number[11]==" " and \
        number.replace(" ", "").replace("-", "").isdigit():
            await add_history(AddHistory(
            validation_type=ValidationEnum.SNILS,
            input_text=number,
            status=StatusEnum.CORRECT
        ), session=session)
            return {"status":True}
    else:
            await add_history(AddHistory(
            validation_type=ValidationEnum.SNILS,
            input_text=number,
            status=StatusEnum.ERROR
        ), session=session)
            return {"status":False}

#Полис OМС
@app.get("/OMS/{number}",
         name="Полис ОМС",
         tags=["Валидаторы"])
async def OMS(number: str, session: SessionDep):
    if len(number)==16 and \
        number.isdigit() and \
        (number[0:2] in [str(region).zfill(2) for region in range(1, 88)] or number[0:2] in ["89", "92", "94"]):
            await add_history(AddHistory(
            validation_type=ValidationEnum.OMS,
            input_text=number,
            status=StatusEnum.CORRECT
            ), session=session)
            return {"status":True}
    else:
            await add_history(AddHistory(
            validation_type=ValidationEnum.OMS,
            input_text=number,
            status=StatusEnum.ERROR
        ), session=session)
            return {"status":False}


#Номера автомобилей (без учёта номера региона): А000АА
@app.get("/car_numbers/{number}",
         name="Номера автомобилей",
         tags=["Валидаторы"])
async def Car_numbers(number: str, session: SessionDep):
    if  len(number) == 6 and \
        number[1:4].isdigit() and \
        number[1:4] != "000" and \
        number[0].lower() in "авекмнорстух" and \
        number[4].lower() in "авекмнорстух" and \
        number[5].lower() in "авекмнорстух":
            await add_history(AddHistory(
            validation_type=ValidationEnum.Car_numbers,
            input_text=number,
            status=StatusEnum.CORRECT
        ), session=session)
            return {"status":True}
    else:
            await add_history(AddHistory(
            validation_type=ValidationEnum.Car_numbers,
            input_text=number,
            status=StatusEnum.ERROR
            ), session=session)
            return {"status":False}

#Адреса электронных почт (Google и Yandex)
@app.get("/mail/{address}",
         name="Адреса электронных почт",
         tags=["Валидаторы"])
async def Mail_addresses(address: str, session: SessionDep):
    #Google почта
    if address.endswith('@gmail.com'):
            await add_history(AddHistory(
            validation_type=ValidationEnum.Mail_addresses,
            input_text=address,
            status=StatusEnum.CORRECT
            ), session=session)
            return {"status":True, "type":"google"}
    #Yandex почта
    if address.endswith('@yandex.ru'):
        await add_history(AddHistory(
            validation_type=ValidationEnum.Mail_addresses,
            input_text=address,
            status=StatusEnum.CORRECT
        ), session=session)
        return {"status":True, "type":"yandex"}
    #Неверный ввод
    else:
        await add_history(AddHistory(
            validation_type=ValidationEnum.Mail_addresses,
            input_text=address,
            status=StatusEnum.ERROR
        ), session=session)
        return {"status":False}

#История
@app.post("/setup_database",
          tags=["История"])
async def setup_database():
    async with engine.begin() as conn:
       await conn.run_sync(Istoriya.metadata.create_all, checkfirst=True)
    return {"ok":True}


@app.post('/history',
          tags=["История"])
async def add_history(data: AddHistory, session: SessionDep):
        await setup_database()
        zapros = History(
        validation_type = data.validation_type,
        input_text = data.input_text,
        status = data.status
        )
        session.add(zapros)
        await session.commit()
        return {"OK": True}

@app.get('/history',
          tags=["История"])
async def get_history(session: SessionDep):
    query = select(History).order_by(History.id.desc())
    result = await session.execute(query)
    return result.scalars().all()

# Удаление одной записи истории
@app.delete('/history/{id}',
          tags=["История"])
async def delete_query(id: int, session: SessionDep):
    stmt = text("DELETE FROM history WHERE id = :id")
    await session.execute(stmt, {"id": id})
    await session.commit()
    return {"status": "Ok"}

# Очистка всей истории
@app.delete('/history',
          tags=["История"])
async def delete_all(session: SessionDep):
    stmt = text("DELETE FROM history")
    await session.execute(stmt)
    await session.commit()
    return {"status": "Ok"}


if __name__=="__main__":
    uvicorn.run(app, port=8000)
