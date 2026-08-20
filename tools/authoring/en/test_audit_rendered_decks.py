import unittest

import audit_rendered_decks


class RenderAuditContractTests(unittest.TestCase):
    def test_inline_spacing_probe_covers_both_generated_input_components(self):
        probe = audit_rendered_decks.probe_expression()

        self.assertIn(".slot-input, .phrase-input", probe)
        self.assertIn("'inline-answer-input', 8", probe)


if __name__ == "__main__":
    unittest.main()
