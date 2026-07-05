import { initCalendar } from "./calendar_core.js";

const calendarEl = document.getElementById("calendar");
const monthLabel = document.getElementById("monthLabel");
let current = new Date();

const { renderCalendar, getCurrent } = initCalendar(calendarEl, monthLabel);

document.getElementById("prev").onclick = () => {
    getCurrent().setMonth(getCurrent().getMonth() - 1);
    renderCalendar();
};

document.getElementById("next").onclick = () => {
    getCurrent().setMonth(getCurrent().getMonth() + 1);
    renderCalendar();
};

renderCalendar();