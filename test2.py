# В нашей школе мы не можем разглашать персональные данные пользователей,
# но чтобы преподаватель и ученик смогли объяснить нашей поддержке, кого они имеют в виду (у преподавателей,
# например, часто учится несколько Саш), мы генерируем пользователям уникальные и легко произносимые имена.
# Имя у нас состоит из прилагательного, имени животного и двузначной цифры. В итоге получается, например,
# "Перламутровый лосось 77". Для генерации таких имен мы и решали следующую задачу:
# Получить с русской википедии список всех животных (https://inlnk.ru/jElywR) и вывести количество
# животных на каждую букву алфавита. Результат должен получиться в следующем виде:
# А: 642
# Б: 412
# В:....

import json
from urllib import parse

import requests
from bs4 import BeautifulSoup, PageElement, ResultSet

START_URL_MIN = 'https://inlnk.ru/jElywR'
BASE_NEXT_URL = 'https://ru.wikipedia.org/w/index.php?title=%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1' \
                '%8F:%D0%96%D0%B8%D0%B2%D0%BE%D1%82%D0%BD%D1%8B%D0%B5_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%' \
                'B2%D0%B8%D1%82%D1%83&pagefrom='


def url_from_min_url(url_min: str) -> str:
    """Извлекает полную ссылку из сокращенной"""
    resp = requests.head(url_min)
    return resp.headers['location']


def _parse_elements_to_catalog(group: PageElement) -> list[str, list]:
    """Делит список элементов по переносу строки, возвращает список,
    где первый элемент - буква, второй элемент - список названий"""
    list_of_animals = group.text.split('\n')
    letter = list_of_animals[0]
    return [letter if letter != 'A' else '', list_of_animals[1:]]


def _parse_group_on_page_by_url(url: str) -> ResultSet:
    """Находит алфавитные группы на странице"""
    page = BeautifulSoup(markup=requests.get(url).text, features="html.parser")
    alphabet_groups_on_page = page.find(id='mw-pages').find_all(class_='mw-category-group')
    return alphabet_groups_on_page


def dict_counter(all_animals_dict: dict) -> None:
    """Считает количество имен животных по категориям (буквам)"""
    print('\nВсе названия животных (включая 1, 2 и 3-х словные):')
    for key, value in all_animals_dict.items():
        print(f'{key}: {len(value)}')


def write_dict_to_json_files(all_animals_dict: dict) -> None:
    """Записывает словарь животных в файлы [буква].json"""
    for key, value in all_animals_dict.items():
        with open(f'test2files/{key}.json', 'w', encoding='utf-8') as json_file:
            json.dump({key: value}, json_file, ensure_ascii=False, indent=4)


def main_parser(url: str) -> dict[str:[str]]:
    """Бежит по буквенным группам животных на странице,
    последнее животное - начало новой страницы"""
    start_url = url_from_min_url(url_min=url)
    alphabet_groups_on_page = _parse_group_on_page_by_url(url=start_url)
    all_dict, letter, last_item_in_group = {}, 'А', ''
    print('Парсим животных с вики (25 сек. ~ 1 мин.):\n', end='')
    while letter:
        for group in alphabet_groups_on_page:
            letter, list_of_names = _parse_elements_to_catalog(group)
            if not letter:
                break
            last_item_in_group = list_of_names[-1]
            if letter not in all_dict.keys():
                all_dict[letter] = list_of_names
            else:
                all_dict[letter] = list(set(all_dict[letter] + list_of_names))  # тут отсёк дубли
        next_url = BASE_NEXT_URL + parse.quote(last_item_in_group)  # следующая ссылка
        alphabet_groups_on_page = _parse_group_on_page_by_url(url=next_url)
        print('█', end='')
    return all_dict


def main() -> None:
    all_dict = main_parser(url=START_URL_MIN)
    dict_counter(all_dict)
    # нижняя функция необязательная, но я решил что файлы лучше сохранить,
    # чтобы не потребовалось парсить еще раз
    write_dict_to_json_files(all_dict)


if __name__ == '__main__':
    # не самый быстрый вариант парсинга, но как я понял из задания его нужно было сделать один раз
    main()
