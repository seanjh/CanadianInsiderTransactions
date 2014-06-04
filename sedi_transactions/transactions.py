import sys
import time
import requests
import lxml.html
from random import randrange


class SEDIView:
    """SEDIView objects provide a persistent requests session. When the SEDIView
    object is first instantiated, 2 sedi.ca user-facing entry pages will be
    visited. These 2 preliminary page requests are required in order to acquire
    form data embedded on these pages that is required by the server in order
    to fetch transaction view results.

    The SEDIView object wrapped using the with clause, as follows:
        with SEDIView() as sedi:
            html, encoding = sedi.get_transactions_view(issuer_number)
    """
    DEBUG = False
    DEFAULT_MIN_PAUSE = 90
    DEFAULT_MAX_PAUSE = 450
    ISSUER_SEARCH_URL = ('https://www.sedi.ca/sedi/'
                         'SVTIIBIselectIssuer?locale=en_CA')
    ISSUER_RESULT_URL = ('https://www.sedi.ca/sedi/'
                         'SVTIIBIviewResults?locale=en_CA')

    def __init__(self,
                 min_pause=DEFAULT_MIN_PAUSE,
                 max_pause=DEFAULT_MAX_PAUSE):
        self._session = requests.Session()
        self._base_form_data = {}
        self._base_response = None
        self.min_pause = min_pause
        self.max_pause = max_pause
        self._prepare_session()
        self._encoding = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    @property
    def encoding(self):
        return self._encoding

    def get_transactions_view(self, number):
        """Returns the sedi.ca transactions view HTML plaintext for the
        specified issuer number.

        :return:
            html or
            None when no results are available
        """
        self._set_search_number(number)

        # Submit the Issuer Number search
        print(("\tRequest Issuer Number {0} "
               "results: {1}").format(number, SEDIView.ISSUER_SEARCH_URL))
        response = self._session.post(SEDIView.ISSUER_SEARCH_URL,
                                      data=self._base_form_data)

        SEDIView.write_html(response, 'temp.html')

        if not self._is_error_page(response):
            form_data = self._get_form_data(response)
            self._tidy_results_form(form_data, number)

            self.hold_up()

            #TODO: remove redundancy here?
            self._tidy_session_headers()

            # Request View transactions
            print(("\tRequest Issuer Number {0} View Results: "
                   "{1}").format(number, SEDIView.ISSUER_RESULT_URL))
            response = self._session.post(SEDIView.ISSUER_RESULT_URL,
                                          data=form_data)
            SEDIView.write_html(response, 'temp.html')

            print(("Found transactions for Issuer Number {0}.").format(number))
            return response.text
        else:
            print(("No transactions available for "
                   "Issuer Number {0}!").format(number))
            return None

    def _set_search_number(self, number):
        # Inject the Issuer number search value
        self._base_form_data['ISSUER_SEARCH_VALUE'] = number

    def _update_synchronizer_token(self, form_data):
        if (self._base_form_data.get('jspSynchronizerToken') and
                form_data.get('jspSynchronizerToken')):
            self._base_form_data['jspSynchronizerToken'] = (
                form_data.get('jspSynchronizerToken')
            )

    def _prepare_session(self):
        """Requests 2 user-facing entry pages. This sets up the required
        form_data required by the server for each individual search request.
        """

        # Request page for Insider information by issuer
        print(("\tRequest page for Insider "
               "information by issuer: {0}").format(SEDIView.ISSUER_SEARCH_URL))
        response = self._session.get(SEDIView.ISSUER_SEARCH_URL)
        form_data = self._get_form_data(response)
        form_data['ISSUER_SEARCH_CRITERIA_SELECT_BOX'] = '7'
        form_data['ISSUER_SEARCH_TYPE'] = '3'
        form_data['pageName'] = 'resubmit'

        self._encoding = response.encoding

        self.hold_up()

        # Request Issuer Number search page
        print(("\tRequest Issuer Number "
               "search page: {0}").format(SEDIView.ISSUER_SEARCH_URL))
        self._base_response = self._session.post(SEDIView.ISSUER_SEARCH_URL,
                                                 data=form_data)
        self._base_form_data = self._get_form_data(self._base_response)

    def _get_form_data(self, response):
        tree = lxml.html.fromstring(response.text)
        hidden_form = self._get_hidden_inputs(tree)
        input_form = self._get_inputs(tree)
        return dict(hidden_form + input_form)

    @staticmethod
    def _get_hidden_inputs(tree):
        hidden = [(e.name, e.value) for e in
                  tree.xpath('//input[@type="hidden"]')]
        hidden_caps = [(e.name, e.value) for e in
                       tree.xpath('//input[@type="HIDDEN"]')]
        return hidden + hidden_caps

    @staticmethod
    def _get_inputs(tree):
        has_selected = [(e.name, e.value) for e in
                        tree.xpath('//select') if e.value]
        no_selected = [(e.name, None) for e in
                       tree.xpath('//select') if not e.value]
        text_inputs = [(e.name, e.value) for e in
                       tree.xpath('//input[@type="text"]')]
        return has_selected + no_selected + text_inputs

    @staticmethod
    def _tidy_results_form(form_data, number):
        """These POST parameters are all required in order to receive a valid
        response from the sedi.ca server.
        """
        if not form_data.get('FROM_MONTH'):
            form_data['FROM_MONTH'] = None
        if not form_data.get('FROM_DAY'):
            form_data['FROM_DAY'] = None
        if not form_data.get('ALPHA_RANGE_FROM'):
            form_data['ALPHA_RANGE_FROM'] = None
        if not form_data.get('ALPHA_RANGE_TO'):
            form_data['ALPHA_RANGE_TO'] = None
        if not form_data.get('ATTRIB_DRILL_ID'):
            form_data['ATTRIB_DRILL_ID'] = number
        if not form_data.get('ATTRIB_DRILL_ID2'):
            form_data['ATTRIB_DRILL_ID2'] = number
        if form_data.get('ISSUER_SEARCH_TYPE'):
            form_data['ISSUER_SEARCH_TYPE'] = '2'

    def _tidy_session_headers(self):
        """These headers are all required in order to
        """
        self._session.headers['Accept'] = ('text/html,application/xhtml+xml,'
                                           'application/xml;q=0.9,image/webp,'
                                           '*/*;q=0.8')
        self._session.headers['Accept-Encoding'] = 'gzip,deflate,sdch'
        self._session.headers['Accept-Language'] = 'en-US,en;q=0.8'
        self._session.headers['Referer'] = ('https://www.sedi.ca/sedi/'
                                            'SVTIIBIselectIssuer?locale=en_CA')

    @staticmethod
    def _is_error_page(response):
        """Error pages indicate that the transaction view does not exist for the
        provided issuer number.
        """
        tree = lxml.html.fromstring(response.text)
        rows = tree.xpath('//tr')
        return [
            e for e in rows
            if 'error' in
            (''.join(e.xpath('.//text()'))).lower()
        ]

    def hold_up(self):
        if SEDIView.DEBUG:
            sleep_time = randrange(self.min_pause, self.max_pause)
            sys.stdout.write('\rSleeping (t-{0} seconds)\t'.format(sleep_time))
            sys.stdout.flush()
            while sleep_time:
                time.sleep(1)
                sleep_time -= 1
                sys.stdout.write(('\rSleeping (t-{0} '
                                  'seconds)\t').format(sleep_time))
                sys.stdout.flush()
            sys.stdout.write('\n')
        else:
            resp = input("Press and key to continue (X to exit): ")
            if resp.lower() == 'x':
                'Exiting'
                exit(0)

    @staticmethod
    def write_html(response, filename):
        with open(filename, 'w', encoding=response.encoding) as outfile:
            outfile.write(response.text)

    @staticmethod
    def write_form_data(data, filename):
        with open(filename, 'w') as outfile:
            outfile.write(str(data))
