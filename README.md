## ***Инструкция по запуску в `docker`***:
* Клонировать репозиторий:
   + ```bash
     ~$ git clone https://github.com/FuchkoDmitry/Social-Network.git
     ~$ cd social_network
     ```
* Создать файл `.env`:
    + ```bash
        ~$ cd social_network
        ~$ touch .env
        ```
* Внести в `.env` следующие переменные:
   + POSTGRES_USER=username
   + POSTGRES_PASSWORD=1234
   + POSTGRES_DB=db_name
   + POSTGRES_PORT=5432
   + POSTGRES_HOST=db
   + SECRET_KEY=your_secretkey
   + ALGORITHM=HS256
   + MAIL_FROM=your_email@mail.ru
   + MAIL_USERNAME=your_email@mail.ru
   + MAIL_SERVER=smtp.mail.ru(в зависимости от использованной почты, указан для mail почты)
   + MAIL_PORT=465(в зависимости от использованной почты, указан для mail почты)
   + MAIL_PASSWORD=password_for_external_apps([инструкция](https://help.mail.ru/mail/security/protection/external))
   + EMAIL_CHECK_API_KEY=[(ключ будет доступен по этой ссылке после регистрации)](https://app.abstractapi.com/api/email-validation/tester) [(регистрация в сервисе верификации email.)](https://app.abstractapi.com/users/signup?target=/api/email-validation/pricing/select)

* Запустить проект:
   + ```bash
     ~$ cd ..
     ~$ docker-compose up
     ```
     