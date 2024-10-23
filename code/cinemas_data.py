import os
from datetime import datetime
import json
from typing import Tuple

DATE_FORMAT = '%d.%m.%Y %H:%M'


class Place:
    def __init__(self, k_price: int = 1, is_lock: bool = False, is_sale: bool = False):
        self.k_price: float = k_price
        self.is_lock: bool = is_lock
        self.is_sale: bool = is_sale

    def __str__(self):
        if self.is_lock:
            return '   '
        elif self.is_sale:
            return '|X|'
        else:
            return '|_|'

    @property
    def is_free(self) -> bool:
        return not (self.is_lock or self.is_sale)

    def get_json(self) -> dict:
        return {'k_price': self.k_price, 'is_lock': self.is_lock}


class Room:
    def __init__(self, count_columns: int, count_rows: int, dict_room=None):
        self._count_rows: int = count_rows
        self._count_columns: int = count_columns
        self._place: list[list[Place, ...], ...]
        self.premiers: dict[str, tuple[str, str, datetime, list[int, int]]]  # name, info, datetime, lock_places

        if dict_room:
            self._place = [[Place(**kwargs) for kwargs in row] for row in dict_room['places']]
            dict_premier = []
            for premier in dict_room.get('premier', []):
                dt = datetime.strptime(premier[2], DATE_FORMAT)
                dict_premier.append((premier[2], (premier[0], premier[1], dt, premier[3])))
            self.premiers = dict(dict_premier)
        else:
            self._place = [[Place() for __ in range(count_columns)] for _ in range(count_rows)]
            self.premiers = {}

    def add_premier(self, name: str, info: str, time: datetime | str) -> None:
        if isinstance(time, str):
            time = datetime.strptime(time, DATE_FORMAT)
        self.premiers[time.strftime(DATE_FORMAT)] = (name, info, time, [])

    @property
    def size(self):
        return self._count_columns, self._count_rows

    def set_select_places(self, active: list[int, int], select: list[tuple[int, int], ...]) -> str:
        places_lines = []
        for row in range(len(self._place)):
            places_line: list[str, ...] = []
            for column in range(len(self._place[row])):
                if column == active[0] and row == active[1]:
                    if (column, row) in select:
                        places_line.append(f'[S]')
                    else:
                        places_line.append(f'[{str(self._place[row][column])[1]}]')
                elif (column, row) in select:
                    places_line.append(f'|S|')
                else:
                    places_line.append(str(self._place[row][column]))

            places_lines.append(' '.join(places_line))
        return '\n'.join(places_lines)

    def __str__(self):
        return '\n'.join([' '.join([str(place) for place in row]) for row in self._place])

    def __getitem__(self, item: tuple[int, int] | slice) -> Place | list[Place, ...]:
        if isinstance(item, slice):
            return self.get_places(item.start, item.stop)
        if isinstance(item, tuple) and len(item) == 2:
            column, row = item
            return self._place[row][column]

    def get_places(self, start_place: tuple[int, int], stop_place: tuple[int, int], is_mode_column: bool = False,
                   filter=lambda place: True) -> list[Place, ...]:
        places = []
        start_column, start_row = start_place or (0, 0)
        step_column, step_row = 1, 1
        stop_column, stop_row = stop_place or (self._count_columns, self._count_rows - 1)
        for row in range(start_row, stop_row + 1, step_row):
            cur_start_column = start_column if is_mode_column or row == start_row else 0
            cur_stop_column = stop_column if is_mode_column or row == stop_row else self._count_columns
            for column in range(cur_start_column, cur_stop_column, step_column):
                if filter(self._place[row][column]):
                    places.append(self._place[row][column])
        return places

    def set_lock(self, start_place: tuple[int, int], stop_place: tuple[int, int], is_lock,
                 is_mode_column: bool = False) -> None:
        for place in self.get_places(start_place, stop_place, is_mode_column):
            place.is_lock = is_lock

    def get_json(self) -> dict:
        list_premier = []
        for premier in self.premiers.values():
            list_premier.append((premier[0], premier[1], premier[2].strftime(DATE_FORMAT), premier[3]))

        data = {'size': (self._count_columns, self._count_rows),
                'places': [[place.get_json() for place in row] for row in self._place],
                'premier': list_premier}

        return data

    def get_premiers(self) -> list[str, ...]:
        list_premiers = []
        for str_datetime, (name, info, datetime, sale_places) in self.premiers.items():
            list_premiers.append(f'{str_datetime} | {name} \t | info ')
        return list_premiers

    def get_room_premiers(self, item: str) -> 'Room':
        premiers_room = Room(self._count_columns, self._count_rows, self.get_json())
        for (column, row) in self.premiers[item][3]:
            premiers_room[(column, row)].is_sale = True
        return premiers_room

    def add_place_sale_premier(self, key_premiers: str, places: list[tuple[int, int], ...]) -> None:
        self.premiers[key_premiers][3].extend(places)


