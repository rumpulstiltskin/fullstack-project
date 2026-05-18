# Frontend — Existing Code Description

## Overview

A pure client-side demo of the Kanban board UI. No backend, no authentication, no persistence. All state lives in React component state and resets on page refresh. This is the starting point for Parts 3–10 of the project plan.

## Tech stack

- Next.js 16 (React 19, TypeScript)
- Tailwind CSS v4
- @dnd-kit/core + @dnd-kit/sortable — drag and drop
- clsx — conditional className utility
- Vitest + @testing-library/react — unit tests
- Playwright — E2E tests
- Google Fonts: Space Grotesk (display/headings), Manrope (body)

## File structure

```
frontend/
  src/
    app/
      layout.tsx         Root layout: loads fonts, sets metadata, wraps children in <html>/<body>
      page.tsx           Entry point: renders <KanbanBoard /> with no auth guard (yet)
      globals.css        CSS custom properties (design tokens) + Tailwind import + base body styles
    components/
      KanbanBoard.tsx    Top-level board component; owns all state; renders columns via DndContext
      KanbanColumn.tsx   Single column; droppable target; renders its cards via SortableContext
      KanbanCard.tsx     Single card; sortable drag handle; shows title, details, and a delete button
      KanbanCardPreview.tsx  Ghost card shown in the DragOverlay while a card is being dragged
      NewCardForm.tsx    Inline form (toggled by "Add a card" button) for creating a new card
    lib/
      kanban.ts          Data types, initial demo data, moveCard logic, createId utility
      kanban.test.ts     Unit tests for moveCard
    test/
      setup.ts           Vitest setup file (imports @testing-library/jest-dom matchers)
      vitest.d.ts        Type augmentation for Vitest globals
  tests/
    kanban.spec.ts       Playwright E2E tests (board load, add card, drag card)
```

## Data model (src/lib/kanban.ts)

```typescript
type Card = { id: string; title: string; details: string }
type Column = { id: string; title: string; cardIds: string[] }
type BoardData = { columns: Column[]; cards: Record<string, Card> }
```

Columns hold ordered card IDs; cards are stored in a flat lookup map. This mirrors what the backend API will return.

The five fixed columns are: Backlog, Discovery, In Progress, Review, Done.

## State management

All board state lives in a single `useState<BoardData>` inside `KanbanBoard`. Mutations are handled by four callbacks passed down as props:

- `handleRenameColumn(columnId, title)` — updates column title
- `handleAddCard(columnId, title, details)` — creates a card with `createId("card")` and appends it to the column
- `handleDeleteCard(columnId, cardId)` — removes the card from both the column's `cardIds` and the cards map
- `handleDragEnd(event)` — calls `moveCard(columns, activeId, overId)` from `kanban.ts`

All mutations return new objects (immutable pattern).

## Drag and drop

Uses @dnd-kit. `DndContext` wraps the whole board. Each `KanbanColumn` is a `useDroppable` target. Each `KanbanCard` is `useSortable`. A `DragOverlay` renders `KanbanCardPreview` while dragging. Collision detection uses `closestCorners`. The `PointerSensor` requires a 6px drag before activation (prevents accidental drags on click).

## Design system

CSS custom properties defined in `globals.css`:

```
--accent-yellow:    #ecad0a
--primary-blue:     #209dd7
--secondary-purple: #753991
--navy-dark:        #032147
--gray-text:        #888888
--surface:          #f7f8fb
--surface-strong:   #ffffff
--stroke:           rgba(3, 33, 71, 0.08)
--shadow:           0 18px 40px rgba(3, 33, 71, 0.12)
```

Use these variables for all new UI. Do not introduce new hardcoded color values.

## Test setup

**Unit tests** — `vitest run` or `npm run test:unit`. Config in `vitest.config.ts`. Setup file at `src/test/setup.ts` imports `@testing-library/jest-dom`. Uses `jsdom` as the environment.

**E2E tests** — `playwright test` or `npm run test:e2e`. Config in `playwright.config.ts`. Currently targets `http://localhost:3000` (will be updated to `http://localhost:8000` in Part 3).

**test:all** — runs both suites in sequence.

## What is not yet implemented

- No authentication or auth guard — the board renders for any visitor
- No backend API calls — `initialData` in `kanban.ts` is used directly
- No persistence — state resets on refresh
- No AI sidebar — to be added in Part 10
- The Next.js config does not yet set `output: 'export'` — required for static serving from FastAPI (Part 3)

## Key things to preserve when making changes

- All state mutations must remain immutable (return new objects, never mutate)
- Keep the five columns; their IDs (`col-backlog`, `col-discovery`, `col-progress`, `col-review`, `col-done`) are referenced in tests
- Card `data-testid` values follow the pattern `card-{id}`; column `data-testid` values follow `column-{id}` — E2E tests depend on these
- The `KanbanBoard` component must remain a `"use client"` component
