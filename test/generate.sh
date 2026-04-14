#!/usr/bin/fish

echo "Однострочные запросы"

echo "Найди среднее арифметическое чисел в wf.vars.numbers. Игнорируй nil и строки."
curl -s -X POST http://localhost:8000/generate -H "Content-Type: application/json" \
  -d '{"prompt": "Найди среднее арифметическое чисел в wf.vars.numbers. Игнорируй nil и строки."}' |
  jq -r '.result' | sed 's/^lua{//; s/}lua$//' | tee script.lua && cat script.lua | lua5.4 test_runner.lua

echo "Извлеки только домены (всё что после @) из массива wf.vars.emails и верни их новым массивом."
curl -s -X POST http://localhost:8000/generate -H "Content-Type: application/json" \
  -d '{"prompt": "Извлеки только домены (всё что после @) из массива wf.vars.emails и верни их новым массивом."}' |
  jq -r '.result' | sed 's/^lua{//; s/}lua$//' | tee script.lua && cat script.lua | lua5.4 test_runner.lua

echo "Отсортируй массив wf.vars.transactions и верни его."
curl -s -X POST http://localhost:8000/generate -H "Content-Type: application/json" \
  -d '{"prompt": "Отсортируй массив wf.vars.transactions и верни его."}' |
  jq -r '.result' | sed 's/^lua{//; s/}lua$//' | tee script.lua && cat script.lua | lua5.4 test_runner.lua

echo "Верни массив транзакций из wf.vars.transactions, где amount больше 1000."
curl -s -X POST http://localhost:8000/generate -H "Content-Type: application/json" \
  -d '{"prompt": "Верни массив транзакций из wf.vars.transactions, где amount больше 1000."}' |
  jq -r '.result' | sed 's/^lua{//; s/}lua$//' | tee script.lua && cat script.lua | lua5.4 test_runner.lua

echo "Вытащи только год из переменной wf.initVariables.iso_date. Формат даты YYYY-MM-DDTHH:MM:SS"
curl -s -X POST http://localhost:8000/generate -H "Content-Type: application/json" \
  -d '{"prompt": "Вытащи только год из переменной wf.initVariables.iso_date. Формат даты YYYY-MM-DDTHH:MM:SS"}' |
  jq -r '.result' | sed 's/^lua{//; s/}lua$//' | tee script.lua && cat script.lua | lua5.4 test_runner.lua
