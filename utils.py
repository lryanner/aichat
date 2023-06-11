import hashlib
import json
import logging
import random
from datetime import datetime

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

def get_same_item(list1, list2):
    result = []
    for item in list1:
        if item in list2:
            result.append(item)
    return result

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

def has_file(file_path):
    import os
    return os.path.exists(file_path)

def get_random_salt():
    return str(random.randint(32768, 65536))

def get_md5_sign(text):
    return hashlib.md5(text).hexdigest()

def get_sha256_sign(text):
    return hashlib.sha256(text).hexdigest()

def get_time_stamp():
    return str(int(datetime.now().timestamp()))

def remove_brackets_content(text):
    """
    Remove the content in brackets. Both Chinese and English brackets are supported.
    :param text: the text to be processed.
    :return:
    """
    import re
    text = re.sub(r'（.*?）', '', text)
    return re.sub(r'\(.*?\)', '', text)

def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')