import { fetchTableData, renderTable } from './db_edit_table.js';
import { setStatus }                   from './db_edit_utils.js';
import { state }                       from './db_edit_state.js';

let sqlHistory = [];
let sqlHistoryIndex = -1;

export function initConsole() {
    document.getElementById('sql-run-btn').addEventListener('click', runSql);
    initConsoleKeyboard();
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
            state.activeTable = '__query__';
            document.getElementById('panel-title').textContent = 'Query Result';
            state.typeData['__query__'] = data.types;
            renderTable(data.rows);
            setStatus(`${data.rows.length} row(s) returned`, 'success');
        } else {
            setStatus('Query OK', 'success');
            // Re-fetch the active table if one is open, since a write may have changed it
            if (state.activeTable && state.activeTable !== '__query__') {
                const rows = await fetchTableData(state.activeTable);
                renderTable(rows);
            }
        }
    } catch (err) {
        setStatus(err.message, 'error');
    }
}

function initConsoleKeyboard() {
    const input = document.getElementById('sql-input');

    input.addEventListener('keydown', (e) => {
        switch (e.key) {
            case 'Enter':
                runSql();
                break;

            case 'ArrowUp':
                e.preventDefault();
                if (sqlHistoryIndex > 0) {
                    sqlHistoryIndex--;
                    input.value = sqlHistory[sqlHistoryIndex];
                }
                break;

            case 'ArrowDown':
                e.preventDefault();
                if (sqlHistoryIndex < sqlHistory.length - 1) {
                    sqlHistoryIndex++;
                    input.value = sqlHistory[sqlHistoryIndex];
                } else {
                    sqlHistoryIndex = sqlHistory.length;
                    input.value = '';
                }
                break;

            case 'Tab':
                e.preventDefault();
                handleTabComplete(input);
                break;
        }
    });
}

function handleTabComplete(input) {
    const val = input.value.trimStart();
    const words = val.split(/\s+/);
    const lastWord = words[words.length - 1].toUpperCase();

    if (!lastWord) {
        return;
    }

    const keywords = [
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE',
        'SET', 'DELETE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON',
        'AND', 'OR', 'NOT', 'NULL', 'IS', 'IN', 'LIKE', 'BETWEEN', 'ORDER',
        'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'DISTINCT', 'AS',
        'CREATE', 'DROP', 'ALTER', 'TABLE', 'INDEX', 'COUNT', 'SUM', 'AVG',
        'MIN', 'MAX',
    ];
    const tableNames = [...document.querySelectorAll('.table-item')].map(el => el.dataset.table.toUpperCase());
    const colNames = Object.values(state.typeData)
        .flatMap(t => Object.keys(t))
        .map(c => c.toUpperCase());
    const candidates = [...new Set([...keywords, ...tableNames, ...colNames])];
    const matches = candidates.filter(c => c.startsWith(lastWord));

    if (matches.length === 1) {
        words[words.length - 1] = matches[0];
        input.value = words.join(' ') + ' ';
    } else if (matches.length > 1) {
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
}
