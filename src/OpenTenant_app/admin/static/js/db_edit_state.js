import { EXPORT_ENDPOINT } from "./db_endpoints.js";

export const state = {  // NOTE: const in JS only prevents reassignment and doesn't actually mean immutable...
    activeTable: null,
    originalData: {},
    editedCells: new Set(),
    pendingChanges: {},
    prevPending: 0,
    typeData: {},
    columnInfo: {},
    constraints: {},
};

export function hasPendingChanges() {
    return Object.values(state.pendingChanges)
        .flatMap(t => Object.values(t))
        .flatMap(r => Object.values(r)).length > 0
}

export function updateButtons() {
    const hasLocal = state.editedCells.size > 0;
    const hasAny = hasPendingChanges();
    document.getElementById('discard-btn').classList.toggle('visible', hasLocal);
    document.getElementById('discard-all-btn').classList.toggle('visible', hasAny);
    document.getElementById('commit-btn').disabled = !hasLocal;
    document.getElementById('commit-all-btn').disabled = !hasAny;
    document.getElementById('export-csv-btn').disabled = false;
    if (state.activeTable !== null) {
        document.getElementById('export-csv-btn').href = EXPORT_ENDPOINT(state.activeTable);
    }
}