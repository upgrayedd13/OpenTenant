
const ENDPOINT_BASE = '/api/db'

const TABLES_ENDPOINT = `${ENDPOINT_BASE}/tables`;
const TABLE_DATA_ENDPOINT = (name) => `${ENDPOINT_BASE}/table/${name}`;
const EXPORT_ENDPOINT = (name) => `${ENDPOINT_BASE}/export/${name}`;

export { TABLES_ENDPOINT, TABLE_DATA_ENDPOINT, EXPORT_ENDPOINT };