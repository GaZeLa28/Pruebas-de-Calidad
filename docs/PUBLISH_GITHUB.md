# Publicación en GitHub

Repositorio objetivo:

```text
https://github.com/GaZeLa28/Pruebas-de-Calidad.git
```

## Opción A: usar el Git Bundle entregado

```bash
git clone CoffeeTrace_Pruebas-de-Calidad_ExistingDB.git.bundle Pruebas-de-Calidad
cd Pruebas-de-Calidad
git remote set-url origin https://github.com/GaZeLa28/Pruebas-de-Calidad.git
git push -u origin main
git push -u origin develop
```

## Opción B: publicar la carpeta del ZIP

```bash
cd Pruebas-de-Calidad
git init
git branch -M main
git remote add origin https://github.com/GaZeLa28/Pruebas-de-Calidad.git
git add .
git commit -m "refactor: conectar CoffeeTrace a SQL Server existente"
git push -u origin main

git switch -c develop
git push -u origin develop
```

## Cuando el remoto ya contiene cambios

```bash
git fetch origin
git switch -c integration/coffeetrace-existing-db origin/develop
git merge --allow-unrelated-histories develop
# resolver conflictos, ejecutar pruebas y abrir Pull Request
```

No publique `.env`, contraseñas, tokens ni archivos `.mdf`/`.ldf`. El `.gitignore` ya excluye `.env`.

Proteja `main` y `develop`, exija Pull Request, una revisión aprobada y ejecución correcta de CI.
