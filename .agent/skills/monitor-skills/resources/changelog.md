# Changelog de Skills

Registro de cambios en los skills del proyecto.

---

## 2026-01-30

### Migración de Nomenclatura
- Convenciones cambiadas de español a **inglés camelCase**
- Carpetas renombradas: `utilidades/` → `utils/`, `estilos/` → `styles/`
- `logger.js` refactorizado: `log_Secuencia()` → `logSequence()`
- `variables.css` refactorizado: `--espacio-*` → `--space-*`
- Comentarios se mantienen en español

### Nuevos Workflows
- `/crear-skill-conocimiento` - Crear skill desde fuente del usuario
- `/crear-skill-conocimiento-documentado` - Crear skill buscando docs online
- `/actualizar-skill-conocimiento` - Actualizar skill con fuente del usuario
- `/actualizar-skill-conocimiento-documentado` - Actualizar skill con docs online

### Nueva Rule
- `detector-tecnologias.md` - Detecta menciones de tecnologías y sugiere workflows

### Eliminados
- **monitor-stack**: Eliminado (funcionalidad integrada en gestor-rules)

### Actualizados
- `instrucciones-comportamiento.md` - Nuevas convenciones en inglés
- `principios-simplicidad.md` - Ejemplos actualizados
- `principios-responsive.md` - Variables CSS en inglés
- `RULES.md` - Índice actualizado

---

## Plantilla de Entrada

```markdown
## [FECHA]

### Nuevos
- **[skill]**: descripción

### Actualizados
- **[skill]**: cambio

### Eliminados
- **[skill]**: razón
```
