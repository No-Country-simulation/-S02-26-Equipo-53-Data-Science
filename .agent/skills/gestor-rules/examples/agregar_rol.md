# Ejemplo: Agregar un Nuevo Rol

## Contexto
El usuario quiere agregar un nuevo rol al archivo RULES.md

## Entrada del Usuario
```
Agrega el rol de Arquitecto
```

## Proceso
1. Leer `.agent/rules/RULES.md`
2. Ubicar sección "TOPOLOGÍA DE AGENTES"
3. Crear nueva entrada de rol
4. Solicitar responsabilidades al usuario
5. Agregar al archivo
6. Confirmar operación

## Salida en RULES.md
```markdown
### 2. 🧠 ARQUITECTO (Diseñador de Sistema)
**Responsabilidades:**
- [Definidas por el usuario]

**Preguntas Clave:**
- [Definidas por el usuario]
```

## Log
```
LOG_INFO: gestor-rules: Nuevo rol 'Arquitecto' agregado a RULES.md
```
