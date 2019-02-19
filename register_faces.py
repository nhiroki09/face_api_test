import argparse
import json
import re
import sys
import time
from pathlib import Path
from uuid import uuid4

import cognitive_face as CF


class CognitiveFace:
    @classmethod
    def initialize(cls):
        config_file = 'config.json'
        with open(config_file) as f:
            config = json.load(f)
            CF.Key.set(config['key'])
            CF.BaseUrl.set(config['url'])

    def __init__(self, person_group_id, person_group_name=None):
        self.person_group_id_ = person_group_id
        self.person_group_name_ = person_group_name
        self.person_id_name_ = {}
        self._create_person_group()

    def _create_person_group(self):
        CF.person_group.create(self.person_group_id_, self.person_group_name_)

    def register_faces(self, dir_path):
        name = Path(dir_path).name
        person_id = CF.person.create(
            self.person_group_id_, name=name)['personId']
        self.person_id_name_[person_id] = name
        results = {}
        regex_pattern = re.compile(r'.*\.jpg', re.IGNORECASE)
        for image_file in [f for f in Path(dir_path).glob('*') if re.match(regex_pattern, f.name)]:
            try:
                print(image_file, self.person_id_name_[person_id])
                result = CF.person.add_face(
                    image_file, self.person_group_id_, person_id)
                results[image_file] = result
            except Exception as ex:
                print(ex)
        return results

    def train(self):
        print('START training')
        CF.person_group.train(self.person_group_id_)

        # wait while a status is notstarted or running.
        status = CF.person_group.get_status(self.person_group_id_)['status']
        while status in ['notstarted', 'running']:
            time.sleep(1)
            status = CF.person_group.get_status(self.person_group_id_)['status']
        if status == 'failed':
            raise Exception
        print('END training')

    def identify(self, image_path):
        detection_results = CF.face.detect(image_path)
        if detection_results:
            face_ids = [result['faceId'] for result in detection_results]
            identify_result = CF.face.identify(face_ids, self.person_group_id_)
            if identify_result:
                return identify_result[0]['candidates'][0]
        return None

    @classmethod
    def delete_all_person_group(self):
        pg_list = CF.person_group.lists()
        for pg in pg_list:
            CF.person_group.delete(pg['personGroupId'])

def main(dir_path, person_group_id=None, person_group_name=None):
    person_group_id = person_group_id or str(uuid4())

    CognitiveFace.initialize()

    cf = CognitiveFace(person_group_id, person_group_name)

    sub_dirs = sorted([d for d in Path(dir_path).glob('*') if d.is_dir()])

    print('START register faces')
    for sub_dir in sub_dirs:
        cf.register_faces(sub_dir)
    print('END register faces')

    cf.train()

    print("check registered faces")
    regex_pattern = re.compile(r'.*\.jpg', re.IGNORECASE)
    for sub_dir in sub_dirs:
        for image_file in [f for f in Path(sub_dir).glob('*') if re.match(regex_pattern, f.name)]:
            result = cf.identify(image_file)
            print(image_file, cf.person_id_name_[result['personId']])

    print(f'person_group_id: {person_group_id}')

if __name__ == '__main__':
    _parser = argparse.ArgumentParser()
    _parser.add_argument('image_dir', help='face image directory path')
    _parser.add_argument('--person_group_id', help='person group id')
    _parser.add_argument('--person_group_name', help='person group name')

    _args = _parser.parse_args()

    _image_dir = _args.image_dir
    _person_group_id = _args.person_group_id
    _person_group_name = _args.person_group_name

    main(_image_dir, person_group_id=_person_group_id, person_group_name=_person_group_name)
