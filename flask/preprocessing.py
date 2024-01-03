from dotenv.main import load_dotenv
import os


load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def convert_data(data: list) -> list[dict]:
    """
    Convert a list of dictionaries into a list of merged dictionaries.

    Args:
        data (list): A list of dictionaries to be converted.

    Returns:
        list[dict]: A list of merged dictionaries.

    Used to combine and convert chat history into appropriate format for langchain.

    Example:

    data = [
    {'output': 'Hello!'},
    {'input': 'Hi there!'},
    {'input': 'How are you?'},
    {"input": "Are you good?"},
    {"output": "I'm fine thanks"},
    {"input": "That's great to hear"},
    {"output": "Did you hear?"},
            ]


    Into:
    [{'input': 'Hi there!\n How are you?\n Are you good?', 'output': 'Hello!'}, {'input': "That's great to hear", 'output': "I'm fine thanks"}]
    """
    if len(data) == 0:
        return []

    merged_data = []
    current_dict = {}

    for item in data:
        key_type = list(item.keys())[0]
        if key_type in current_dict:
            current_dict[key_type] += "\n" + item[key_type]
        else:
            if current_dict:
                merged_data.append(current_dict)
            current_dict = item

    if current_dict:
        merged_data.append(current_dict)

    new = []
    for i in range(0, len(merged_data) - 1, 2):
        new_dict = {
            "input": "",
            "output": "",
            **merged_data[i],
            **merged_data[i + 1],
        }
        new.append(new_dict)

    return new
