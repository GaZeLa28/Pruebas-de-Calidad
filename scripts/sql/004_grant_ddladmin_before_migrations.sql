/*
    Ejecutar solamente cuando se necesiten nuevas migraciones en producción.
    Después de migrar, vuelva a ejecutar 003_revoke_ddladmin_after_migrations.sql.
*/
USE [CoffeeTrace];
GO

IF IS_ROLEMEMBER(N'db_ddladmin', N'coffeetrace_app') <> 1
BEGIN
    ALTER ROLE [db_ddladmin] ADD MEMBER [coffeetrace_app];
    PRINT N'Rol db_ddladmin asignado temporalmente a coffeetrace_app.';
END
ELSE
BEGIN
    PRINT N'coffeetrace_app ya pertenece a db_ddladmin.';
END;
GO
