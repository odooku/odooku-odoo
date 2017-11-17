Odooku Odoo
===========

**DISCLAIMER: All files packaged by this application are Copyright (c) 2004-2017 Odoo S.A. Original LICENSE and COPYRIGHT file is included. The purpose of these packages is to provide an easy and reliable installation method for Odoo.**

[![Build Status](https://travis-ci.org/odooku/odooku-odoo.svg?branch=11.0)](https://travis-ci.org/odooku/odooku-odoo)

## Installation

```
pip install odooku-odoo-addons
```

This will install the full Odoo suite. If you want to keep installation and dependency size to a minimal, feel free to install the seperate packages like so:

```
pip install odooku-odoo-[app]
```

Available options are:

- mail
- account_invoicing
- board
- calendar
- contacts
- crm
- fleet
- hr
- hr_attendance
- hr_expense
- hr_holidays
- hr_recruitment
- project
- hr_timesheet
- im_livechat
- lunch
- maintenance
- mass_mailing
- stock
- mrp
- sale_management
- mrp_repair
- note
- point_of_sale
- purchase
- website
- survey
- website_blog
- website_event
- website_forum
- website_sale
- website_slides
- extra
- addons

## Build requirements

While the Odoo source code does not require any distribution libraries, it's dependencies do. In order for them to build successfully follow instructions below:

#### Ubuntu 16.04 LTS
```
sudo apt-get install libpq-dev libxml2-dev libxslt1-dev libldap2-dev libsasl2-dev libssl-dev
```

#### OSX
```
brew install postgresql
```

## External dependencies

At runtime Odoo will always require the LESSC compiler, and most likely wkhtmltopdf.

#### lessc
This package does not install the LESSC compiler for you.

#### wkhtmltopdf
This package does not install the wkhtmltopdf binary for you.

## Update policy

Tags under the release branch are published to pypi periodically. The source for these builds are found at [the Odoo github repository](https://github.com/odoo/odoo). A commit is pinned and tested, while the version number is simply bumped. 

#### Frequency
Due to the large size of these packages, pypi pushes will be done once every month. If you require more frequent updates, concider running the setup script manually or using your own pypi server. 

#### Version format
[ODOO_VERSION].[BUMP] For Odoo 11 the version format will be 11.0.[BUMP]

## Using the setup script

#### Install directly 

Running the setup.py script through pip will install the full Odoo suite:

```
[ODOO_VERSION=] [ODOO_URL=] pip install .
```

In order to install seperate features run like so:

```
FEATURE=<feature> pip install .
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
pip install --find-links file://$(pwd)/dist odooku-odoo-<feature>
```

#### Installing without all languages

Specify a comma seperated set of languages will reduce the install size 
even further.

```
[LANGUAGES=] pip install .
```