CREATE VIEW IF NOT EXISTS items_count AS
SELECT champID, item1, item2, item3, COUNT(*) count
FROM champs
WHERE item1 <> 0
GROUP BY champID, item1, item2, item3;