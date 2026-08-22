/*
    CoffeeTrace - verificación de la base de datos existente.

    Este script es de solo lectura. No crea bases, logins, usuarios ni tablas.
*/
USE [CoffeeTrace];
GO

SELECT
    DB_NAME() AS base_datos_actual,
    ORIGINAL_LOGIN() AS login_actual,
    USER_NAME() AS usuario_base_datos,
    CAST(SERVERPROPERTY('ServerName') AS nvarchar(128)) AS servidor,
    CAST(SERVERPROPERTY('ProductVersion') AS nvarchar(128)) AS version_sql_server;
GO

SELECT
    dp.name AS usuario,
    dp.type_desc AS tipo_usuario
FROM sys.database_principals AS dp
WHERE dp.name = N'coffeetrace_app';
GO

SELECT
    miembro.name AS usuario,
    rol.name AS rol
FROM sys.database_role_members AS drm
INNER JOIN sys.database_principals AS rol
    ON rol.principal_id = drm.role_principal_id
INNER JOIN sys.database_principals AS miembro
    ON miembro.principal_id = drm.member_principal_id
WHERE miembro.name = N'coffeetrace_app'
ORDER BY rol.name;
GO
