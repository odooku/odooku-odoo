Odooku Odoo
===========

**DISCLAIMER:  All files packaged by this application are Copyright (c) 2004-2017 Odoo S.A. Original LICENSE and COPYRIGHT file is included. The purpose of these packages is to provide an easy and reliable installation method for Odoo. **


## Installation

```
pip install odooku-odoo-addons
```

This will install the full Odoo suite. If you want to keep installation and dependency size to a minimal, feel free to install the seperate packages like so:

```
pip install odooku-odoo-[app]
```

Available options are:

 - account
 - account_accountant
 - board
 - calendar
 - contacts
 - crm
 - **extra: ** This package provides point of sale hardware modules and a few test modules.
 - fleet 
 - hr 
 - hr_attendance 
 - hr_expense
 - hr_holidays
 - hr_recruitment
 - hr_timesheet
 - im_livechat
 - l10n_fr_certification
 - lunch
 - mail
 - maintenance
 - mass_mailing
 - mrp
 - mrp_repair
 - note
 - point_of_sale
 - project
 - project_issue
 - purchase
 - sale
 - stock
 - survey
 - website
 - website_blog
 - website_event
 - website_forum
 - website_sale
 - website_slides

## Build requirements

#### Ubuntu 16.04 LTS
```
sudo apt-get install libpq-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libssl-dev
```

#### OSX
```
brew install postgresql
```

## LESSC

This package does not install the LESSC compiler for you.

## WKHTMLTOPDF

#### Ubuntu 16.04 LTS

This package does not install the wkhtmltopdf binary for you.

## Using the setup script manually

#### Install directly 

Running the setup.py script through pip will install the full Odoo suite:

```
[ODOO_VERSION=] [ODOO_URL=] pip install .
```

In order to install seperate features run like so:

```
FEATURE=<desired feature> pip install .
```

This will always require the 'base' feature. In order to install the 'account'
app you should run:

```
FEATURE=base pip install .
FEATURE=mail pip install .
FEATURE=account pip install .
```

The best method to locally install is to use the 'bdist_wheel' helper script.
This will generate wheels for all features. Which you can then install using
automatic dependency resolving:

```
./bdist_wheel.bash
pip install --find-links file://$(pwd)/dist odooku-odoo-feature
```

#### Installing without all languages

Specify a comma seperated set of languages will reduce the install size 
even further.

```
[LANGUAGES=] pip install .
```