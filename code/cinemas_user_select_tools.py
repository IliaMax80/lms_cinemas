import sys

import typer
import inquirer
import keyboard
from cinemas_data import InterfaceCinema, Cinema, Room, Place


def user_set_cinema(interface_cinema: InterfaceCinema) -> str:
    choice_cinema: list[inquirer.List] = [
        inquirer.List(
            'cinema',
            message='Выберете кинотеатр',
            choices=interface_cinema.get_cinemas() + ['Выйти']
        )
    ]
    choice = inquirer.prompt(choice_cinema)['cinema']
    return choice


def user_set_room(interface_cinema: InterfaceCinema, cinema: str) -> str:
    choice_room: list[inquirer.List] = [
        inquirer.List(
            'room',
            message='Выберете зал',
            choices=interface_cinema.get_rooms(cinema) + ['Выйти']
        )
    ]
    choice = inquirer.prompt(choice_room)['room']
    return choice


def user_set_premier(interface_cinema: InterfaceCinema, cinema: str) -> str:
    choice_room: list[inquirer.List] = [
        inquirer.List(
            'premier',
            message='Выберете сеанс',
            choices=interface_cinema[cinema].get_premiers() + ['Выйти']
        )
    ]
    choice = inquirer.prompt(choice_room)['premier']
    return choice


def user_set_places(room: Room) -> Room | None:
    print('Используйте стрелки для перемещения')
    print('Для выбора нажмите space')
    print('После нажмите enter, что бы потвердить свой выбор')
    print('При нажатие X вы выйдите из текущего пункта, весь выбор будет удален')

    active_places: list[int, int] = [0, 0]
    places: list[tuple[int, int]] = []
    is_conform: bool = False
    is_exit: bool = False

    def move(step_x: int, step_y: int):
        nonlocal active_places
        count_columns, count_rows = room.size
        active_places[0] = (active_places[0] + step_x) % count_columns
        active_places[1] = (active_places[1] + step_y) % count_rows

    def select():
        nonlocal active_places
        if room[(active_places[0], active_places[1])].is_free:
            if tuple(active_places) in places:
                places.remove(tuple(active_places.copy()))
            else:
                places.append(tuple(active_places.copy()))

    def confirm():
        nonlocal is_conform
        is_conform = True

    def exit():
        nonlocal is_exit
        is_exit = True

    while (not is_conform) and (not is_exit):
        keyboard.on_press_key('right', lambda x: move(1, 0), suppress=True)
        keyboard.on_press_key('left', lambda x: move(-1, 0), suppress=True)
        keyboard.on_press_key('up', lambda x: move(0, -1), suppress=True)
        keyboard.on_press_key('down', lambda x: move(0, 1), suppress=True)
        keyboard.on_press_key('enter', lambda x: confirm(), suppress=True)
        keyboard.on_press_key('space', lambda x: select(), suppress=True)
        keyboard.on_press_key('x', lambda x: exit(), suppress=True)
        print(room.set_select_places(active_places, places))
        keyboard.read_event()
        sys.stdin.flush()
        if (not is_conform) and (not is_exit):
            for _ in range(room.size[1]):
                sys.stdout.write('\x1b[1A')
                sys.stdout.write('\x1b[2K')

    keyboard.unhook_all()

    if is_exit:
        return
    return places



def user_all_select_places(interface_cinema: InterfaceCinema, is_premier: bool = True, final: str = 'place', **kwarg) \
        -> tuple[str, int, list[tuple[int, int], ...]] | tuple[...] | None:
    cinema: str | None = kwarg.get('cinema', None)
    number_room: int | None = kwarg.get('number_room', None)
    premier: str | None = kwarg.get('premier', None)
    places: list[tuple[int, int], ...] = kwarg.get('places', None)
    is_confirm: bool = False

    while not (cinema and number_room and is_confirm):
        if not cinema:
            choice = user_set_cinema(interface_cinema)
            if choice in interface_cinema.cinemas:
                cinema = choice
                if final == 'cinema':
                    return cinema
            else:
                return

        elif not number_room and not is_premier:
            choice = user_set_room(interface_cinema, cinema)
            if choice in interface_cinema.get_rooms(cinema):
                number_room = int(choice[:-3])
                if final == 'number_room':
                    return cinema, number_room
            else:
                cinema = None

        elif not is_confirm and is_premier and not premier:
            choice = user_set_premier(interface_cinema, cinema)
            if choice in interface_cinema[cinema].get_premiers():
                premier = choice[:16]
                number_room = int(choice.split()[-2])
                if final == 'premier':
                    return cinema, number_room, premier
            else:
                cinema = None

        elif not is_confirm:
            if is_premier:
                room = interface_cinema[cinema][number_room - 1].get_room_premiers(premier)
            else:
                room = None
            places = user_set_places(room)
            if places:
                is_confirm = True
            else:
                premier = None
                number_room = None
            print()
    return cinema, number_room, premier, places
