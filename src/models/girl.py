# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship

from src.models.common import GirlBase
from src.models.mixins import BaseFilterMixin, ExtFilterMixin, ServicesMixin


csc = 'all,delete,delete-orphan'


class GirlServices(ServicesMixin, GirlBase):
    __tablename__ = 'girl_services'

    #       --- relationship ---
    girl_id         = Column(Integer, ForeignKey('girls.id', ondelete='CASCADE'))
    girl            = relationship('Girl', back_populates='services')


class GirlExtFilter(ExtFilterMixin, GirlBase):
    __tablename__ = 'girl_ext_filter'

    #       --- prices ---
    app_one_hour            = Column(Integer, nullable=False, name='Апартаменты 1 час', key='app_one_hour')
    app_two_hours           = Column(Integer, name='Апартаменты 2 часа', key='app_two_hours')
    departure_to_you        = Column(Integer, nullable=False, name='Выезд к Вам', key='departure_to_you')
    departure_to_you_night  = Column(Integer, nullable=False, name='Выезд к Вам на ночь', key='departure_to_you_night')

    #       --- relationship ---
    girl_id         = Column(Integer, ForeignKey('girls.id', ondelete='CASCADE'))
    girl            = relationship('Girl', back_populates='ext_filter')


class GirlBaseFilter(BaseFilterMixin, GirlBase):
    __tablename__ = 'girl_base_filter'

    #       --- appearance details ---
    age             = Column(Integer, name='Возраст', nullable=False, key='age')
    height          = Column(Integer, name='Рост', key='height')
    chest           = Column(Integer, name='Грудь', key='chest')

    #       --- price ---
    price           = Column(Integer, name='Цена', nullable=False, key='price')

    #       --- relationship ---
    girl_id         = Column(Integer, ForeignKey('girls.id', ondelete='CASCADE'))
    girl            = relationship('Girl', back_populates='base_filter')


class Girl(GirlBase):
    __tablename__ = 'girls'

    id              = Column(Integer, primary_key=True)

    #       --- main ---
    name            = Column(String(50), name='Имя', nullable=False, key='name')
    about           = Column(String(500), name='О себе', nullable=True, key='about')

    #       --- photo ---
    preview_photo   = Column(LargeBinary, nullable=False)
    photo1          = Column(LargeBinary, nullable=True)
    photo2          = Column(LargeBinary, nullable=True)
    photo3          = Column(LargeBinary, nullable=True)

    #       --- contacts ---
    phone           = Column(String(30), nullable=False)
    viber           = Column(String(30), nullable=True)
    whatsapp        = Column(String(30), nullable=True)
    telegram        = Column(String(30), nullable=True)

    base_filter     = relationship('GirlBaseFilter', uselist=False, back_populates='girl', cascade=csc)
    ext_filter      = relationship('GirlExtFilter', uselist=False, back_populates='girl', cascade=csc)
    services        = relationship('GirlServices', uselist=False, back_populates='girl', cascade=csc)
