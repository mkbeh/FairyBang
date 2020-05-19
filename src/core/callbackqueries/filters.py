# -*- coding: utf-8 -*-
import itertools

from src.models import session, FILTERS
from src.core.utils import pyutils
from src.core.callbackqueries.base import BaseCBQ


filters_state = {}


class FiltersCBQ(BaseCBQ):
    __slots__ = ('_query_name', '_username', '_chat_id', '_increment')

    _chunk_size = 7

    def __init__(self, query_name, username, chat_id, increment=0):
        self._query_name     = query_name
        self._username       = username
        self._chat_id        = chat_id
        self._increment      = increment

        self._state          = None
        self._add_move       = True

    @staticmethod
    def get_max_size_name_of_all_options(all_options):
        return len(
            max(
                (map(lambda x: ''.join(x[1:]), all_options))
            )
        )

    def get_option_name_with_indent(self, all_options, name_data):
        max_str_size = self.get_max_size_name_of_all_options(all_options)
        str_size = len(''.join(name_data))
        whs_num = 1 if max_str_size - str_size == 0 else max_str_size - str_size
        whs = ' ' * int(whs_num * 2.3777 + 35)
        option_name = whs.join(name_data)
        return option_name

    def get_girls_options(self):
        filter_ = FILTERS.get(self._query_name)
        return filter_.as_tuple(
            session.query(filter_).filter(filter_.user_username == self._username).one()
        )

    def get_chunk_girls_options(self):
        girls_options = self.get_girls_options()
        return pyutils.chunk_list(girls_options, self._chunk_size)

    def get_part_from_chunk_girls_options(self):
        chunk_girls_options = self.get_chunk_girls_options()
        state = filters_state.get(self._chat_id, 0) + self._increment
        if state == len(chunk_girls_options):
            state = 0

        if len(chunk_girls_options) == 1:
            self._add_move = False

        filters_state[self._chat_id] = self._state = state
        return chunk_girls_options[state]

    def get_options_objects(self):
        part_girls_options = self.get_part_from_chunk_girls_options()
        return (
            self.Option(name=self.get_option_name_with_indent(part_girls_options, data), callback=key)
            for key, *data in part_girls_options
        )

    def add_move_options(self):
        options_objects = self.get_options_objects()

        if not self._add_move:
            return options_objects

        if self._state == 0:
            move_options = (self.move_options_data[1], )
        else:
            move_options = self.move_options_data

        move_options = (self.Option(name, callback) for name, callback in move_options)
        return itertools.chain(options_objects, move_options)

    def get_keyboard_options(self):
        return self.add_move_options()