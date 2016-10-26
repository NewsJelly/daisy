# Daisy
데이터를 시각화하는 솔루션, 데이지의 오픈 소스 프로젝트입니다.

데모: http://daisy.newsjel.ly/solution/

## 특징
1. 실시간 데이터 연동
1. 시각화 프레임 워크
1. 다양한 시각화 유형
1. 시각화 추천 기술

## 요구 사항
데이지는 Django 1.9, Python 2.7을 필요로 합니다.

## 필요 시스템 라이브러리
아래의 라이브러리가 필요하며 데이터베이스와 관련된 라이브러리는 선택 사항입니다.

- python-dev (for compilation and linking)
- libjpeg (for JPEG support in Pillow)
- zlib (for PNG support in Pillow)
- libpq-dev (for `psycopg2`)
- mysql-devel (for `MySQL`)

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
(env) $ python manage.py makemigrations && python manage.py migrate --run-syncdb
(env) $ python manage.py loaddata dumpdata/VisualizeType.json
(env) $ python manage.py runserver
```

또는, [링크](https://github.com/NewsJelly/daisy/wiki/%EB%8F%85%EB%A6%BD-%EC%84%9C%EB%B2%84-%EA%B5%AC%EC%B6%95)를 참조하여 독립된 서버를 구축할 수 있습니다.

## 문의
<daisy@newsjel.ly>로 문의하시기 바랍니다.
