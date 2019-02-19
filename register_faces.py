import json
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
        for image_file in Path(dir_path).glob('*.jpg'):
            try:
                print(image_file, self.person_id_name_[person_id])
                result = CF.person.add_face(
                    image_file, self.person_group_id_, person_id)
                results[image_file] = result
            except Exception as ex:
                print(ex)
        return results

    def train(self):
        CF.person_group.train(self.person_group_id_)
        # until status become success

        status = CF.person_group.get_status(self.person_group_id_)['status']
        while status in ['notstarted', 'running']:
            time.sleep(1)
            status = CF.person_group.get_status(self.person_group_id_)['status']
        if status == 'failed':
            raise Exception

    def identify(self, image_path):
        detection_results = CF.face.detect(image_path)
        if detection_results:
            face_ids = [result['faceId'] for result in detection_results]
            identify_result = CF.face.identify(face_ids, self.person_group_id_)
            if identify_result:
                return identify_result[0]['candidates'][0]
        return None


def main(argv):
    dir_path = sys.argv[1]
    CognitiveFace.initialize()

    person_group_id = str(uuid4())
    person_group_name = 'mieru'
    cf = CognitiveFace(person_group_id, person_group_name)

    dirs = sorted([d for d in Path(dir_path).glob('*') if d.is_dir()])

    print('register faces')
    for index, sub_dir in enumerate(dirs):
        cf.register_faces(sub_dir)

    cf.train()

    print("check registered face")
    for sub_dir in dirs:
        for image_file in Path(sub_dir).glob('*.jpg'):
            result = cf.identify(image_file)
            print(image_file, cf.person_id_name_[result['personId']])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: register_faces.py image_dir_path')
        exit(-1)

    main(sys.argv)
