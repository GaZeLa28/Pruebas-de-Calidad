/*
    Ejecutar después de: python manage.py migrate
    Consulta las tablas e índices creados por Django sin modificar datos.
*/
USE [CoffeeTrace];
GO

SELECT
    s.name AS esquema,
    t.name AS tabla,
    SUM(p.rows) AS filas
FROM sys.tables AS t
INNER JOIN sys.schemas AS s
    ON s.schema_id = t.schema_id
INNER JOIN sys.partitions AS p
    ON p.object_id = t.object_id
    AND p.index_id IN (0, 1)
GROUP BY s.name, t.name
ORDER BY s.name, t.name;
GO

SELECT
    OBJECT_SCHEMA_NAME(i.object_id) AS esquema,
    OBJECT_NAME(i.object_id) AS tabla,
    i.name AS indice,
    i.is_unique
FROM sys.indexes AS i
WHERE i.name IS NOT NULL
ORDER BY esquema, tabla, indice;
GO
