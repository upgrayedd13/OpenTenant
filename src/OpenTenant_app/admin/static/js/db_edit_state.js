export const state = {  // NOTE: const in JS only prevents reassignment and doesn't actually mean immutable...
    activeTable: null,
    originalData: {},
    editedCells: new Set(),
    pendingChanges: {},
    prevPending: 0,
    typeData: {},
};

export function hasPendingChanges() {
    return Object.values(state.pendingChanges)
        .flatMap(t => Object.values(t))
        .flatMap(r => Object.values(r)).length > 0
}