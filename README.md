# Canadian Insider Transactions
## Overview
This application is intended for use as a user-driven command-line based browser of transaction view pages from sedi.ca. An explicit list of issuer numbers must be provided to the application. Each input issuer number corresponds to a user-driven search. This user-driven approach is explicitly intended to prevent an automated scrape or crawl over the site content en masse, which is prohibited by the sedi.ca Terms of Use. In other words, this application is intended to provide an alternative guided method for browsing Canadian Insider Transaction data from sedi.ca. See the SEDI Terms of Use for more details.

* https://www.sedi.ca/sedi/disclaimer_en.html

## Usage
        $ python sedi_transactions <issuer_num>...
    
    Options:
        -h --help     Show this screen.
        --version     Show version.

The resulting HTML (if any) will be downloaded to the /output directory beneath the application's root directory.
