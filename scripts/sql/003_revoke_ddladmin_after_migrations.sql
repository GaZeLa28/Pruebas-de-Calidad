/*
    Endurecimiento opcional para producción.
    Ejecutar con una cuenta administrativa después de aplicar migraciones.
*/
USE [CoffeeTrace];
GO

IF IS_ROLEMEMBER(N'db_ddladmin', N'coffeetrace_app') = 1
BEGIN
    ALTER ROLE [db_ddladmin] DROP MEMBER [coffeetrace_app];
    PRINT N'Rol db_ddladmin retirado de coffeetrace_app.';
END
ELSE
BEGIN
    PRINT N'coffeetrace_app no pertenece a db_ddladmin.';
END;
GO

SELECT
    IS_ROLEMEMBER(N'db_datareader', N'coffeetrace_app') AS es_datareader,
    IS_ROLEMEMBER(N'db_datawriter', N'coffeetrace_app') AS es_datawriter,
    IS_ROLEMEMBER(N'db_ddladmin', N'coffeetrace_app') AS es_ddladmin;
GO
