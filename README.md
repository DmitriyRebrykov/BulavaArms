## 🧰 Установка

1. Клонируйте репозиторий:

```bash
git clone ...
cd ...
```
2. Создайте виртуальное окружение:

```bash
python -m venv venv
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4.Создать .env

```bash
SECRET_KEY=...
POSTGRES_DB=blockwear_db
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_HOST=localhost
POSTGRES_PORT=...

STRIPE_PUBLIC_KEY=...
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
```

5. Выполните миграции БД:
   
```bash
python manage.py migrate
```

6. Создайте суперпользователя (админ-панель):
   
```bash
python manage.py createsuperuser
```

7.Создать .env

```bash
SECRET_KEY=...

LIQPAY_PUBLIC_KEY=...
LIQPAY_PRIVATE_KEY=...
```

8. Запустите сервер разработки:
```bash
python manage.py runserver
```

