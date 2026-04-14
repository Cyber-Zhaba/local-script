-- Фильтруем массив wf.vars.numbers, оставляя только числа больше 10

local result = _utils.array.new()

for _, value in ipairs(wf.vars.numbers) do
  if type(value) == "number" and value > 10 then
    table.insert(result, value)
  end
end

return result
