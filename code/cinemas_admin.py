from typing import Callable
import inquirer
import typer
from cinemas_data import InterfaceCinema, Room
from cinemas_user_select_tools import user_all_select_places

app = typer.Typer()


@app.command()
def admin() -> None:
    name_commands: tuple[str, ...] = (
        'Добавить/Удалить объект',
        'Настройки зала(настройка расположения мест, настройка сеансов)',
        'Выйти')

    commands: tuple[Callable[[InterfaceCinema], None]] = [add_or_remove_object, config_room, lambda x: None]
    questions_commands: list[inquirer.List] = [
        inquirer.List(
            'command',
            message='Выберете команду',
            choices=name_commands,
        )
    ]
    interface_cinema = InterfaceCinema()
    commands_function: dict[str, Callable[[InterfaceCinema], None]] = dict(zip(name_commands, commands))
    command: str = ""

    while command != name_commands[-1]:
        command = inquirer.prompt(questions_commands)['command']
        commands_function[command](interface_cinema)


def add_or_remove_object(interface_cinema: InterfaceCinema) -> None:
    actives = ['Добавить', 'Удалить']
    objects = ['Кинотеатр', 'Зал', 'Премьеру', 'Отмена действия']
    questions_config: list[inquirer.List] = [
        inquirer.List(
            'actives',
            message='Выберете действие',
            choices=actives,
        ),
        inquirer.List(
            'objects',
            message='Что вы хотите удалить',
            choices=objects,
        ),
    ]
    config = inquirer.prompt(questions_config)
    function: dict[tuple[str, str], Callable[[InterfaceCinema], None]] = {(actives[0], objects[0]): add_cinema,
                                                                          (actives[1], objects[0]): remove_cinema,
                                                                          (actives[0], objects[1]): add_room,
                                                                          (actives[1], objects[1]): remove_room,
                                                                          (actives[0], objects[2]): add_pattern_premier,
                                                                          (actives[1],
                                                                           objects[2]): remove_pattern_premier
                                                                          }
    function.get((config['actives'], config['objects']), lambda x: None)(interface_cinema)


def add_cinema(interface_cinema: InterfaceCinema) -> None:
    name = ''
    while name in interface_cinema.get_cinemas() or not name:
        questions_commands: list[inquirer.text] = [
            inquirer.Text(
                'name',
                message='Введите название кинотеатра',
            )
        ]
        name = inquirer.prompt(questions_commands)['name'].strip()
        if not name:
            print('Название кинотеатра не может быть пустым')
        if name in interface_cinema.get_cinemas():
            print('Название кинотеатра не могут повторяться')

    interface_cinema.add_cinema(name)
    interface_cinema.save()


def remove_cinema(interface_cinema: InterfaceCinema) -> None:
    if len(interface_cinema.get_cinemas()) == 0:
        print('Кинотеатров нет')
        return
    cinema = user_all_select_places(interface_cinema, final='cinema')
    confirm = False
    if cinema:
        questions_confirm: list[inquirer.text] = [
            inquirer.Confirm(
                'confirm',
                message=f'Вы уверены, что хотите удалить кинотеатр {cinema}, все его залы и премьеры будут удалены',
            )
        ]
        confirm = inquirer.prompt(questions_confirm)['confirm']
    if not confirm:
        print('Действие отменено :(')
        return
    interface_cinema.remove_cinema(cinema)
    interface_cinema.save()


def add_room(interface_cinema: InterfaceCinema) -> None:
    cinema_name: str = user_all_select_places(interface_cinema, final='cinema')
    if not cinema_name:
        print('Действие отменено :(')
        return
    room_size = ''
    count_row = 0
    count_column = 0
    while not count_column or not count_row:
        questions_commands: list[inquirer.text] = [
            inquirer.Text(
                'size',
                message='Введите размер зала в формате: (count column)x(count row), например: 10x10',
            )
        ]
        room_size = inquirer.prompt(questions_commands)['size'].strip()
        if room_size == '':
            print('Действие отменено :(')
            return
        try:
            room_size = room_size.replace('х', 'x')
            count_row = int(room_size.split('x')[0])
            count_column = int(room_size.split('x')[1])
        except:
            print('Неправильный формат ввода размера')
        else:
            if not count_column or not count_row:
                print('Размеры должны быть отличны от 0')

    interface_cinema[cinema_name].append(Room(count_column, count_row))
    interface_cinema.save()


def remove_room(interface_cinema: InterfaceCinema) -> None:
    path = user_all_select_places(interface_cinema, is_premier=False, final='number_room')
    if not path:
        print('Действие отменено :(')
        return
    cinema, number_room = path
    confirm = False

    if cinema:
        massage = f'Вы уверены, что хотите удалить {number_room} зал кинотеатра {cinema},'
        massage += ' все его данные будут потеряны'
        questions_confirm: list[inquirer.text] = [
            inquirer.Confirm(
                'confirm',
                message=massage
            )
        ]
        confirm = inquirer.prompt(questions_confirm)['confirm']
    if not confirm:
        print('Действие отменено :(')
        return
    interface_cinema[cinema].clear(number_room - 1)
    interface_cinema.save()


def add_pattern_premier(interface_cinema: InterfaceCinema) -> None:
    name = ''
    while name in interface_cinema.get_pattern_premier() or not name:
        questions_commands: list[inquirer.text] = [
            inquirer.Text(
                'name',
                message='Введите название премьеры',
            )
        ]
        name = inquirer.prompt(questions_commands)['name'].strip()
        if not name:
            print('Название премьеры не может быть пустым')
        if name in interface_cinema.get_pattern_premier():
            print('Название премьер не могут повторяться')
    questions_commands: list[inquirer.text] = [
        inquirer.Text(
            'info',
            message='Введите описание премьеры',
        )
    ]
    info = inquirer.prompt(questions_commands)['info'].strip()
    interface_cinema.add_pattern_premier(name, info)
    interface_cinema.save()

def remove_pattern_premier(interface_cinema: InterfaceCinema) -> None:
    choice_pattern_premier: list[inquirer.List] = [
        inquirer.List(
            'pattern_premier',
            message='Выберете премьеру',
            choices=interface_cinema.get_pattern_premier() + ['Отмена']
        )
    ]
    pattern_premier: str = inquirer.prompt(choice_pattern_premier)['pattern_premier']
    confirm = False
    if pattern_premier in interface_cinema.get_pattern_premier():
        questions_confirm: list[inquirer.text] = [
            inquirer.Confirm(
                'confirm',
                message=f'Вы уверены, что хотите удалить премьеру {pattern_premier}, все его сеансы будут удалены',
            )
        ]
        confirm = inquirer.prompt(questions_confirm)['confirm']

    if not confirm:
        print('Действие отменено :(')
        return

    interface_cinema.remove_pattern_premier(pattern_premier)
    interface_cinema.save()


def config_room() -> None:
    pass


if __name__ == '__main__':
    app()
