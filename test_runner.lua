wf = {
	vars = {
		numbers = { 15, -5, 42, 8, 100, nil, "error" },
		emails = { "admin@corp.com", "user1@mail.ru", "support@corp.com" },
		transactions = { { id = 1, amount = 1200 }, { id = 2, amount = 300 }, { id = 3, amount = 5500 } },
		users = {
			{ name = "Ivan", age = 16, budget = 1500 },
			{ name = "Anna", age = 22, budget = 5000 },
			{ name = "Oleg", age = 15, budget = 800 },
			{ name = "Nina", age = 19, budget = 2000 },
		},
		prices = { 100, 200, 300 },
	},
	initVariables = {
		iso_date = "2023-12-31T23:59:59+00:00",
	},
}

_utils = {
	array = {
		new = function()
			return {}
		end,
		isArray = function(t)
			return type(t) == "table"
		end,
	},
}

local script_code = io.read("*all")
local func, err = load(script_code)

if not func then
	print("\n/!\\ Ошибка компиляции: " .. err)
	os.exit(1)
end

local success, result = pcall(func)

if not success then
	print("\n/!\\ Ошибка выполнения (Runtime): " .. tostring(result))
else
	print("\n[+] РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ:")
	if type(result) == "table" then
		for k, v in pairs(result) do
			if type(v) == "table" then
				print("[" .. k .. "]", "Table: name=" .. tostring(v.name) .. ", budget=" .. tostring(v.budget))
			else
				print("[" .. k .. "]", v)
			end
		end
	else
		print(tostring(result))
	end
end
