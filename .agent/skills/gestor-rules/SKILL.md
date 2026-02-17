---
name: Gestor de Rules del Proyecto
description: Actualiza y mantiene los archivos en .agent/rules/ incluyendo roles, principios, stack y decisiones
---

# Skill: Gestor de Rules del Proyecto

## Propósito
Mantener TODOS los archivos de reglas en `.agent/rules/` actualizados, coherentes y sincronizados.

## Archivos que Gestiona

```
.agent/rules/
├── RULES.md                        # Índice
├── topologia-agentes.md            # Roles del proyecto
├── instrucciones-comportamiento.md # Patrones de trabajo
├── principios-simplicidad.md       # Reglas de código
├── principios-responsive.md        # Diseño responsive
├── stack-tecnologico.md            # Tecnologías
└── decisiones-pendientes.md        # Por decidir
```

---

## Triggers de Activación

### Roles (topologia-agentes.md)
| Frase | Acción |
|-------|--------|
| "Agrega el rol de X" | Crear nueva sección de rol |
| "Modifica el rol X" | Actualizar rol existente |

### Comportamiento (instrucciones-comportamiento.md)
| Frase | Acción |
|-------|--------|
| "Nueva convención: X" | Agregar patrón |
| "Cambiar nomenclatura a X" | Actualizar sección |

### Principios (principios-simplicidad.md, principios-responsive.md)
| Frase | Acción |
|-------|--------|
| "Nuevo principio: X" | Agregar principio |
| "Regla de responsive: X" | Agregar a responsive |

### Stack Tecnológico (stack-tecnologico.md)
| Frase | Acción |
|-------|--------|
| "Vamos a usar X" | Confirmar y registrar tecnología |
| "Usaremos X para Y" | Registrar con propósito |
| "¿Qué stack tenemos?" | Mostrar resumen |
| "Cambiamos X por Y" | Actualizar tecnología |

### Decisiones (decisiones-pendientes.md)
| Frase | Acción |
|-------|--------|
| "Decidimos usar X" | Marcar decisión como tomada |
| "Pendiente: X" | Agregar nueva decisión |

---

## Proceso de Actualización

1. Detectar trigger en mensaje del usuario
2. Identificar archivo a modificar
3. Proponer cambio al usuario
4. Aplicar si aprueba
5. Verificar coherencia con otros archivos
6. Confirmar con log

---

## Verificación de Coherencia

Después de cada cambio verificar:
- [ ] No hay duplicación entre archivos
- [ ] Todos los archivos tienen `trigger: always_on`
- [ ] RULES.md refleja todos los archivos existentes
- [ ] Formato consistente (tablas, listas)

---

## Logs

Prefijo: `gestor-rules:`
```
LOG_INFO: "gestor-rules: Actualizando [archivo]"
LOG_INFO: "gestor-rules: Tecnología [X] registrada en stack"
LOG_INFO: "gestor-rules: Coherencia verificada"
LOG_WARN: "gestor-rules: Posible duplicación detectada"
```

---

## NO Gestiona

- Rules de skills individuales → Responsabilidad de `monitor-skills`
- Archivos fuera de `.agent/rules/`
