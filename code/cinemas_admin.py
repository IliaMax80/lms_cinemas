from typing import Callable

import inquirer
import typer
from cinemas_data import InterfaceCinema
from cinemas_user_select_tools import user_all_select_places

app = typer.Typer()


@app.command()
def admin() -> None:
    name_commands: tuple[str, ...] = (
        'Добавить/Удалить объект', 'Задать конфигурацию зала', 'Выйти')

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
    objects = ['Кинотеатр', 'Зал', 'Сеанс']
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
                                                                          (actives[1], objects[0]): remove_cinema
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
        name = inquirer.prompt(questions_commands)['name']
        if not name:
            print('Название кинотеатра не может быть пустым')
        if name in interface_cinema.get_cinemas():
            print('Название кинотеатра не могут повторяться')

    interface_cinema.add_cinema(name)


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


def add_room(interface_cinema: InterfaceCinema) -> None:
    name = ''
    while name in interface_cinema.get_cinemas() or not name:
        questions_commands: list[inquirer.text] = [
            inquirer.Text(
                'name',
                message='Введите название кинотеатра',
            )
        ]
        name = inquirer.prompt(questions_commands)['name']
        if not name:
            print('Название кинотеатра не может быть пустым')
        if name in interface_cinema.get_cinemas():
            print('Название кинотеатра не могут повторяться')

    interface_cinema.add_cinema(name)


def add_premier() -> None:
    pass


def config_room() -> None:
    pass


if __name__ == '__main__':
    app()
