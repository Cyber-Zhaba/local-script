![Титульник](docs/Титульник.jpg)

# 🚀 LocalScript: Локальная мультиагентная система для генерации кода

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135%2B-green)
![VRAM](https://img.shields.io/badge/VRAM-%E2%89%A4%208GB-red)
![Zero_Leakage](https://img.shields.io/badge/Data_Leakage-0%25-success)

**LocalScript** — это локальная AI-система для генерации кода под специфичные корпоративные фреймворки, проприетарные API и LowCode-экосистемы. Система работает полностью в закрытом контуре, переводит задачи с естественного языка в готовый скрипт (например, Lua) и автоматически валидирует его через локальный компилятор.

## ⚡ Quick Start

### Требования

- Docker & Docker Compose
- NVIDIA GPU (8 GB VRAM) + NVIDIA Container Toolkit

### Запуск (One-Click)

1. Клонируйте репозиторий.
2. Поднимите инфраструктуру (модель скачается автоматически на этапе инициализации):

   ```bash
   docker compose up --build
   ```

3. **⏳ ВАЖНО:** При первом запуске сервис `init` выполнит `ollama pull qwen2.5-coder:7b-instruct` и загрузит базу знаний в Qdrant. Бэкенд API будет доступен **только после того**, как в консоли появится ASCII-арт `Local Script`.

## 🎯 Почему LocalScript? (Или решаемые проблемы)

Публичные LLM (ChatGPT, Copilot) не знают внутренних стандартов вашей компании и ваших закрытых библиотек. А отправка коммерческой тайны во внешние API нарушает NDA.

LocalScript решает эту проблему:

- 🔒 **Zero Data Leakage:** Полный On-Premise. Никаких внешних вызовов.
- 💻 **Low VRAM Footprint:** Вся генерация идет на локальной GPU (Qwen2.5-Coder квантованная версия, пиковое потребление ≤ 8.0 GB VRAM).
- 🔄 **Self-Healing Code:** Сгенерированный код прогоняется через компилятор. Если есть ошибка, агенты исправляют её без участия человека.
- 🧩 **Агностичность:** Легко настраивается под любой DSL (Domain-Specific Language) через редактирование RAG-базы.

_(Успешно протестировано на сценариях интеграции с LowCode платформой МТС Octapi)._

## 🎮 Демонстрации и Тестирование

Чтобы продемонстрировать работу системы, мы подготовили эмулятор закрытой экосистемы
Выберите сценарий:

👉 **[Демонстрация 1: Работа эндпоинта /generate (Single-shot)](examples/ex1/README.md)**  
👉 **[Демонстрация 2: Продуктовая задача через Human-in-the-Loop (Chat UI)](examples/ex2/README.md)**

## 🧠 Мультиагентная архитектура "Под капотом"

Система построена на чистом Python-бэкенде (без тяжеловесного LangChain), где взаимодействуют 4 агента:

1. 🧐 **Аналитик:** Проверяет полноту ТЗ. При необходимости запрашивает уточнения (Human-in-the-Loop).
2. 📚 **RAG-модуль:** Ищет релевантные примеры в векторной БД `Qdrant` (на CPU).
3. 💻 **Кодер (Qwen2.5-Coder):** Генерирует код строго по заданным `BEST_PRACTICES`.
4. 🛠 **Фиксер + Чекер:** Прогоняет код через локальный компилятор (в нашем примере `luac`). Обратная связь от компилятора отправляется Кодеру для исправления багов.

[![](https://mermaid.ink/img/pako:eNqNVW1rG0cQ_ivLhoAEd7JOp9fDGFw7TVzk2qnsfmiuH1a6lSVyulNXJxLXMig2aQMKuLRfQgtNC_lauKQ2UWTL-Qt7_6gzu3IsFwtyQtzu3uzMM888s3tAG6HHqUP3BOu2yM66GxB47t4l8k_5MRnKM3kK_3P4T-VYnhH5UV7K8-SlfA_vdzJOjvBzcqL37fa4SD1yqXx9q9VLskTkXzKW78FzLN_Ky-Qo-Rn8TpbrYmklJd_AylBeJMcQcZwM4X2WHBHwEgOMGE0N8qDfYYHZDsyoxc1qGHbTLv0-7QYaQa9f16lUwwbzaw3R7kYEEM1Pa_u9iHdISr5S-FQojROSnCYj-UGHnACCESBUCxOwmMLkOBliQB0Nn-sRsvY7mF0okqbIGe4myTOI8ExxcJGMru3XWiwCaMv1ld0NYAanZCOIuGiyBl9eqq9oVmqR4KzjtyNDsQ-gjki5kLXS6rN8hY6RT3iPIYlZAqcwiSG3S_nvArir2xs6-uoeD6Ie2RKNFu9FgkWhuI7-JetFYDkL9gf6w4LJ2CHyF0gyVvxh6Imh0z9FODB-g2uQO8wyevc_QM1bJSlEN0VPJLW2vZvGzGY1wFTAO_H7rLEA-ENPsCB6lHJpav2LNIEMvuUNAE3WWcTqrDfHnTadI65o27bO5ZvV-2byQsnwXNV2RAAOzGIsPipgqgQxlh9cmr4VyJbvsw7TJCqBkWp1k9wL9trBHAZtNYfBsvJ2XoP44QkPcpmCiV0onFIddA0V6DcikroPvCgCbgrsV0B6DLIaqpbUTQkkv0tOAPH4prjIsmmuDKAZz2adjC0UX3ENMoW6Aecqb61QbL-xHGuC7tV2UCQgza9qW18PcHxDPZ_cX-JuOSEqCp4VqpXAHZCaPNfxxhDvTNdYNxOgUWEe7OxsQwgox2BW2duC_KbS1Tr_CcKdkGqfmbc50lg16doTD7wrFmcMgqMXC7jDI4yYpjkAO3X44QE010wEwwwUvf_f8Bqqe4ItjuckHiCKZ-B1RJagxTh0FifI6ozKa0h_qwaCRsJtOr_ZcRbt-_zGWdZs-75zp1nBnwFaCR9z5w6IejY2n7S9qOXkuk-vFjzWazEh2L5DCqQw71Yh1_6y5XyuVDcaoR8K8N5sztspKWk7yyqW694CO6zWZ5jpIn-OpS7iIktqwK3V9qgDDcMN2uGiw3BKD9CHS-F-6HCXOjD0mHjsUkOv42QT-g0_4VY3OARXXRZ8F4adK28i7O-1qNNkfg9m_a4HtVtvM7hbOp9WBQiLi7WwH0TUsUtZ5YQ6B_QpdSwrk68US_lKuVSq5CrFctmg-7CctTNWuVAq5MrFcrGQs_OHBv1RxbUyWdu2srlSpWDliyXbsg3KvTaca5v6ilY39eF_ktdbjA?type=png)](https://mermaid.live/edit#pako:eNqNVW1rG0cQ_ivLhoAEd7JOp9fDGFw7TVzk2qnsfmiuH1a6lSVyulNXJxLXMig2aQMKuLRfQgtNC_lauKQ2UWTL-Qt7_6gzu3IsFwtyQtzu3uzMM888s3tAG6HHqUP3BOu2yM66GxB47t4l8k_5MRnKM3kK_3P4T-VYnhH5UV7K8-SlfA_vdzJOjvBzcqL37fa4SD1yqXx9q9VLskTkXzKW78FzLN_Ky-Qo-Rn8TpbrYmklJd_AylBeJMcQcZwM4X2WHBHwEgOMGE0N8qDfYYHZDsyoxc1qGHbTLv0-7QYaQa9f16lUwwbzaw3R7kYEEM1Pa_u9iHdISr5S-FQojROSnCYj-UGHnACCESBUCxOwmMLkOBliQB0Nn-sRsvY7mF0okqbIGe4myTOI8ExxcJGMru3XWiwCaMv1ld0NYAanZCOIuGiyBl9eqq9oVmqR4KzjtyNDsQ-gjki5kLXS6rN8hY6RT3iPIYlZAqcwiSG3S_nvArir2xs6-uoeD6Ie2RKNFu9FgkWhuI7-JetFYDkL9gf6w4LJ2CHyF0gyVvxh6Imh0z9FODB-g2uQO8wyevc_QM1bJSlEN0VPJLW2vZvGzGY1wFTAO_H7rLEA-ENPsCB6lHJpav2LNIEMvuUNAE3WWcTqrDfHnTadI65o27bO5ZvV-2byQsnwXNV2RAAOzGIsPipgqgQxlh9cmr4VyJbvsw7TJCqBkWp1k9wL9trBHAZtNYfBsvJ2XoP44QkPcpmCiV0onFIddA0V6DcikroPvCgCbgrsV0B6DLIaqpbUTQkkv0tOAPH4prjIsmmuDKAZz2adjC0UX3ENMoW6Aecqb61QbL-xHGuC7tV2UCQgza9qW18PcHxDPZ_cX-JuOSEqCp4VqpXAHZCaPNfxxhDvTNdYNxOgUWEe7OxsQwgox2BW2duC_KbS1Tr_CcKdkGqfmbc50lg16doTD7wrFmcMgqMXC7jDI4yYpjkAO3X44QE010wEwwwUvf_f8Bqqe4ItjuckHiCKZ-B1RJagxTh0FifI6ozKa0h_qwaCRsJtOr_ZcRbt-_zGWdZs-75zp1nBnwFaCR9z5w6IejY2n7S9qOXkuk-vFjzWazEh2L5DCqQw71Yh1_6y5XyuVDcaoR8K8N5sztspKWk7yyqW694CO6zWZ5jpIn-OpS7iIktqwK3V9qgDDcMN2uGiw3BKD9CHS-F-6HCXOjD0mHjsUkOv42QT-g0_4VY3OARXXRZ8F4adK28i7O-1qNNkfg9m_a4HtVtvM7hbOp9WBQiLi7WwH0TUsUtZ5YQ6B_QpdSwrk68US_lKuVSq5CrFctmg-7CctTNWuVAq5MrFcrGQs_OHBv1RxbUyWdu2srlSpWDliyXbsg3KvTaca5v6ilY39eF_ktdbjA)

## ⚙️ Как адаптировать LocalScript под вашу компанию?

Вся бизнес-логика вынесена в папку `prompts/`. Чтобы заставить LocalScript писать код для вашей платформы:

1. Отредактируйте `agents.json` под вашу специфику.
2. Замените правила в `LUA_BEST_PRACTICES.md` на ваши стандарты кодирования.
3. Положите примеры вашего кода в `examples.json` (при рестарте система сама векторизует их для RAG).
