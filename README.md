# Daisy

데이터를 시각화하는 솔루션, 데이지의 오픈 소스 프로젝트입니다.

데모: http://daisy.newsjel.ly/solution/

## 특징
1. 실시간 데이터 연동
1. 시각화 프레임 워크
1. 다양한 시각화 유형
1. 시각화 추천 기술

## 빠르게 시작하기
```
$ git clone https://github.com/NewsJelly/daisy.git daisy
$ pip install --upgrade virtualenv
$ virtualenv env
$ source env/bin/activate
(env) $ cd daisy
(env) $ pip install -r requirements.txt
(env) $ cd daisy
(env) $ mkdir -p media/uploaded_images && mv dumpdata/*data media/uploaded_images
(env) $ python manage.py makemigrations && python manage.py migrate
(env) $ python manage.py loaddata dumpdata/VisualizeType.json
(env) $ python manage.py runserver
```
