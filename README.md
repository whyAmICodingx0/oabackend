# OA System - Backend (Django)

本專案為 OA 系統後端，使用 Django REST Framework 開發，具備請假流程、通知公告、員工管理等功能。支援 JWT 驗證、第三方 API 串接（天氣查詢）與 Celery 排程，部署可支援 Docker。

## 功能
- 員工請假系統（含審核流程與狀態流轉）
- 通知公告管理（發布、是否已讀）
- 员工管理（CRUD、新增員工）
- JWT 驗證與權限控管（員工／主管）
- 第三方 API 串接（天氣 API）
- Celery 排程任務

## 安裝
```bash
git clone https://github.com/你的帳號/oabackend.git
cd oabackend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py initdepartments
python manage.py inituser
python manage.py initabsenttype
python manage.py runserver
```

## Docker 快速啟動
```bash
docker-compose up --build
```

## 作者
由 @whyAmICodingx0 開發，歡迎交流與改進建議。
