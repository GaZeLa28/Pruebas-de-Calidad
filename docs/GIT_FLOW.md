# Estrategia Git Flow

## Ramas protegidas

- `main`: versión estable y etiquetada.
- `develop`: integración continua del sprint.

Ambas deben bloquear el push directo y exigir:

1. Pull Request.
2. Al menos una revisión aprobada.
3. Ejecución correcta del flujo de CI.
4. Rama actualizada antes del merge.

## Convención de ramas

```text
feature/HU01-login
feature/HU02-registro-productores
feature/HU06-creacion-lotes
feature/HU09-consulta-qr
hotfix/correccion-peso-lote
```

## Convención de commits

Se recomienda Conventional Commits:

```text
feat(producers): agregar registro de productores
fix(lots): impedir asignar más peso del disponible
test(receptions): cubrir tolerancia de peso
docs(api): documentar endpoint público QR
refactor(reports): separar consulta y renderizado
```

## Flujo de una historia

```bash
git switch develop
git pull origin develop
git switch -c feature/HU06-creacion-lotes
# desarrollar y probar
git add .
git commit -m "feat(lots): implementar creación de lotes"
git push -u origin feature/HU06-creacion-lotes
```

Luego se abre un Pull Request hacia `develop`, se vincula la historia de GitHub Projects y se solicita revisión cruzada.

## Cierre de sprint

```bash
git switch main
git merge --no-ff develop
git tag -a v0.1-sprint1 -m "Entrega del Sprint 1"
git push origin main --tags
```
