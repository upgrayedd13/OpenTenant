import { initConsole }       from './db_edit_console.js';
import { initTooltip }       from './db_edit_tooltip.js';
import { initEditor }        from './db_edit_editor.js';
import { initTables }        from './db_edit_table.js';
import { initModal }         from './db_edit_modal.js';

// Connect the various listeners and pop up initial warning modal
initTables();
initEditor();
initConsole();
initTooltip();
initModal();


// TODO: still getting layout issues from type="module"