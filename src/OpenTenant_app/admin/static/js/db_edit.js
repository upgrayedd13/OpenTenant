const TABLES_ENDPOINT = '/api/db/tables';
const TABLE_DATA_ENDPOINT = (name) => `/api/db/table/${name}`;

let activeTable = null;
let originalData = [];
let editedCells = new Set();
let pendingChanges = {};
let prevPending = 0;

// ── Fetch table list ──────────────────────────────────────────
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
        setStatus(`${Object.keys(data.tables).length} table(s) found`);
    } catch (err) {
        list.innerHTML = `<div class="error-msg">Error: ${err.message}</div>`;
        setStatus('Failed to load tables');
    }
}

function renderTableList(tables) {
    const list = document.getElementById('table-list');
    const tableNames = Object.keys(tables);

    if (tableNames.length === 0) {
        list.innerHTML = '<div class="state-msg" style="height:80px;">No tables found</div>';
        return;
    }

    list.innerHTML = tableNames
        .map(t => `<div class="table-item${activeTable === t ? ' active' : ''}" data-table="${t}">${t}</div>`)
        .join('');
}

// ── Select & load a table ─────────────────────────────────────
async function selectTable(name) {
    if (activeTable === name) {
        return;
    }

    activeTable = name;
    editedCells.clear();

    document.querySelectorAll('.table-item').forEach(el => {
        el.classList.toggle('active', el.textContent === name);
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

// ── Fetch table contents ─────────────────────────────────────
async function fetchTableData(tableName) {
    const res = await fetch(TABLE_DATA_ENDPOINT(tableName));
    if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.json().error}`);
    }

    const data = await res.json();
    return data.rows;
}

// ── Render editable table ─────────────────────────────────────
function renderTable(rows) {
    originalData = rows.map(r => ({ ...r }));
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
                    data-row="${ri}"
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
}

// ── Cell edit tracking ────────────────────────────────────────
function onCellInput(input, rowIdx, col) {
    const original = String(originalData[rowIdx][col] ?? '');
    const key = `${rowIdx}:${col}`;

    if (!pendingChanges[activeTable]) {
        pendingChanges[activeTable] = {};
    }

    if (!pendingChanges[activeTable][rowIdx]) {
        pendingChanges[activeTable][rowIdx] = {};
    }

    if (input.value !== original) {
        input.classList.add('modified');
        editedCells.add(key);
        pendingChanges[activeTable][rowIdx][col] = input.value;
    } else {
        input.classList.remove('modified');
        editedCells.delete(key);
        delete pendingChanges[activeTable][rowIdx][col];
    }

    const totalPending = Object.values(pendingChanges)
        .flatMap(t => Object.values(t))
        .flatMap(r => Object.values(r)).length;

    document.getElementById('commit-btn').disabled = totalPending === 0;
    document.getElementById('edit-actions').style.display = editedCells.size > 0 ? 'flex' : 'none';

    if (totalPending > 0 && totalPending != prevPending) {
        setStatus(`${totalPending} uncommitted change(s)`);
    }
    prevPending = totalPending;
}

// ── Save ──────────────────────────────────────────────────────
async function saveChanges() {
    const inputs = document.querySelectorAll('.cell-input.modified');
    const changes = [];

    inputs.forEach(inp => {
        const ri = parseInt(inp.dataset.row);
        const col = inp.dataset.col;
        changes.push({
        row: ri,
        col,
        oldValue: originalData[ri][col],
        newValue: inp.value,
        });
        originalData[ri][col] = inp.value;
        inp.classList.remove('modified');
    });

    editedCells.clear();
    document.getElementById('edit-actions').style.display = 'none';

    // TODO: send changes to your backend
    //
    // await fetch(`/api/table/${activeTable}/update`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(changes),
    // });

    console.log('Changes saved (stub):', changes);
    setStatus(`Saved ${changes.length} change(s)`);
}

async function commitAll() {
    if (!Object.keys(pendingChanges).length) return;

    try {
        const res = await fetch('/api/db/commit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ changes: pendingChanges }),
        });
        const data = await res.json();
        if (!res.ok) {
            setStatus(data.error, 'error');
        } else {
            setStatus(`Committed changes to ${Object.keys(pendingChanges).length} table(s)`, 'success');
            pendingChanges = {};
            document.getElementById('commit-btn').disabled = true;
            document.querySelectorAll('.cell-input.modified').forEach(el => el.classList.remove('modified'));
            editedCells.clear();
            document.getElementById('edit-actions').style.display = 'none';
        }
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

// ── Discard ───────────────────────────────────────────────────
function discardChanges() {
    document.querySelectorAll('.cell-input.modified').forEach(inp => {
        const ri = parseInt(inp.dataset.row);
        inp.value = String(originalData[ri][inp.dataset.col] ?? '');
        inp.classList.remove('modified');
    });

    editedCells.clear();
    delete pendingChanges[activeTable];
    document.getElementById('edit-actions').style.display = 'none';
    document.getElementById('commit-btn').disabled = Object.keys(pendingChanges).length === 0;
    setStatus('Changes discarded');
}

// ── Helpers ───────────────────────────────────────────────────
function setStatus(msg, type = 'info') {
    const log = document.getElementById('message-log');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;  // auto-scroll to bottom
}

async function runSql() {
    const input = document.getElementById('sql-input');
    const query = input.value.trim();
    if (!query) return;

    setStatus(query);
    input.value = '';

    try {
        const res = await fetch('/api/db/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
        });
        const data = await res.json();
        if (!res.ok) {
            setStatus(data.error, 'error');
        } else {
            setStatus(`${data.rows.length} row(s) returned`, 'success');
            // optionally render results in the main panel:
            renderTable(data.rows);
        }
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

function escHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

// ── Init ──────────────────────────────────────────────────────
fetchTables();
document.getElementById('refresh-btn').addEventListener('click', fetchTables);
document.getElementById('discard-btn').addEventListener('click', discardChanges);
document.getElementById('commit-btn').addEventListener('click', commitAll);
document.getElementById('table-list').addEventListener('click', (e) => {
    const item = e.target.closest('.table-item');
    if (item) {
        selectTable(item.dataset.table);
    }
});

document.getElementById('sql-run-btn').addEventListener('click', runSql);
document.getElementById('sql-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        runSql();
    }
});

document.getElementById('panel-body').addEventListener('input', (e) => {
    const input = e.target.closest('.cell-input');
    if (!input) return;
    const rowIdx = parseInt(input.dataset.row);
    const col = input.dataset.col;
    onCellInput(input, rowIdx, col);
});

// TODO: still getting layout issues from type="module"