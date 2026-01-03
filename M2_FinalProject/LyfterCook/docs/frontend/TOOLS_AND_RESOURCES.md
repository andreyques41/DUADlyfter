# Frontend Development Tools & Resources

> **Propósito**: Esta guía te ayudará a crear wireframes, especificaciones de páginas, y encontrar referencias de diseño para comunicarte mejor con el agente frontend.

---

## 📐 Herramientas de Wireframing (Gratis)

### 1. **Excalidraw** ⭐ RECOMENDADO
- **URL**: https://excalidraw.com
- **Ventaja**: Gratuito, sin registro, colaborativo
- **Uso**: Dibujos rápidos tipo sketch para layouts
- **Cómo usar**:
  1. Abre https://excalidraw.com
  2. Dibuja cajas para representar componentes
  3. Agrega texto para etiquetar
  4. Exporta como PNG o comparte link

**Ejemplo de uso para LyfterCook**:
```
Dibuja:
- Rectángulo grande = página completa
- Rectángulo con "Navbar" arriba
- Cuadrícula de rectángulos = tarjetas de platillos
- Botón = "Add Dish"
```

---

### 2. **Figma** (Opción Profesional)
- **URL**: https://www.figma.com
- **Ventaja**: Herramienta profesional, gratis para uso personal
- **Uso**: Diseños detallados con colores, tipografía, componentes reutilizables
- **Cómo usar**:
  1. Crea cuenta gratuita
  2. Usa plantillas de UI kits (busca "Dashboard Template")
  3. Duplica y modifica para LyfterCook
  4. Comparte link con "View Only"

