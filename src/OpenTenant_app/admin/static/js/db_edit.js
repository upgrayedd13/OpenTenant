const TABLES_ENDPOINT = '/api/db/tables';
const TABLE_DATA_ENDPOINT = (name) => `/api/db/table/${name}`;

let activeTable = null;
let originalData = [];
let editedCells = new Set();
let pendingChanges = {};
let prevPending = 0;
let typeData = {};
let sqlHistory = [];
let sqlHistoryIndex = -1;

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

function renderTableList(tableNames) {
    const list = document.getElementById('table-list');

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

// ── Fetch table contents ─────────────────────────────────────
async function fetchTableData(tableName) {
    const res = await fetch(TABLE_DATA_ENDPOINT(tableName));
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(`HTTP ${res.status}: ${errBody.error ?? 'Unknown error'}`)
    }

    // get the JSON data from the response
    const data = await res.json();

    // save off the type data
    typeData[tableName] = data.types;

    // return the row data
    return data.rows;
}

// ── Render editable table ─────────────────────────────────────
function renderTable(rows) {
    originalData = Object.fromEntries(rows.map(r => [parseInt(r.id), { ...r }]));
    editedCells.clear();
    const body = document.getElementById('panel-body');

    if (!rows.length) {
        body.innerHTML = '<div class="state-msg"><span>This table is empty</span></div>';
        return;
    }

    // draw the table
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

    // reapply any pending changes for this table
    const tablePending = pendingChanges[activeTable];
    if (tablePending) {
        document.querySelectorAll('.cell-input').forEach(inp => {
            const id = parseInt(inp.dataset.id);
            const col = inp.dataset.col;
            if (tablePending[id]?.[col] !== undefined) {
                inp.value = tablePending[id][col];
                inp.classList.add('modified');
                editedCells.add(`${id}:${col}`);
            }
        });
    }

    document.getElementById('edit-actions').style.display = editedCells.size > 0 ? 'flex' : 'none';
}

// ── Cell edit tracking ────────────────────────────────────────
function onCellInput(input, id, col) {
    const original = String(originalData[id][col] ?? '');
    const key = `${id}:${col}`;

    if (!pendingChanges[activeTable]) {
        pendingChanges[activeTable] = {};
    }

    if (!pendingChanges[activeTable][id]) {
        pendingChanges[activeTable][id] = {};
    }

    if (input.value !== original) {
        input.classList.add('modified');
        editedCells.add(key);
        pendingChanges[activeTable][id][col] = input.value;
    } else {
        input.classList.remove('modified');
        editedCells.delete(key);
        delete pendingChanges[activeTable][id][col];
    }

    const totalPending = Object.values(pendingChanges)
        .flatMap(t => Object.values(t))
        .flatMap(r => Object.values(r)).length;

    document.getElementById('commit-btn').disabled = totalPending === 0;
    document.getElementById('edit-actions').style.display = editedCells.size > 0 ? 'flex' : 'none';

    if (totalPending != prevPending) {
        setStatus(`${totalPending} uncommitted change(s)`);
    }
    prevPending = totalPending;
}

async function commitAll() {
    if (!Object.keys(pendingChanges).length) {
        return;
    }

    try {
        const res = await fetch(TABLES_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ changes: pendingChanges }),
        });

        const data = await res.json();
        if (!res.ok) {
            setStatus(data.error, 'error');
            return;
        }

        // at this point, we know the commit worked, so we need to re-fetch the data to sync our copies
        document.querySelectorAll('.cell-input.modified').forEach(inp => {
            const id = parseInt(inp.dataset.id);
            originalData[id][inp.dataset.col] = inp.value;
            inp.classList.remove('modified');
        });

        setStatus(`Committed changes to ${Object.keys(pendingChanges).length} table(s)`, 'success');
        pendingChanges = {};
        prevPending = 0;
        document.getElementById('commit-btn').disabled = true;
        document.querySelectorAll('.cell-input.modified').forEach(el => el.classList.remove('modified'));
        editedCells.clear();
        document.getElementById('edit-actions').style.display = 'none';
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

