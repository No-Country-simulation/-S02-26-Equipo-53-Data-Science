---
trigger: always_on
---

# 📋 Decisiones Pendientes
 
Registro de decisiones por tomar en el proyecto.

---

## Estado: 🟡 En Definición

---

## Decisiones Técnicas

### 1. Framework Frontend
| Opción | Pros | Contras |
|--------|------|---------|
| Vanilla JS | Simple, sin build | Manual para UI compleja |
| React | Componentes reactivos | Overhead de setup |
| Vue | Balance simplicidad/poder | Aprender syntax |

**Estado:** ⏳ Pendiente  
**Decisión:** -

---

### 2. Sistema de Almacenamiento para Flashcards
| Opción | Capacidad | Sincronización |
|--------|-----------|----------------|
| localStorage | ~5MB | ❌ Solo local |
| IndexedDB | ~50MB+ | ❌ Solo local |
| Backend + DB | Ilimitado | ✅ Multi-dispositivo |

**Estado:** ⏳ Pendiente  
**Decisión:** -

---

### 3. Enrutamiento para Doble Interfaz
| Opción | Complejidad | Caso de Uso |
|--------|-------------|-------------|
| Sin router | Baja | SPA simple |
| Hash router | Media | Múltiples vistas |
| History API | Alta | URLs limpias |

**Estado:** ⏳ Pendiente  
**Decisión:** -

---

## Cómo Registrar una Decisión

Cuando se tome una decisión:

```markdown
**Estado:** ✅ Decidido (2026-01-30)  
**Decisión:** [Opción elegida]  
**Razón:** [Por qué se eligió]
```

---

## Historial de Decisiones

| Fecha | Decisión | Elegido |
|-------|----------|---------|
| - | - | - |