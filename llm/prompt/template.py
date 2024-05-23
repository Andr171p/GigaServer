import os
from utils.preprocessing_data import txt_to_str


def join_prompt(system_path, user_directory_path):
    directory = user_directory_path
    prompts = {}
    system_prompt = txt_to_str(
        file_path=system_path
    )
    for filename in os.listdir(directory):
        name = filename.split(".")[0]
        prompt = (f"{system_prompt}\n"
                  f"{txt_to_str(os.path.join(directory, filename))}")
        prompts[name] = prompt

    return prompts

