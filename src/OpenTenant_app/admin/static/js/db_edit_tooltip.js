import { escHtml } from './db_edit_utils.js';
import { state }   from './db_edit_state.js';


export function initTooltip() {
    const tooltip = document.getElementById('cell-tooltip');
    const panelBody = document.getElementById('panel-body');

    panelBody.addEventListener('mouseover', (e) => {
        const input = e.target.closest('.cell-input');
        if (!input) return;

        const id = parseInt(input.dataset.id);
        const col = input.dataset.col;
        const type = state.typeData[state.activeTable]?.[col] ?? 'unknown';
        const original = String(state.originalData[id]?.[col] ?? '');
        const isChanged = input.classList.contains('modified');

        tooltip.innerHTML = `
            <div class="tooltip-type">type: ${escHtml(type)}</div>
            <div class="tooltip-original ${isChanged ? 'changed' : ''}">
                original: ${escHtml(original)}
            </div>
        `;
        tooltip.style.display = 'block';
    });

    panelBody.addEventListener('mousemove', (e) => {
        tooltip.style.left = `${e.clientX + 12}px`;
        tooltip.style.top  = `${e.clientY + 12}px`;
    });

    panelBody.addEventListener('mouseout', (e) => {
        tooltip.style.display = 'none';
    });
}
