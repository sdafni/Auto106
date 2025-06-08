from unittest import TestCase

from app.proc import process_file_content
from app import state

class Test(TestCase):

    def test_via_digital(self):
        PDF_PATH = "../forms/via_digital/form_106_pdf_689124_20250406_131744.pdf"
        with open(PDF_PATH, 'rb') as pdf_file:
            process_file_content( pdf_file.read(), PDF_PATH, "106", "main", None)
            non_zero_results = {k: v for k, v in state.results.items() if v != 0}

        expected =  {'042': 110926,
                     '158': 352366,
                     '244': 210267,
                     '248': 30407,
                     '045': 12616}

        self.assertEqual(expected, non_zero_results)

    def test_via_digital_no_llm(self):
        PDF_PATH = "../forms/via_digital/form_106_pdf_689124_20250406_131744.pdf"
        with open(PDF_PATH, 'rb') as pdf_file:
            process_file_content( pdf_file.read(), PDF_PATH, "106", "main", None, use_local_extract=True)
            non_zero_results = {k: v for k, v in state.results.items() if v != 0}

        expected =  {'042': 110926,
                     '158': 352366,
                     '244': 210267,
                     '248': 30407,
                     '045': 12616}

        self.assertEqual(expected, non_zero_results)

    def test_dagshub_ocr_old(self):

        PDF_PATH = "../forms/dagshub_ocr_old/non_pass_031168701_T106.pdf"
        with open(PDF_PATH, 'rb') as pdf_file:
            process_file_content( pdf_file.read(), PDF_PATH, "106", "main", None)
            non_zero_results = {k: v for k, v in state.results.items() if v != 0}

        expected =  {'042': 14049,
                     '158': 60432,
                     '244': 56363,
                     '248': 7950,
                     '045': 3382 }

        self.assertEqual(expected, non_zero_results)

    def test_dagshub_ocr_old_with_password(self):
        PDF_PATH = "../forms/dagshub_ocr_old/031168701_T106.pdf"
        with open(PDF_PATH, 'rb') as pdf_file:
            process_file_content(pdf_file.read(), PDF_PATH, "106", "main", "H6RH54")
            non_zero_results = {k: v for k, v in state.results.items() if v != 0}

        expected = {'042': 14049,
                    '158': 60432,
                    '244': 56363,
                    '248': 7950,
                    '045': 3382}

        self.assertEqual(expected, non_zero_results)

    def test_dagshub_ocr_new(self):
        PDF_PATH = "../forms/dagshub_non_ocr/יובל דפני - טופס 106 לשנת 2023.pdf"
        with open(PDF_PATH, 'rb') as pdf_file:
            process_file_content(pdf_file.read(), PDF_PATH, "106", "main", "H6RH54")
            non_zero_results = {k: v for k, v in state.results.items() if v != 0}

        expected = {'042': 78068,
                    '158': 407373,
                    '244': 394957,
                    '248': 56853,
                    '045': 16822 + 6875}

        self.assertEqual(expected, non_zero_results)