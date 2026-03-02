# Rules: gestor-rules

Reglas específicas para el skill de gestión de rules.

---

## Archivos que Gestiona

Todos los archivos en `.agent/rules/`:
- RULES.md (índice)
- topologia-agentes.md
- instrucciones-comportamiento.md
- principios-simplicidad.md
- principios-responsive.md
- stack-tecnologico.md
- decisiones-pendientes.md

---

## Operaciones por Archivo

| Archivo | Operaciones |
|---------|-------------|
| topologia-agentes | Agregar/modificar roles |
| instrucciones-comportamiento | Agregar convenciones |
| principios-simplicidad | Agregar principios código |
| principios-responsive | Agregar reglas responsive |
| stack-tecnologico | Confirmar/actualizar tecnologías |
| decisiones-pendientes | Registrar/resolver decisiones |

---

## Proceso de Confirmación de Stack

Cuando el usuario menciona una tecnología:
1. Detectar mención ("Vamos a usar X", "Usaremos X")
2. Preguntar: "¿Confirmas [X] para [propósito]?"
3. Si confirma → Actualizar stack-tecnologico.md
4. Agregar entrada al historial de cambios
5. Confirmar con log

---

## Checklist de Coherencia

Verificar después de cada cambio:
- [ ] Todos los archivos tienen `trigger: always_on`
- [ ] No hay información duplicada entre archivos
- [ ] RULES.md lista todos los archivos existentes
- [ ] Formato de tablas y listas es consistente

---

## Logs

Prefijo: `gestor-rules:`

---

## NO Gestiona

- Rules de skills → Responsabilidad de `monitor-skills`
- Archivos fuera de `.agent/rules/`
