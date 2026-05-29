import { escHtml } from './db_edit_utils.js';
import { state }   from './db_edit_state.js';


const tooltip = document.getElementById('cell-tooltip');

let hoveredInput = null;

export function initTooltip() {
    const panelBody = document.getElementById('panel-body');

    panelBody.addEventListener('mouseover', (e) => {
        const input = e.target.closest('.cell-input');
        hoveredInput = input ?? null;
        if (input) showTooltip(e);
    });

    panelBody.addEventListener('input', (e) => {
        const input = e.target.closest('.cell-input');
        if (input && input === hoveredInput) {
            showTooltip(e);
        }
    });

    panelBody.addEventListener('mousemove', (e) => {
        tooltip.style.left = `${e.clientX + 12}px`;
        tooltip.style.top  = `${e.clientY + 12}px`;
    });

    panelBody.addEventListener('mouseout', () => {
        hoveredInput = null;
        tooltip.style.display = 'none';
    });
}

function showTooltip(e) {
    const input = e.target.closest('.cell-input');
    if (!input) {
        return;
    }

    const id = parseInt(input.dataset.id);
    const col = input.dataset.col;
    const info = state.columnInfo[state.activeTable]?.[col];
    const original = String(state.originalData[id]?.[col] ?? '');
    const isChanged = input.value !== original;

    const lines = [
        { text: `type: ${info?.type ?? 'unknown'}`, class: '' },
        { text: `nullable: ${info?.nullable ?? '?'}`, class: '' },
        info?.primary_key ? { text: 'primary key', class: '' } : null,
        info?.foreign_keys?.length ? { text: `-> ${info.foreign_keys.join(', ')}`, class: '' } : null,
        info?.default != null ? { text: `default: ${info.default}`, class: '' } : null,
        { text: `original: ${original}`, class: isChanged ? 'tooltip-original changed' : 'tooltip-original' },
    ].filter(Boolean);

    tooltip.innerHTML = lines.map(line =>
        `<div class="${line.class}">${escHtml(line.text)}</div>`
    ).join('');

    tooltip.style.display = 'block';
}