class Cinema:
    def __init__(self, name: str):
        self.name: str = name
        self._rooms: list[Room, ...] = []

    def get_json(self) -> dict:
        data = {'name': self.name,
                'rooms': [room.get_json() for room in self._rooms]}
        return data

    def set_json(self, data: dict) -> None:
        json_room: dict
        for json_room in data['rooms']:
            count_column, count_row = json_room['size']
            self.append(Room(count_column, count_row, dict_room=json_room))

    def __getitem__(self, item: int) -> Room:
        return self._rooms[item]

    def append(self, room: Room) -> None:
        self._rooms.append(room)

    def __repr__(self) -> str:
        return f'Cinema(\'{self.name}\')'

    def clear(self, index) -> None:
        self._rooms.pop(index)

    def get_rooms(self) -> list[str, ...]:
        return [f'{i + 1} зал' for i in range(len(self._rooms))]

    def get_premiers(self) -> list[str, ...]:
        list_premier = []
        for i in range(len(self._rooms)):
            list_premier += [(premier + f' | {i + 1} зал') for premier in self._rooms[i].get_premiers()]
        return list_premier


'''
        self._cursor_place: tuple[int, int] | None = None
        self._action_cinema: Cinema | None = None
        self._action_room: Room | None = None
        self._action_places: list[Place, ...] | None = None
'''


class InterfaceCinema:
    PATH = 'cinemas.json'

    def __init__(self, is_read_file: bool = True):
        self._cinemas: [Cinema, ...] = []
        if is_read_file:
            self._set_json()

    @property
    def cinemas(self) -> dict[str, Cinema]:
        return dict([(cinema.name, cinema) for cinema in self._cinemas])

    def save(self) -> None:
        self._get_json()

    def append(self, cinema: Cinema) -> None:
        self._cinemas.append(cinema)
        self._get_json()

    def _set_json(self) -> None:
        if not os.path.isfile(self.PATH):
            return

        with open(self.PATH, "r") as read_file:
            data = json.load(read_file)

        for json_cinema in data['cinemas']:
            cinema: Cinema = Cinema(json_cinema['name'])
            cinema.set_json(json_cinema)
            self._cinemas.append(cinema)

        # self._cursor_place = data['cursor_place']
        # self._action_room = data['action_room']
        # self._action_places = data['action_places']

    def _get_json(self) -> None:
        data = {'cinemas': []}
        for cinema in self._cinemas:
            data['cinemas'].append(cinema.get_json())

        with open(self.PATH, "w") as write_file:
            json.dump(data, write_file)

    def __getitem__(self, item: str) -> Cinema:
        return self.cinemas[item]

    def get_cinemas(self) -> list[str, ...]:
        return [cinema.name for cinema in self._cinemas]

    def get_rooms(self, cinema: str) -> list[str, ...]:
        return self.cinemas[cinema].get_rooms()

    def add_cinema(self, name: str) -> None:
        self._cinemas.append(Cinema(name))
        self.save()

    def remove_cinema(self, name: str) -> None:
        if name in self.cinemas:
            self._cinemas.remove(self.cinemas[name])
        self.save()

if __name__ == '__main__':
    interface_cinema = InterfaceCinema()
    interface_cinema.save()
