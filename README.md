# Azure FaceAPI test

## 動作環境
Python 3.6

## インストール
FaceAPIのSDKをインストールする
``` bash
$ pip install cognitive-face
```

## 使い方

1. config.jsonのKeyにFaceAPIのKEYを追記
2. 実行

``` bash
$ python register_faces.py face_image_dir [options]
```
face_image_dir: 顔画像ディレクトリ  
[options]  
--person_group_id [id]: 人物グループID  
--person_group_name [name]: 人物グループ名  

注) face_image_dirはサブディレクトリに人物名、サブディレクトリ以下に顔画像が配置されていること。
```
face_image_dir/
   人物1/person1_0001.jpg
           person1_0002.jpg
           .....
   人物2/person2_0001.jpg
           person2_0002.jpg
```