**Templates útiles**:
- [Dashboard UI Kit](https://www.figma.com/community/file/1234567890/dashboard-ui-kit)
- [Restaurant Admin Panel](https://www.figma.com/community/search?q=restaurant%20admin)

---

### 3. **Balsamiq Cloud** (Trial Gratis)
- **URL**: https://balsamiq.cloud
- **Ventaja**: Estilo sketch paper, rápido para prototipos
- **Uso**: Wireframes de baja fidelidad
- **Costo**: 30 días gratis, luego $9/mes

---

### 4. **Draw.io** (Alternativa Simple)
- **URL**: https://app.diagrams.net
- **Ventaja**: Gratis, sin registro, muchas formas predefinidas
- **Uso**: Wireframes básicos con formas geométricas

---

### 5. **Papel y Lápiz** (Serio) ✏️
- **Ventaja**: Más rápido que cualquier herramienta digital
- **Uso**: Sketch inicial antes de digitalizar
- **Cómo compartir**: Toma foto con celular → sube a chat

---

## 🎨 Referencias de Diseño

### Dashboard Inspiration

#### 1. **Stripe Dashboard**
- **URL**: https://dashboard.stripe.com (necesitas cuenta demo)
- **Qué copiar**: Layout limpio, navegación lateral, tablas elegantes
- **Screenshot**: https://i.imgur.com/stripe-dashboard.png

#### 2. **Notion Database**
- **URL**: https://www.notion.so
- **Qué copiar**: Modales de formularios, filtros, vistas de tabla vs. tarjeta

#### 3. **Airtable**
- **URL**: https://www.airtable.com
- **Qué copiar**: Tablas editables, drag-and-drop, filtros avanzados

#### 4. **Airbnb Host Dashboard**
- **URL**: https://www.airbnb.com/hosting (necesitas cuenta)
- **Qué copiar**: Calendario de reservas, cards de propiedades

---

### Component Libraries (Para Referencias Visuales)

#### 1. **TailwindUI Components**
- **URL**: https://tailwindui.com/components
- **Gratis**: Ejemplos de código HTML/CSS para copiar
- **Categorías útiles**:
  - Tables
  - Forms
  - Modals
  - Cards
  - Navigation

#### 2. **Flowbite Components**
- **URL**: https://flowbite.com/docs/components/
- **Gratis**: Todos los componentes con código
- **Ventaja**: Basado en TailwindCSS, fácil de integrar

#### 3. **DaisyUI**
- **URL**: https://daisyui.com/components/
- **Gratis**: Componentes Tailwind con clases predefinidas
- **Ventaja**: Menos código CSS custom

---

## 📝 Workflow Recomendado

### Paso 1: Sketch Rápido (5 minutos)
1. Abre Excalidraw o toma papel
2. Dibuja layout básico:
   - Navbar arriba
   - Sidebar a la izquierda (si aplica)
   - Área principal de contenido
   - Ubicación de botones principales
3. Toma screenshot o foto

**Ejemplo para "Clients Page"**:
```
+------------------+
| [Logo] Clients   |  ← Navbar
+-----+------------+
|     | Search Bar |
| S   | [+ Add]    |
| i   +------------+
| d   | TABLE:     |
| e   | Name Email |
| b   | John john@ |
| a   | Jane jane@ |
| r   +------------+
|     | Pagination |
+-----+------------+
```

---

### Paso 2: Lista de Componentes (10 minutos)
Anota todos los elementos interactivos:

**Ejemplo**:
- Search bar (text input)
- "+ Add Client" button (opens modal)
- Table with 4 columns
- Edit icon per row (opens modal)
- Delete icon per row (shows confirmation)
- Pagination controls (prev/next/numbers)

---

### Paso 3: Encuentra Referencia Similar (5 minutos)
Busca en Google Images o referencias:

**Búsquedas útiles**:
- "admin dashboard client management"
- "restaurant admin panel"
- "CRM table view"
- "dashboard modal form"

Guarda 2-3 imágenes que te gusten.

---

### Paso 4: Especifica Comportamiento (15 minutos)
Usa el template `PAGE_SPECIFICATION_TEMPLATE.md` y llena:
- Sección 7: User Interactions (qué pasa cuando hago click)
- Sección 8: Error Handling (qué pasa si falla)
- Sección 9: Loading States (qué muestra mientras carga)

---

### Paso 5: Comunica al Agente
En el chat, proporciona:

1. **Link al sketch**: "Aquí está el wireframe: [link a Excalidraw]"
2. **Referencias**: "Quiero algo como esta tabla de Stripe: [screenshot]"
3. **Especificaciones**: "Revisa `docs/frontend/CLIENTS_PAGE_SPEC.md` para detalles"

---

## 🖼️ Ejemplos de Comunicación Efectiva

### ❌ Comunicación Vaga
> "Necesito una página de clientes con una tabla"

**Problema**: El agente no sabe:
- ¿Qué columnas tiene la tabla?
- ¿Hay búsqueda o filtros?
- ¿Cómo se agregan clientes?

---

### ✅ Comunicación Clara
> "Necesito la página de clientes. Aquí está el sketch: [link]. 
> Debe tener:
> - Tabla con columnas: Name, Email, Phone, Actions
> - Search bar arriba a la izquierda
> - Botón '+ Add Client' arriba a la derecha (abre modal)
> - Paginación abajo (20 clientes por página)
> - Referencia visual: tabla estilo Stripe (adjunto screenshot)
> - Especificación completa en `docs/frontend/CLIENTS_PAGE_SPEC.md`"

**Ventaja**: El agente puede empezar a programar inmediatamente.

---

## 🎯 Priorización de Páginas

### Orden Recomendado (de más simple a más complejo)

1. **Login Page** (más simple)
   - 2 inputs (email, password)
   - 1 botón
   - Sin estado complejo

2. **Register Page**
   - Similar a login + selector de rol

3. **Clients Page**
   - CRUD básico
   - Tabla simple
   - Buen punto de partida

4. **Dishes Page**
   - CRUD con imágenes
   - Cards en lugar de tabla
   - Introduce upload de archivos

5. **Menus Page**
   - Asignación de platillos (relación muchos a muchos)
   - Multi-select

6. **Quotations Page**
   - Formulario complejo
   - Cálculos dinámicos
   - Generación de PDF

7. **Appointments Page** (más complejo)
   - Integración de calendario
   - Librería externa
   - Drag-and-drop (opcional)

---

## 📚 Recursos de Aprendizaje

### CSS & Design
- **Every Layout**: https://every-layout.dev (patrones de layout)
- **CSS Tricks**: https://css-tricks.com (snippets útiles)
- **Can I Use**: https://caniuse.com (compatibilidad de navegadores)

### JavaScript
- **MDN Web Docs**: https://developer.mozilla.org/en-US/docs/Web/JavaScript
- **JavaScript.info**: https://javascript.info (guía completa de ES6+)

### Vanilla JS Examples
- **TodoMVC**: https://todomvc.com/examples/vanillajs/ (arquitectura de ejemplo)
- **You Might Not Need jQuery**: https://youmightnotneedjquery.com

---

## 🔧 Setup de Herramientas (Opcional)

### VS Code Extensions
- **Live Server**: Preview en tiempo real
- **Prettier**: Formateo automático de código
- **ESLint**: Detección de errores JS
- **HTML CSS Support**: Autocompletado

### Browser DevTools
- **Chrome DevTools**: Inspeccionar elementos, debugger JS
- **Firefox Developer Edition**: Mejor para CSS Grid/Flexbox
- **Lighthouse**: Auditoría de performance y accesibilidad

---

## 📋 Checklist Antes de Pedir Nueva Página

Antes de pedirle al agente que construya una página, asegúrate de tener:

- [ ] Sketch o wireframe (puede ser papel + foto)
- [ ] Lista de componentes y sus interacciones
- [ ] Al menos 1 referencia visual similar
- [ ] Endpoints de API documentados (revisa `docs/api/API_DOCUMENTATION.md`)
- [ ] Decisión sobre layout (tabla vs. cards vs. lista)
- [ ] ¿Qué pasa cuando está vacío? (empty state)
- [ ] ¿Qué pasa mientras carga? (loading state)
- [ ] ¿Qué pasa si falla? (error state)

---

## 🎓 Ejemplo Completo: "Clients Page"

### 1. Sketch en Excalidraw
![Client Page Wireframe](https://excalidraw.com/#json=abc123...)

### 2. Lista de Componentes
- Navbar (header)
- Search bar (text input con debounce)
- "+ Add Client" button (abre modal)
- Client table (4 columnas, sortable)
- Edit button (pencil icon, abre modal con datos pre-llenados)
- Delete button (trash icon, muestra confirmación)
- Pagination (prev/next + números de página)

### 3. Referencias Visuales
- Tabla: Similar a Stripe Customers (screenshot adjunto)
- Modal: Similar a Notion form (screenshot adjunto)

### 4. Especificación
Ver archivo completo: [`docs/frontend/CLIENTS_PAGE_SPEC.md`](PAGE_SPECIFICATION_TEMPLATE.md)

### 5. Comunicación al Agente
```
@workspace Como frontend agent, construye la página de Clients.

Aquí está el plan:
- Wireframe: https://excalidraw.com/#json=...
- Referencias: [adjunto 2 screenshots]
- Especificación completa: docs/frontend/CLIENTS_PAGE_SPEC.md
- API endpoints ya implementados (ver docs/api/API_DOCUMENTATION.md líneas 400-450)

Prioriza funcionalidad sobre diseño bonito. Empezaremos con tabla HTML simple + CSS básico.
```

---

## 💡 Tips Pro

1. **Usa placeholders realistas**: En lugar de "Lorem ipsum", usa datos reales:
   - Nombres: John Doe, Jane Smith
   - Emails: john.doe@example.com
   - Precios: $12.99, $24.50

2. **Piensa en casos extremos**:
   - ¿Qué pasa con nombres muy largos?
   - ¿Y si hay 0 resultados?
   - ¿Y si hay 10,000 clientes?

3. **Documenta decisiones**: Anota por qué elegiste una opción:
   - "Elegí cards en lugar de tabla porque las imágenes se ven mejor"
   - "No incluí búsqueda avanzada para simplificar MVP"

4. **Itera**: No necesitas especificar todo perfectamente desde el inicio. Construye, prueba, ajusta.

---

**¿Preguntas?** Actualiza este documento con herramientas que descubras.
