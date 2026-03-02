---
trigger: always_on
---

# 🔧 Principios de Simplicidad

Reglas duras de código que NO se negocian.

--- 

## Código Directo

- ❌ **Sin try-catch redundantes** - Solo manejar errores críticos
- ❌ **Sin abstracciones innecesarias** - No crear clases para todo
- ❌ **Sin sobreingeniería** - Resolver el problema actual, no el futuro
- ✅ **Código legible** - Si necesita comentario extenso, simplificar

### Ejemplo Correcto
```javascript
// Obtiene flashcard por ID
function getFlashcard(id) {
  logSequence('Buscando flashcard', id)
  return flashcards.find(f => f.id === id)
}
```

### Ejemplo Incorrecto
```javascript
// Demasiadas abstracciones innecesarias
class FlashcardRepository {
  constructor(dataSource) {
    this.dataSource = dataSource
  }
  
  async findById(id) {
    try {
      const result = await this.dataSource.query(...)
      if (!result) throw new NotFoundError(...)
      return new FlashcardEntity(result)
    } catch (error) {
      throw new RepositoryError(error)
    }
  }
}
```

---

## Archivos Pequeños

- **Una responsabilidad por archivo**
- **Máximo ~100-150 líneas** por archivo
- Si crece más → dividir en archivos más pequeños

### Estructura de Carpetas
```
src/components/
├── flashcard.js          # Componente de flashcard
├── flashcard.css         # Estilos de flashcard
├── flashcardList.js      # Lista de flashcards
└── flashcardList.css     # Estilos de lista
```

---

## Documentación Mínima

- ✅ **Un comentario breve por función** - Solo el propósito
- ❌ **No documentar lo obvio** - El código debe ser autoexplicativo
- ❌ **No JSDoc extenso** - Solo si es API pública

### Ejemplo
```javascript
// Guarda flashcard en localStorage
function saveFlashcard(flashcard) {
  // ... código simple
}
```

---

## Manejo de Errores Simple

Solo para errores **críticos** que el usuario debe ver:

```javascript
function loadData() {
  const data = localStorage.getItem('flashcards')
  
  if (!data) {
    logWarn('No hay datos guardados')
    return []  // Retornar valor por defecto, no lanzar error
  }
  
  return JSON.parse(data)
}
```