# Приветствуем на GreenAtom!
###  Как это запустить?

1. Склонить репозиторий;
2. На ПК естественно должен быть установлен Python;
3. Создать virtualenv в папке куда скопировано содержимое (python3 -m venv env);
4. Активировать source env/bin/activate;
5. Установить пакеты - **pip install** -r **requirements**.txt;
6. Установить переменные окружения - export FLASK_APP="greenatom.py" (для win - set);
7. Установить БД - flask db upgrade, flask db migrate;
8. Выполнить ./run_all;
9. Открыть localhost:5000 и 5001 в браузере;


> Модели описаны в .ipynb-файлах в корневой директории (бейзлайн - требует доработки), данные csv (general-data.csv - Kaggle HR Attriction Prediction) также расположены в ней. Можно попробовать различные модели заменив файл model.pkl на другой результат (Рекомендую сгенерить их из jupiter ноутбуков самому так как на машинах с различной архитектурой (32/64) заранее подготовленные pkl-модели могут не запуститься (и возможно для xgb придется сменить размерности в конце файла routes.py - ValuePredictor)).

Удачи!