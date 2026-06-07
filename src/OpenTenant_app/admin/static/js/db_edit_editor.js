import { state, hasPendingChanges, updateButtons } from './db_edit_state.js';
import { updateTableListHighlights }               from './db_edit_table.js';
import { TABLES_ENDPOINT }                         from './db_endpoints.js';
import { setStatus }                               from './db_edit_utils.js';


export function initEditor() {
    document.getElementById('discard-btn').addEventListener('click', discardChanges);
    document.getElementById('discard-all-btn').addEventListener('click', discardAllChanges);
    document.getElementById('commit-btn').addEventListener('click', commitCurrent);
    document.getElementById('commit-all-btn').addEventListener('click', commitAll);

    document.getElementById('panel-body').addEventListener('input', (e) => {
        const input = e.target.closest('.cell-input');
        if (!input) {
            return;
        }

        onCellInput(input, parseInt(input.dataset.id), input.dataset.col);
    });
}

function onCellInput(input, id, col) {
    const original = String(state.originalData[id][col] ?? '');
    const key = `${id}:${col}`;

    // ensure there's an entry for this table
    state.pendingChanges[state.activeTable] ??= {};

    // ensure there's an entry for this ID
    state.pendingChanges[state.activeTable][id] ??= {};

    if (input.value !== original) {
        input.classList.add('modified');
        state.editedCells.add(key);
        state.pendingChanges[state.activeTable][id][col] = input.value
    } else {
        input.classList.remove('modified');
        state.editedCells.delete(key)
        delete state.pendingChanges[state.activeTable][id][col];
    }

    const totalPending = Object.values(state.pendingChanges)
        .flatMap(t => Object.values(t))
        .flatMap(r => Object.values(r)).length;

    updateButtons();

    if (totalPending !== state.prevPending) {
        setStatus(`${totalPending} uncommitted change(s)`);
    }
    state.prevPending = totalPending;
    updateTableListHighlights();
}

async function commitCurrent() {
    if (state.editedCells.size === 0) {
        return;
    }

    const tableChanges = state.pendingChanges[state.activeTable];
    if (!tableChanges) {
        return;
    }

    try {
        const res = await fetch(TABLES_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ changes: { [state.activeTable]: tableChanges } }),
        });

        const data = await res.json();
        if (!res.ok) {
            setStatus(data.error, 'error');
            return;
        }

        // Sync originalData to the committed values
        document.querySelectorAll('.cell-input.modified').forEach(inp => {
            const id = parseInt(inp.dataset.id);
            state.originalData[id][inp.dataset.col] = inp.value;
            inp.classList.remove('modified');
        });

        delete state.pendingChanges[state.activeTable];
        state.editedCells.clear();
        updateButtons();
        updateTableListHighlights();
        setStatus(`Committed changes to ${state.activeTable}`, 'success');
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

async function commitAll() {
    if (!hasPendingChanges()) {
        return;
    }

    try {
        const res = await fetch(TABLES_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ changes: state.pendingChanges }),
        });

        const data = await res.json();
        if (!res.ok) {
            setStatus(data.error, 'error');
            return;
        }

        // Sync originalData to the committed values
        document.querySelectorAll('.cell-input.modified').forEach(inp => {
            const id = parseInt(inp.dataset.id);
            state.originalData[id][inp.dataset.col] = inp.value;
            inp.classList.remove('modified');
        });

        setStatus(`Committed changes to ${Object.keys(state.pendingChanges).length} table(s)`, 'success');
        state.pendingChanges = {};
        state.prevPending = 0;
        state.editedCells.clear();
        updateButtons();
        updateTableListHighlights();
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

function discardChanges() {
    document.querySelectorAll('.cell-input.modified').forEach(inp => {
        const id = parseInt(inp.dataset.id);
        inp.value = String(state.originalData[id][inp.dataset.col] ?? '');
        inp.classList.remove('modified');
    });

    state.editedCells.clear();
    delete state.pendingChanges[state.activeTable];
    updateButtons();
    updateTableListHighlights();
    setStatus('Changes discarded');
}

function discardAllChanges() {
    if (!hasPendingChanges()) return;

    // Reset all modified inputs in the current view
    document.querySelectorAll('.cell-input.modified').forEach(inp => {
        const id = parseInt(inp.dataset.id);
        inp.value = String(state.originalData[id][inp.dataset.col] ?? '');
        inp.classList.remove('modified');
    });

    state.pendingChanges = {};
    state.editedCells.clear();
    state.prevPending = 0;
    updateButtons();
    updateTableListHighlights();
    setStatus('All changes discarded');
}
