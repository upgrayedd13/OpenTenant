export function escHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

export function setStatus(msg, type = 'info') {
    const log = document.getElementById('message-log');
    const entry = document.createElement('div');

    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    log.appendChild(entry);
    log.scrollTop = log.scrollHeight;  // auto-scroll to bottom
}
