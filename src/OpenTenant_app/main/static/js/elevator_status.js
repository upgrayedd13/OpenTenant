const API_URL = '/api/elevator/status';
const REFRESH_INTERVAL = 60000;

let refreshTimeout;

async function fetchElevatorStatus() {
    try {
        const response = await fetch(API_URL);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const elevators = await response.json();
        renderElevators(elevators);
    } catch (error) {
        console.error('Failed to fetch elevator status:', error);
        showError();
    }
}

function renderElevators(elevators) {
    const container = document.getElementById('elevators');
    
    if (elevators.length === 0) {
        container.innerHTML = '<div class="loading">No elevators configured</div>';
        return;
    }
    
    container.innerHTML = elevators.map(elevator => createElevatorCard(elevator)).join('');
}

function createElevatorCard(elevator) {
    const statusClass = elevator.status.toLowerCase().replace(' ', '-');
    const statusText = elevator.status.replace('-', ' ').toUpperCase();
    const comment = elevator.comment?.trim() || '<span class="no-comment">No additional information</span>';
    
    let timestampHtml = '';
    if (elevator.last_updated) {
        const lastUpdated = new Date(elevator.last_updated).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit'
        });
        timestampHtml = `
            <div class="timestamp-section">
                <span class="timestamp-label">Last updated:</span>
                <span class="timestamp-text">${lastUpdated}</span>
            </div>
        `;
    }
    
    return `
        <div class="elevator-card" data-car="${elevator.car_number}">
            <div class="elevator-card-header">
                <span class="elevator-number">
                    <span class="elevator-number-label">Car</span>
                    ${elevator.car_number}
                </span>
                <span class="status-indicator ${statusClass}">${statusText}</span>
            </div>
            <div class="status-text ${statusClass}">${statusText}</div>
            <div class="comment-section">
                <span class="comment-label">Note:</span>
                <div class="comment-text">${comment}</div>
            </div>
            ${timestampHtml}
        </div>
    `;
}

function showError() {
    const container = document.getElementById('elevators');
    container.innerHTML = '<div class="loading">Unable to load elevator status. Please try again later.</div>';
}

function startAutoRefresh() {
    if (refreshTimeout) {
        clearTimeout(refreshTimeout);
    }
    
    refreshTimeout = setTimeout(() => {
        fetchElevatorStatus();
        startAutoRefresh();
    }, REFRESH_INTERVAL);
}

document.addEventListener('DOMContentLoaded', () => {
    fetchElevatorStatus();
    startAutoRefresh();
});
