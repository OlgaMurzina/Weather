# Weather
*Цель*  
Простой локальный проект по типу: запрос к сайту - ответ - парсинг - занесение в БД - построение витрины - визуализация
Запуск с определенной периодичностью в виде скрипта с расписанием из файла crontab

*Технологии*  
* Запрос - requests
* Парсинг ответа и загрузка в БД - SQLAlchemy
* Витрины - SQLAlchemy + Pandas
* Визуализация - Seaborn

*Особенности*  
Проверка дублей при парсинге и удаление старых дублирующих записей по сложному ключу дата_время + название города
