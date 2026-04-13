#!/usr/bin/fish

echo "Однострочные запросы"

echo "Вопрос 1: напиши функцию которая вычисляет факториал"
time curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "напиши функцию которая вычисляет факториал"}'

echo "Вопрос 2: Создай новый пустой массив и добавь в него все значения больше 10 из массива wf.vars.numbers"
time curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Создай новый пустой массив и добавь в него все значения больше 10 из массива wf.vars.numbers"}'

echo "Вопрос 3: Отфильтруй список транзакций в переменной transactions"
time curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Отфильтруй список транзакций в переменной transactions"}'

echo "Вопрос 4: Возьми имя из переменной first_name и фамилию из last_name. Верни строку приветствия: Привет, [Имя] [Фамилия]!"
time curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Возьми имя из переменной first_name и фамилию из last_name. Верни строку приветствия: Привет, [Имя] [Фамилия]!"}'

echo "Вопрос 5: Увеличивай значение переменной try_count_n на каждой итерации"
time curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Увеличивай значение переменной try_count_n на каждой итерации"}'
