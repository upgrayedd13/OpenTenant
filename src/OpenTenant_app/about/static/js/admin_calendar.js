import { initCalendar } from "./calendar_core.js";

const calendarEl = document.getElementById("calendar");
const monthLabel = document.getElementById("monthLabel");
const adminMain = document.querySelector(".admin-main");
const eventPane = document.getElementById("eventPane");
const eventPaneDate = document.getElementById("eventPaneDate");
const eventForm = document.getElementById("eventForm");
const eventPaneClose = document.getElementById("eventPaneClose");
const eventTitle = document.getElementById("eventTitle");

let selectedDateStr = null;
let selectedCell = null;

function openPanel(dateStr, cell) {
    // Deselect previous cell
    if (selectedCell) selectedCell.classList.remove("selected");

    selectedDateStr = dateStr;
    selectedCell = cell;
    cell.classList.add("selected");

    // Format date nicely for the panel header
    const [year, month, day] = dateStr.split("-").map(Number);
    const label = new Date(year, month - 1, day).toLocaleDateString("default", {
        weekday: "long", month: "long", day: "numeric"
    });
    eventPaneDate.textContent = label;

    eventForm.reset();
    adminMain.classList.add("panel-open");
    setTimeout(() => eventTitle.focus(), 350);
}

function closePanel() {
    if (selectedCell && selectedCell.isConnected) {
        selectedCell.classList.remove("selected");
    }
    selectedCell = null;
    selectedDateStr = null;
    adminMain.classList.remove("panel-open");
}

eventPaneClose.onclick = closePanel;

eventForm.onsubmit = (e) => {
    e.preventDefault();
    if (!selectedDateStr) return;

    const title = eventTitle.value.trim();
    const time = document.getElementById("eventTime").value;
    const description = document.getElementById("eventDesc").value.trim();
    if (!title) return;

    fetch("/api/calendar/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, date: selectedDateStr, time, description })
    })
    .then(async res => {
        const data = await res.json();
        if (!res.ok) throw new Error(data.error);
        closePanel();
        renderCalendar();
    })
    .catch(err => alert(err.message || "Failed to create event"));
};

const { renderCalendar, getCurrent } = initCalendar(calendarEl, monthLabel, {
    onDayClick: (dateStr, cell, renderCalendar) => openPanel(dateStr, cell)
});

document.getElementById("prev").onclick = () => {
    getCurrent().setMonth(getCurrent().getMonth() - 1);
    closePanel();
    renderCalendar();
};
document.getElementById("next").onclick = () => {
    getCurrent().setMonth(getCurrent().getMonth() + 1);
    closePanel();
    renderCalendar();
};

renderCalendar();