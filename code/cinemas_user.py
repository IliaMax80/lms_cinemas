import sys

import typer
import inquirer
import keyboard
from cinemas_data import InterfaceCinema, Cinema, Room, Place
from typing import Callable

from cinemas_user_select_tools import user_all_select_places

app = typer.Typer()


@app.command()
def user() -> None:
    name_commands: tuple[str, ...] = ('Купить билеты', 'Выйти')
    commands: tuple[Callable[[InterfaceCinema], None]] = [bay, lambda x: None]

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


def bay(interface_cinema: InterfaceCinema) -> None:
    data = user_all_select_places(interface_cinema)
    if not data: return
    cinema, number_room, premier, places = data
    interface_cinema[cinema][number_room - 1].add_place_sale_premier(premier, places)
    interface_cinema.save()


if __name__ == '__main__':
    app()
