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

# Hosting
The following is a list of thoughts on what setup would need to be performed on an OS hosting our applications.

## VPS Requirements
  * Ubuntu Server 24.04 LTS
  * 2 vCPUs
  * 2 GB RAM
  * 100 GB SSD
    * Plenty of space for bulk storage and OS
    * Could probably also use less if money is tight
  * Only port 443 exposed

## Flask-based website hosted on VPS
  * Support for at most 360 users
    * Assuming low concurrancy
  * Exposes basic file utility for bulk file storage for admin users (board members)
    * Using this method for bulk storage instead of SMB/SFTP for simplicity and security
  * Apps will run as non-root user
  * Will need to install/configure:
    * [Nginx](https://nginx.org/en/)
      * Handles HTTPS requests
      * Serves static files
      * Reverse proxy to app
    * [Gunicorn](https://gunicorn.org/)
      * WSGI server
      * Runs Flask app
    * [UV](https://docs.astral.sh/uv/)
      * Python package manager
    * systemd
      * Keeps app running
      * Auto-restarts on crash
    * UFW
      * Firewall
      * Only allows connection to ports 443 and SSH port
      * WILL NOT USE PORT 22 FOR SSH
    * [Fail2Ban](https://github.com/fail2ban/fail2ban)
      * Intrusion prevention
    * [Certbot](https://certbot.eff.org/)
      * Handles certificates for Nginx/HTTPS
    * Bulk storage backup
    * SMTP relay
      * Handles outgoing email from app

## Email Hosting
  * Probably want to use a standalone email hoster
    * This is because of email spam filtering/trust/etc.
  * Could use [Proton](https://proton.me/mail) or [Zoho](https://www.zoho.com/) Mail

# TODO
These TODOs aren't presented in any particular order.
- [x] Initialize SQL database
- [ ] Write a bill parser
- [ ] Add info from parsed bills into database
- [ ] Fill in placeholder text with actual info
- [ ] Determine what "Legal BS" should actually go in the [footer](src/OpenTenant_app/templates/layout/_footer.html) and update it
- [ ] Replace stock photos with ones the union takes
- [ ] Create data visualization widget from info in DB in [Admin page](src/OpenTenant_app/templates/pages/admin.html)
- [ ] Pretty up frontend
- [ ] Add in multilanguage support with [flask_babel](https://python-babel.github.io/flask-babel/index.html)
- [ ] Pull actual account data from DB when user logs in
- [ ] Fix broken "Remember me" login and Login -> Account tab with JS
- [ ] Make submit button on Register page actually save info to DB and make a user account
- [ ] Change from password auth to 2FA (bug Kyle about this?)
- [ ] Add support for different user account types (admin vs normal user)
- [ ] Make [Admin page](src/OpenTenant_app/templates/pages/admin.html) only visible when an admin is logged in
- [ ] Create property map widget based on Weidner's [Interactive Leasing](https://www.lpmapartments.com/floor-plans) page
- [ ] Create spider that checks for empty apartments once a day and updates DB
- [ ] Replace [About page](src/OpenTenant_app/templates/pages/about.html) with drop-down menu of several pages (there's going to be too much info there for one page) (probably should rename "About"  too)
- [ ] Add sub-page under [About](src/OpenTenant_app/templates/pages/about.html) for legal help, rights, etc.
- [ ] Add sub-page under [About](src/OpenTenant_app/templates/pages/about.html) for who we are, what we stand for, bylaws, etc.
- [ ] Add sub-page under [About](src/OpenTenant_app/templates/pages/about.html) for union calendar
- [ ] Add a less-intense way to create an account (i.e. for those who don't feel comfortable uploading a lease)
- [ ] Make [Report a Bug](src/OpenTenant_app/templates/pages/bug_report.html) page actually send an email to *someone*
- [ ] Actually host the damn thing on a VPS
- [ ] Create an actual OS image for said VPS host (should be minimal, but secure)
- [ ] Make a way to approve user accounts in [Admin page](src/OpenTenant_app/templates/pages/admin.html)
- [ ] Clean up the beast of a [CSS file](src/OpenTenant_app/static/css/style.css)
- [ ] Reorder Python code to make use of blueprints/routes instead of everything being in [app.py](src/OpenTenant_app/app.py)
- [ ] Perform some type of hardening