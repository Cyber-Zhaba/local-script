-- Фильтруем список пользователей, оставляя только тех, у кого возраст меньше 18 лет
local result = {}
for _, user in ipairs(wf.vars.users) do
	if type(user.age) == "number" and user.age < 18 then
		table.insert(result, user)
	end
end

-- Возвращаем отфильтрованный список пользователей
return result
