-- Функция для фильтрации массива чисел, оставляя только те, которые больше 10
function filterNumbers(numbers)
  local result = _utils.array.new()
  
  for _, number in ipairs(numbers) do
    if type(number) == "number" and number > 10 then
      table.insert(result, number)
    end
  end
  
  return result
end

-- Возврат отфильтрованного массива
return filterNumbers(wf.vars.numbers)
