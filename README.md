# Расчет параметров урожайности

Программа состоит из:

1) Папки "1_первая часть сезона", внутри которой: \
   a) Папка "метео" для метеофайлов из первой части сезона. Формат данных - csv. Если в данных встречаются лишние  
   записи формата
   > TOGUCHI,55.2167,84.3667,2022/05/01,16,7.5,0,39,3.4            01.05.2022

   или
   > TOGUCHI,55.2167,84.3667,2022/01,-10.1,-19.3,16.2,78.6,1.5

   то программа отбрасывает ненужные данные (число в первом случае, всю строку во втором) \
   b) Папка "солнечная радиация" для файлов солнечной радиации из первой части сезона
2) Папки "2_вторая часть сезона", внутри которой: \
   a) Папка "метео" для метеофайлов из второй части сезона. Формат данных - xlxs. \
   b) Папка "солнечная радиация" для файлов солнечной радиации из второй части сезона. Формат данных - xlxs.
3) Папки "excels", внутри которой:
   a) Таблица constant_raion.xlsx - таблица с константами.
   b) Таблица "Перечень_район_метеостанция" - таблица соответствия районов в метеофайлах и районов в файлах солнечной
   радиации
   c) Таблица "Таблица вычислений_НСО_районы" - таблица содержащая название района, дату начала посадки, дату конца
   посадки, индексы HI (три столбца). В эту же таблицу программа записывает результат (в столбцы 7-9)

Для корректной работы программы необходимо разместить файлы с соответствующими именами в нужных папках.

Для запуска программы необходимо запустить main.py