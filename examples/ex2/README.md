# Демонстрация 2: Решение бизнес-задачи через `/chat`

API `generate` отлично подходит для single-shot интеграций. Но для удобства разработки сложных скриптов (полноценный Human-in-the-Loop) мы реализовали интерфейс контекстного чата.

В этом демо мы решим реальную продуктовую задачу за 3 итерации. **Цель:** Посчитать суммарный бюджет всех несовершеннолетних пользователей.

> **Требования:** Запускайте команды из корня проекта.

### Шаг 1. Поиск нужных объектов

Просим систему выбрать из таблицы только пользователей младше 18 лет.

```bash
curl -s -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{"messages": [
  {"role": "user", "content": "Выведи список пользователей у которых age < 18 из переменной wf.vars.users"}
]}' | jq -r '.result' | sed 's/^lua{//; s/}lua$//' | tee script.lua && cat script.lua | lua5.4 ../../test_runner.lua
```

**Результат в эмуляторе:** Выведены таблицы пользователей `Ivan (16 лет)` и `Oleg (15 лет)`.

### Шаг 2. Извлечение конкретного поля

Система написала хороший фильтр, но нам нужны не целые объекты, а только их бюджеты. Добавляем уточнение в контекст.

```bash
curl -s -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{"messages": [
  {"role": "user", "content": "Выведи список пользователей у которых age < 18 из переменной wf.vars.users"},
  {"role": "assistant", "content": "lua{ local r = _utils.array.new(); for _,u in ipairs(wf.vars.users) do if u.age < 18 then table.insert(r,u) end end; return r }lua"},
  {"role": "user", "content": "Окей, теперь отфильтруй у них только поле budget. Верни массив из чисел."}
]}' | jq -r '.result' | sed 's/^lua{//; s/}lua$//' | tee script.lua && cat script.lua | lua5.4 ../../test_runner.lua
```

**Результат в эмуляторе:** Выведен массив из двух чисел: `1500` и `800`.

### Шаг 3. Агрегация данных

Финальный этап бизнес-логики — суммирование.

```bash
curl -s -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d '{"messages": [
  {"role": "user", "content": "Выведи список пользователей у которых age < 18 из переменной wf.vars.users"},
  {"role": "assistant", "content": "lua{ local r = _utils.array.new(); for _,u in ipairs(wf.vars.users) do if u.age < 18 then table.insert(r,u) end end; return r }lua"},
  {"role": "user", "content": "Окей, теперь отфильтруй у них только поле budget. Верни массив из чисел."},
  {"role": "assistant", "content": "lua{ local r = _utils.array.new(); for _,u in ipairs(wf.vars.users) do if u.age < 18 then table.insert(r,u.budget) end end; return r }lua"},
  {"role": "user", "content": "А теперь просуммируй их бюджеты и верни итоговое число."}
]}' | jq -r '.result' | sed 's/^lua{//; s/}lua$//' | tee script.lua && cat script.lua | lua5.4 ../../test_runner.lua
```

**Результат в эмуляторе:** Скрипт успешно отработал и вывел итоговую сумму `2300`.

---

**Итог:** Модель не только сгенерировала синтаксически верный код, но и продемонстрировала глубокое понимание контекста бизнес-задачи, корректируя скрипт по шагам (Human-in-the-Loop).
