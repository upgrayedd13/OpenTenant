import { escHtml, setStatus } from './db_edit_utils.js';
import { state }              from './db_edit_state.js';

const TABLES_ENDPOINT = '/api/db/tables';
const TABLE_DATA_ENDPOINT = (name) => `/api/db/table/${name}`;

export { TABLES_ENDPOINT, TABLE_DATA_ENDPOINT };

export function initTables() {
    fetchTables();

    document.getElementById('refresh-btn').addEventListener('click', fetchTables);

    document.getElementById('table-list').addEventListener('click', (e) => {
        const item = e.target.closest('.table-item');
        if (item) {
            selectTable(item.dataset.table);
        }
    });
}

export async function fetchTableData(tableName) {
    const res = await fetch(TABLE_DATA_ENDPOINT(tableName));
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(`HTTP ${res.status}: ${err.error ?? 'Unknown error'}`);
    }

    const data = await res.json();
    state.typeData[tableName] = data.types;
    state.columnInfo[tableName] = data.columns;
    state.constraints[tableName] = data.constraints;
    return data.rows;
}

export function renderTable(rows) {
    state.originalData = Object.fromEntries(rows.map(r => [parseInt(r.id), { ...r }]));
    state.editedCells.clear();

    const body = document.getElementById('panel-body');

    if (!rows.length) {
        body.innerHTML = '<div class="state-msg"><span>This table is empty</span></div>';
        return;
    }

    const cols = Object.keys(rows[0]);
    body.innerHTML = `
        <table class="data-table">
        <thead>
            <tr>${cols.map(c => `<th>${c}</th>`).join('')}</tr>
        </thead>
        <tbody>
            ${rows.map((row, ri) => `
            <tr>
                ${cols.map(col => `
                <td>
                    <input
                        class="cell-input"
                        data-id="${row.id}"
                        data-col="${col}"
                        value="${escHtml(String(row[col] ?? ''))}"
                        aria-label="${col}, row ${ri + 1}"
                    />
                </td>
                `).join('')}
            </tr>
            `).join('')}
        </tbody>
        </table>
    `;

    // Reapply any pending changes for this table
    const tablePending = state.pendingChanges[state.activeTable];
    if (tablePending) {
        document.querySelectorAll('.cell-input').forEach(inp => {
            const id = parseInt(inp.dataset.id);
            const col = inp.dataset.col;
            if (tablePending[id]?.[col] !== undefined) {
                inp.value = tablePending[id][col];
                inp.classList.add('modified');
                state.editedCells.add(`${id}:${col}`);
            }
        });
    }

    document.getElementById('edit-actions').style.display = state.editedCells.size > 0 ? 'flex' : 'none';
}

async function fetchTables() {
    const list = document.getElementById('table-list');
    list.innerHTML = '<div class="state-msg" style="height:80px;">Loading...</div>';
    setStatus('Fetching tables...');

    try {
        const res = await fetch(TABLES_ENDPOINT);
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        renderTableList(data.tables);
        setStatus(`${data.tables.length} table(s) found`);
    } catch (err) {
        list.innerHTML = `<div class="error-msg">Error: ${err.message}</div>`;
        setStatus('Failed to load tables');
    }
}

function renderTableList(tableNames) {
    const list = document.getElementById('table-list');

    if (tableNames.length === 0) {
        list.innerHTML = '<div class="state-msg" style="height:80px;">No tables found</div>';
        return;
    }

    list.innerHTML = tableNames
        .map(t => `<div class="table-item${state.activeTable === t ? ' active' : ''}" data-table="${t}">${t}</div>`)
        .join('');
}

async function selectTable(name) {
    if (state.activeTable === name) {
        return;
    }

    state.activeTable = name;

    document.querySelectorAll('.table-item').forEach(el => {
        el.classList.toggle('active', el.dataset.table === name);
    });

    document.getElementById('panel-title').textContent = name;
    document.getElementById('edit-actions').style.display = 'none';
    document.getElementById('panel-body').innerHTML = '<div class="state-msg"><span>Loading...</span></div>';
    setStatus(`Loading ${name}...`);

    try {
        const rows = await fetchTableData(name);
        renderTable(rows);
        setStatus(`${rows.length} row(s) — click any cell to edit`);
    } catch (err) {
        document.getElementById('panel-body').innerHTML = `<div class="error-msg">Error: ${err.message}</div>`;
        setStatus(`Failed to load table data for table ${name}`);
    }
}
