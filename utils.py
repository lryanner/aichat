import json
import logging
import random
import winsound

import pandas

import numpy as np


def load_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def load_json_string(json_string):
    return json.loads(json_string)

def save_json(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_json_string(data):
    return json.dumps(data, ensure_ascii=False, indent=4)

def has_same_item(list1, list2):
    for item in list1:
        if item in list2:
            return True
    return False

def shuffle_list(list_):
    random.shuffle(list_)
    return list_

def copy_file(src, dst):
    import shutil
    shutil.copy(src, dst)

def warn(warning):
    logging.warning(warning)

def info(info_):
    logging.info(info_)

def load_csv(file_name):
    return pandas.read_csv(file_name).to_dict(orient='records')

def save_csv(file_name, data):
    pandas.DataFrame(data).to_csv(file_name, index=False)

def get_similar_array_index(array, target):
    if not isinstance(array, np.ndarray):
        array = np.array(array)
    if not isinstance(target, np.ndarray):
        target = np.array(target)
    target = np.array(target)
    result = np.linalg.norm(array - target, axis=1)
    result = np.argmin(result)
    return result

def get_similar_array(array, target):
    if not isinstance(array, np.ndarray):
        array = np.array(array)
    if not isinstance(target, np.ndarray):
        target = np.array(target)
    target = np.array(target)
    result = np.linalg.norm(array - target, axis=1)
    result = np.argmin(result)
    return target[result]

def play_sound(file_name):
    winsound.PlaySound(file_name, winsound.SND_FILENAME)

def rename_file(origin_file_name_with_path, file_name):
    """
    Rename the file.
    :param origin_file_name_with_path: origin file name with path
    :param file_name: file name without path
    :return:
    """
    import os
    # get the original file path
    file_path = os.path.dirname(origin_file_name_with_path)
    target_file_name_with_path = os.path.join(file_path, file_name)
    os.rename(origin_file_name_with_path, target_file_name_with_path)
