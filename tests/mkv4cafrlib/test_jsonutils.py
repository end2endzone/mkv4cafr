import pytest
import os
from mkv4cafrlib import jsonutils

def test_dump_details():
    # arrange
    person: dict
    person = dict()

    person['name'] = "Luke Skywalker"
    person['age'] = 23
    person['force-user'] = True
    person['height'] = 1.75
    person['friends'] = list()
    person['friends'].append('Leia Organa')
    person['friends'].append('Han Solo')
    person['friends'].append('Chewbacca')
    person['friends'].append('Yoda')
    person['friends'].append('Obi-Wan Kenobi')
    person['friends'].append('R2-D2')
    person['light-sabers'] = dict()
    person['light-sabers']['red'] = False
    person['light-sabers']['green'] = True
    person['light-sabers']['blue'] = False
    person['light-sabers']['white'] = False
    person['light-sabers']['black'] = False
    person['light-sabers']['yellow'] = False
    person['light-sabers']['purple'] = False

    actual_json_str = jsonutils.dump_details(person)
    assert actual_json_str != None and len(actual_json_str) > 0

    expected_json_str = '''name: 'Luke Skywalker'
age: 23
force-user: true
height: 1.75
friends[0]: 'Leia Organa'
friends[1]: 'Han Solo'
friends[2]: 'Chewbacca'
friends[3]: 'Yoda'
friends[4]: 'Obi-Wan Kenobi'
friends[5]: 'R2-D2'
light-sabers.red: false
light-sabers.green: true
light-sabers.blue: false
light-sabers.white: false
light-sabers.black: false
light-sabers.yellow: false
light-sabers.purple: false'''

    assert expected_json_str == actual_json_str


class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age


def test_dump_details_unknown_types():
    # arrange
    person: dict
    person = dict()

    person['key'] = Person("Luke Skywalker", 23)

    # assert an exception is thrown
    with pytest.raises(Exception) as e_info:
        actual_json_str = jsonutils.dump_details(person)
