# Open Tenant
OpenTenant is an app that helps tenants track problems with their management company through the tracking and data analysis of bills and building issues.

# Getting Started
* Install [UV](https://docs.astral.sh/uv/getting-started/installation/)
* Create a Python virtual environment with `uv venv`
  * This is not strictly speaking necessary, but is still highly recommended
* Install Python dependencies with `uv sync`
* Setup environment variables by running `cp .env.example .env` and editing `.env`
  * **Do not commit `.env`!!!**

# Running Open Tenant
The easiest way to start the web app is to run `./run.sh`. More methods for running the app may come in the future.

# TODO
- [ ] Write a bill parser
- [ ] Initialize SQL database
- [ ] Add info from parsed bills into database
- [ ] Data visualization from info in DB
- [ ] Pretty up frontend
