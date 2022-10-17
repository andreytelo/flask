from __future__ import annotations

from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy import Column, Integer, String, DateTime, func, create_engine, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker
import atexit
import pydantic
from typing import Optional

app = Flask('server')

DSN = 'postgresql://flask:1234@127.0.0.1:5431/netology'
engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class HttpError(Exception):
    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HttpError)
def http_error_handler(err: HttpError):
    response = jsonify({
        'status': 'error',
        'message': err.message
    })
    response.status_code = err.status_code
    return response


def on_exit():
    engine.dispose()


atexit.register(on_exit)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(60), unique=True, nullable=False)
    password = Column(String, nullable=False)
    advertisements = relationship('Advertisement', back_populates='user')


class Advertisement(Base):
    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)


Base.metadata.create_all(engine)


class CreateUserSchema(pydantic.BaseModel):
    username: str
    password: str


class PatchUserSchema(pydantic.BaseModel):
    username: Optional[str]
    password: Optional[str]


class CreateAdvertisementSchema(pydantic.BaseModel):
    title: str
    description: str
    user_id: int


class PatchAdvertisementSchema(pydantic.BaseModel):
    title: Optional[str]
    description: Optional[str]


def validate(Schema, data: dict):
    try:
        data_validated = Schema(**data).dict(exclude_none=True)
    except pydantic.ValidationError as er:
        raise HttpError(400, er.errors())
    return data_validated


def get_user(user_id: int, session: Session) -> User:
    user = session.query(User).get(user_id)
    if user is None:
        raise HttpError(400, 'user_not_found')
    return user


def get_advertisement(advertisement_id: int, session: Session) -> Advertisement:
    advertisement = session.query(Advertisement).get(advertisement_id)
    if advertisement is None:
        raise HttpError(400, 'advertisement_not_found')
    return advertisement


class UserView(MethodView):

    def get(self, user_id: int):
        with Session() as session:
            user = get_user(user_id, session)
            return jsonify({'id_user': user.id, 'username': user.username})

    def post(self):
        json_data_validated = validate(CreateUserSchema, request.json)

        with Session() as session:
            new_user = User(**json_data_validated)
            try:
                session.add(new_user)
                session.commit()
            except IntegrityError:
                raise HttpError(400, 'user_already_exists')

            return jsonify({'status': 'success', 'id': new_user.id})

    def patch(self, user_id: int):
        json_data_validated = validate(PatchUserSchema, request.json)
        with Session() as session:
            user = get_user(user_id, session)
            for k, v in json_data_validated.items():
                setattr(user, k, v)
            session.add(user)
            session.commit()
        return jsonify({'status': 'success'})

    def delete(self, user_id: int):
        with Session() as session:
            user = get_user(user_id, session)
            session.delete(user)
            session.commit()
        return jsonify({'status': 'success'})


class AdvertisementView(MethodView):

    def get(self, advertisement_id):
        with Session() as session:
            advertisement = get_advertisement(advertisement_id, session)
        return jsonify({'title': advertisement.title, 'description': advertisement.description,
                        'date': advertisement.creation_time.isoformat(), 'user_id': advertisement.user_id})

    def post(self):
        json_data_validated = validate(CreateAdvertisementSchema, request.json)

        with Session() as session:
            new_advertisement = Advertisement(**json_data_validated)
            session.add(new_advertisement)
            session.commit()

            return jsonify({'status': 'success', 'id_adv': new_advertisement.id, 'user_id': new_advertisement.user_id})

    def patch(self, advertisement_id: int):
        json_data_validated = validate(PatchAdvertisementSchema, request.json)

        with Session() as session:
            advertisement = get_advertisement(advertisement_id, session)
            for k, v in json_data_validated.items():
                setattr(advertisement, k, v)
            session.add(advertisement)
            session.commit()

        return jsonify({'status': 'success'})

    def delete(self, advertisement_id: int):
        with Session() as session:
            advertisement = get_advertisement(advertisement_id, session)
            session.delete(advertisement)
            session.commit()

        return jsonify({'status': 'success'})


app.add_url_rule('/user/', methods=['POST'], view_func=UserView.as_view('create_user'))
app.add_url_rule('/user/<int:user_id>', methods=['GET', 'PATCH', 'DELETE'], view_func=UserView.as_view('get_user'))
app.add_url_rule('/advertisement/', methods=['POST'], view_func=AdvertisementView.as_view('create_advertisement'))
app.add_url_rule('/advertisement/<int:advertisement_id>', methods=['GET', 'PATCH', 'DELETE'],
                 view_func=AdvertisementView.as_view('get_advertisement'))
app.run()
