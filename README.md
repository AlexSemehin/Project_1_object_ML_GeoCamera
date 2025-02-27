# GeoCameraObject

Программа для создания точного позиционирования дорожных знаков и других объектов дорожного комплекса в пространстве.

Данное программное обеспечение предназначено для автоматизации обработки данных (распознавание объектов на панорамных снимках и их позиционирование).

## Функционал программы

Детекция и позиционирование объектов. Панорамные снимки были выполнены мобильным лазерным комплексом Alpha 3D Dual, оснащенным панорамной камерой LadyBag 5+.

Реализовано детектирование объектов с использованием дообучения существующей модели Yolo по двум классам (класс 1 - дорожный знак 6.13 «Километровый знак», класс 2 - знаки 5.19.1, 5.19.2 «Пешеходный переход»), позиционирование объектов выполняется  по координатам фотокамеры. Распознанные объекты сохраняются в соотвествующий слой shp

## Тестовый проект:

В тестовом проекте использовано 9628 изображений. Эти изображения получены при выполнении мобильного лазерного сканирования автомобильной дороги А393 "Южно-Сахалинск – Оха", участок автомобильной дороги протяженностью 63 км.

Панорамные снимки выполнялись каждую секунды.

Детекцию тестового проекта (9628 изображений) программа выполняла с 12:41:00 до 14:18:00 (97 минут)

## Авторы

*   Семехин Алексей Сергеевич ([https://github.com/AlexSemehin](https://github.com/AlexSemehin)) - AlexSemehin@yandex.ru
*   Сурикова Ксения Витальевна ([https://github.com/ksusha19ru](https://github.com/ksusha19ru)) - letitbe03@yandex.ru

## Инструкция по установке и использованию

Релиз программы доступен по ссылке: [https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/releases/tag/v1.0.0](https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/releases/tag/v1.0.0)

### 1. Требования

*   Python 3.7+
*   ([Необходимые библиотеки](https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/requirements.txt))

### 2. Установка

1.  Клонируйте репозиторий:

    ```bash
    git clone https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera.git
    cd Project_1_object_ML_GeoCamera
    ```

2.  (Опционально) Создайте и активируйте виртуальное окружение:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate  # Windows
    ```

3.  Установите необходимые библиотеки:

    ```bash
    pip install -r requirements.txt 


### 3. Использование

Запустите программу с использованием Python-скрипта или Jupyter Notebook:

*   **Python-скрипт:**

    ```bash
    python ML_GeoCamera.py [аргументы, если есть]
    ```
*   **Jupyter Notebook:**

    1.  Установите Jupyter Notebook (если еще не установлен): `pip install jupyter`
    2.  Запустите Jupyter Notebook: `jupyter notebook`
    3.  Откройте файл `ML_GeoCamera.ipynb` в браузере.


## Информация о зависимостях

Зависимости указаны в файле `requirements.txt` или должны быть установлены вручную (см. раздел "Требования").  Основные зависимости включают `opencv-python`, `torch`, `torchvision`, `yolov5`.

## Ссылки на ресурсы

*   **Python-скрипт:** [https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/ML_GeoCamera.py](https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/ML_GeoCamera.py)
*   **Jupyter Notebook:** [https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/ML_GeoCamera.ipynb](https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/ML_GeoCamera.ipynb)
*   **Модель машинного обучения (best.pt):** [https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/best.pt](https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/best.pt)
*   **Тест:** [https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/test.zip](https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/test.zip)
*   **Лицензия:** [https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/LICENSE](https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/LICENSE)
  

## Поддержка

Если у вас возникли сложности или вопросы по поводу необходимого пакета, создайте обсуждение в данной репозитории или напишите на электронную почту:

*   AlexSemehin@yandex.ru
*   letitbe03@yandex.ru

## Планы развития

*   Планируется использование детектирования всех доступных дорожных знаков (около 200) ПДД и позиционирование объектов с точностью топографической съемки масштаба 1:2000 (не более 1 метра).
*   Одним из направления развития может стать ГИС с созданием структурных линий автомобильной дороги. Необходимо разработать модель машинного обучения. В версии v1.01 используется дообучение yolo 8.

## Лицензия

Данный проект распространяется под лицензией MIT. См. файл [LICENSE](https://github.com/AlexSemehin/Project_1_object_ML_GeoCamera/blob/main/LICENSE) для получения дополнительной информации.
