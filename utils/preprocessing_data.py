def txt_to_str(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.readlines()

    return "".join(text)