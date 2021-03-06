# -*- coding: utf-8 -*-
from sqlalchemy import create_engine, MetaData, Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.sql.sqltypes import INTEGER, VARCHAR, BOOLEAN
from sqlalchemy.dialects.postgresql.base import ENUM, BYTEA
from sqlalchemy.dialects.postgresql.array import ARRAY

from src import USERS_DB, GIRLS_DB
from src.core.helpers.types import ColumnResultSet


def _get_db_base_data(db):
    meta = MetaData()
    db_url = str(URL(**db))
    engine = create_engine(db_url)
    meta.reflect(bind=engine)
    return meta, engine


meta_user, engine_user = _get_db_base_data(USERS_DB)
BaseUser      = declarative_base()

meta_girl, engine_girl = _get_db_base_data(GIRLS_DB)
BaseGirl      = declarative_base()


META = {
    'user': meta_user,
    'girl': meta_girl,
}

EXCLUDE_BY_DEFAULT = (
    'id',
    'user_id',
    'user_username',
)


def _bool_to_word(val: bool):
    return 'да' if val else 'не важно'


def _get_meta_tables(meta:str):
    meta = META.get(meta)
    if not meta.sorted_tables:
        meta_user.reflect(bind=engine_user)
        meta_girl.reflect(bind=engine_girl)

    return meta.sorted_tables


def _get_column_info(column: Column, table_name: str, meta: str):
    for table in _get_meta_tables(meta):
        if table.name == table_name:
            col = table.columns[column.name]
            return type(col.type), col.nullable


def _get_value_and_type(instance, column: Column, format_value: bool, meta: str):
    """
    :param instance:
    :param column:
    :param format_value:
    :param meta:
    :return: value and type from specific column of instance.
    """
    col_type, nullable = _get_column_info(column, instance.__class__.__table__.name, meta)
    col_val = getattr(instance, column.key)

    if format_value is False:
        return col_type, col_val, nullable

    if col_val is None:
        val = 'не задано'
    elif col_type is INTEGER:
        val = str(col_val)
    elif col_type is VARCHAR or col_type is BYTEA:
        val = col_val
    elif col_type is BOOLEAN:
        val = _bool_to_word(col_val)
    elif col_type is ENUM:
        val = col_val.value
    elif col_type is ARRAY:
        val = '{} - {}'.format(*col_val)
    else:
        raise Exception(f'Invalid column type {col_type}.')

    return col_type, val, nullable


def _create_column_result_set(instance, column: Column, format_value: bool, meta: str):
    col_type, col_val, nullable = _get_value_and_type(instance, column, format_value, meta)
    return ColumnResultSet(
        key=column.key,
        name=column.name,
        value=col_val,
        type=col_type,
        nullable=nullable
    )


def _filter_include_exclude(iter_, inc: tuple, excl: tuple):
    return filter(
        lambda col: col.name in inc if inc else col.name and col.name not in excl,
        iter_
    )


class Common:
    @staticmethod
    def as_dict(instance,
                include_col_names: tuple = None,
                excl_columns_names: tuple = EXCLUDE_BY_DEFAULT,
                only_key_val: bool = False,
                format_value: bool = True):
        if only_key_val:
            return {
                column.key: getattr(instance, column.key)
                for column in _filter_include_exclude(
                    instance.__table__.columns, include_col_names, excl_columns_names
                )
            }

    @staticmethod
    def as_genexpr(instance,
                   include_col_names: tuple = None,
                   exclude_col_names: tuple = EXCLUDE_BY_DEFAULT,
                   format_value: bool = True,
                   meta: str = 'user'):
        return (
            _create_column_result_set(instance, column, format_value, meta)
            for column in _filter_include_exclude(
                instance.__table__.columns, include_col_names, exclude_col_names
            )
        )

    @staticmethod
    def as_tuple(instance,
                 include_col_names: tuple = None,
                 exclude_col_names: tuple = EXCLUDE_BY_DEFAULT,
                 format_value: bool = True,
                 meta: str = 'user'):
        return tuple(Common.as_genexpr(**locals()))

    @staticmethod
    def values_callable(obj):
        return [e.value for e in obj]


class UserBase(BaseUser, Common):
    __abstract__ = True


class GirlBase(BaseGirl, Common):
    __abstract__ = True


UserSession = sessionmaker(bind=engine_user)
user_session = UserSession()

GirlSession = sessionmaker(bind=engine_girl)
girl_session = GirlSession()