// ── Discard ───────────────────────────────────────────────────
function discardChanges() {
    document.querySelectorAll('.cell-input.modified').forEach(inp => {
        const id = parseInt(inp.dataset.id);
        inp.value = String(originalData[id][inp.dataset.col] ?? '');
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
    if (!query) {
        return;
    }

    // Add to history, avoiding consecutive duplicates
    if (sqlHistory[sqlHistory.length - 1] !== query) {
        sqlHistory.push(query);
    }
    sqlHistoryIndex = sqlHistory.length;

    setStatus(query, 'command');
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
            return;
        }

        if (data.rows.length > 0) {
            activeTable = '__query__';
            document.getElementById('panel-title').textContent = 'Query Result';
            typeData['__query__'] = data.types;
            renderTable(data.rows);
            setStatus(`${data.rows.length} row(s) returned`, 'success');
        } else {
            setStatus('Query OK', 'success');
            // Re-fetch the active table if one is open, since a write may have changed it
            if (activeTable && activeTable !== '__query__') {
                const rows = await fetchTableData(activeTable);
                renderTable(rows);
            }
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

document.getElementById('panel-body').addEventListener('input', (e) => {
    const input = e.target.closest('.cell-input');
    if (!input) {
        return;
    }

    onCellInput(input, parseInt(input.dataset.id), input.dataset.col);
});

const tooltip = document.getElementById('cell-tooltip');
document.getElementById('panel-body').addEventListener('mouseover', (e) => {
    const input = e.target.closest('.cell-input');
    if (!input) {
        return;
    }

    const id = parseInt(input.dataset.id);
    const col = input.dataset.col;
    const type = typeData[activeTable]?.[col] ?? 'unknown';
    const original = String(originalData[id]?.[col] ?? '');
    const isChanged = input.classList.contains('modified');

    tooltip.innerHTML = `
        <div class="tooltip-type">type: ${escHtml(type)}</div>
        <div class="tooltip-original ${isChanged ? 'changed' : ''}">
            original: ${escHtml(original)}
        </div>
    `;
    tooltip.style.display = 'block';
});

document.getElementById('panel-body').addEventListener('mousemove', (e) => {
    tooltip.style.left = `${e.clientX + 12}px`;
    tooltip.style.top  = `${e.clientY + 12}px`;
});

document.getElementById('panel-body').addEventListener('mouseout', (e) => {
    const input = e.target.closest('.cell-input');
    if (!input) {
        return;
    }
    tooltip.style.display = 'none';
});

document.getElementById('sql-input').addEventListener('keydown', (e) => {
    const input = e.target;

    if (e.key === 'Enter') {
        runSql();
        return;
    }

    if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (sqlHistoryIndex > 0) {
            sqlHistoryIndex--;
            input.value = sqlHistory[sqlHistoryIndex];
        }
        return;
    }

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (sqlHistoryIndex < sqlHistory.length - 1) {
            sqlHistoryIndex++;
            input.value = sqlHistory[sqlHistoryIndex];
        } else {
            sqlHistoryIndex = sqlHistory.length;
            input.value = '';
        }
        return;
    }

    if (e.key === 'Tab') {
        e.preventDefault();
        const val = input.value.trimStart();
        const words = val.split(/\s+/);
        const lastWord = words[words.length - 1].toUpperCase();
        if (!lastWord) return;

        // Build completion candidates from SQL keywords + known table/column names
        const keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE',
            'SET', 'DELETE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON',
            'AND', 'OR', 'NOT', 'NULL', 'IS', 'IN', 'LIKE', 'BETWEEN', 'ORDER',
            'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'DISTINCT', 'AS',
            'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'COUNT', 'SUM', 'AVG',
            'MIN', 'MAX',
        ];
        const tableNames = [...document.querySelectorAll('.table-item')].map(el => el.dataset.table.toUpperCase());
        const colNames = Object.keys(typeData[activeTable] ?? {}).map(c => c.toUpperCase());
        const candidates = [...new Set([...keywords, ...tableNames, ...colNames])];

        const matches = candidates.filter(c => c.startsWith(lastWord));
        if (matches.length === 1) {
            // Unambiguous — complete it
            words[words.length - 1] = matches[0];
            input.value = words.join(' ') + ' ';
        } else if (matches.length > 1) {
            // Show options in the log
            setStatus(`Completions: ${matches.join(', ')}`, 'info');

            // Fill in the longest common prefix
            const prefix = matches.reduce((a, b) => {
                let i = 0;
                while (i < a.length && a[i] === b[i]) i++;
                return a.slice(0, i);
            });
            if (prefix.length > lastWord.length) {
                words[words.length - 1] = prefix;
                input.value = words.join(' ');
            }
        }
        return;
    }
});

// TODO: still getting layout issues from type="module"