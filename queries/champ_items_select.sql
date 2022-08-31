SELECT champID, item1, item2, item3
FROM items_count
GROUP BY champID
HAVING count = MAX(count);