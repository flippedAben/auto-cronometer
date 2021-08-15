import auto_cronometer.gwt_parser as gwt_parser
from pathlib import Path

CUR_PATH = Path(__file__).parent.absolute()

def test_parse_recipe_list():
    with open(CUR_PATH / 'raw_response_strings/recipe_list.txt', 'r') as f:
        response = f.read()
    resp_dict = gwt_parser.parse_recipe_list(response)
    assert resp_dict["Bean chili"] == 13456807
    assert resp_dict["Chicken adobo"] == 14718405
    assert resp_dict["Fruits"] == 13455864
    assert resp_dict["Trail mix"] == 16549828
    assert resp_dict["Eggs with spinach"] == 13455692
    assert resp_dict["Galbitang"] == 15410888


def test_parse_recipe():
    with open(CUR_PATH / 'raw_response_strings/single_recipe.txt', 'r') as f:
        response = f.read()
    resp_dict = gwt_parser.parse_recipe(response)
    assert resp_dict['name'] == 'Greek yogurt with honey'
    assert resp_dict['ingredients'] == [
        {
            'id': 450087,
            'grams': 47.249890044000004,
        },
        {
            'id': 450871,
            'grams': 35.313193305000006,
        },
        {
            'id': 458238,
            'grams': 907.1847392,
        },
    ]

def test_parse_food():
    with open(CUR_PATH / 'raw_response_strings/food.txt', 'r') as f:
        response = f.read()
    resp_dict = gwt_parser.parse_food(response)
    assert resp_dict['name'] == "Olive Oil"
    assert resp_dict['grams_per_unit'] == {
        'cup': 215.9994375,
        'oz': 28.3495231,
        'tbsp': 13.499968584000001,
        'tsp': 4.499984541000001,
    }

def test_parse_food_sweet_potato_raw():
    # Take into account bar codes and other elements in the response.
    with open(CUR_PATH / 'raw_response_strings/food_sweet_potato_raw.txt', 'r') as f:
        response = f.read()
    resp_dict = gwt_parser.parse_food(response)
    assert resp_dict['name'] == "Sweet Potato, Raw"
    assert resp_dict['grams_per_unit']['cup'] == 267.36806249999995
    assert resp_dict['grams_per_unit']['large'] == 204
    assert resp_dict['grams_per_unit']['oz'] == 28.3495231
