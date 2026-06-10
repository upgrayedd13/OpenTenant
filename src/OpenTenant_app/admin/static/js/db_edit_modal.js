import { hasPendingChanges } from './db_edit_state.js';

const overlay  = document.getElementById('overlay');
const titleEl  = document.getElementById('modalTitle');
const contentEl = document.getElementById('modalContent');
const closeBtn = document.getElementById('closeModal');

let modalClosed = false;
let navigatingAway = false;

export function initModal() {
    modalWarning();

    closeBtn.addEventListener('click', closeModal);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.classList.contains('active')) {
            closeModal();
        }
    });

    window.addEventListener('beforeunload', (e) => {
        if (!navigatingAway && hasPendingChanges()) {
            e.preventDefault();
        }
    });

    document.addEventListener('click', popupConfirmationModal);
}

function closeModal() {
    overlay.classList.remove('active');
    modalClosed = true;
}

function showConfirmModal(title, message, onConfirm) {
    titleEl.textContent = title;
    contentEl.innerHTML = `
        <p>${message}</p>
        <div style="display:flex;gap:8px;margin-top:16px;">
            <button id="modal-stay-btn" class="btn">Stay</button>
            <button id="modal-leave-btn" class="btn btn-primary">Leave anyway</button>
        </div>
    `;
    overlay.classList.add('active');

    document.getElementById('modal-stay-btn').addEventListener('click', closeModal);
    document.getElementById('modal-leave-btn').addEventListener('click', () => {
        closeModal();
        onConfirm();
    });
}

async function modalWarning() {
    if (modalClosed) {
        return;
    }

    titleEl.textContent = 'Read before continuing!';
    contentEl.innerHTML = 'Loading...';
    overlay.classList.add('active');

    try {
        const response = await fetch('/modal/db_edit_notice');
        if (!response.ok) {
            throw new Error('Failed to load');
        }

        contentEl.innerHTML = await response.text();
    } catch {
        contentEl.innerHTML = '<p>Error loading content.</p>';
    }
}

function popupConfirmationModal(e) {
    const link = e.target.closest('a[href]');
    if (!link || !hasPendingChanges()) {
        return;
    }

    e.preventDefault();
    showConfirmModal(
        'Uncommitted changes',
        'You have uncommitted changes that will be lost if you navigate away.',
        () => {
            navigatingAway = true;
            window.location.href = link.href;
        }
    );
}
