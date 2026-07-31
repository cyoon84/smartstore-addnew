#!/usr/bin/env python3

import copy
import unittest

from build_draft import item_content
from verify_draft import expected_draft, first_difference


PARSED = {
    "shopping": [
        {
            "product_id": "100",
            "option": "맛: Chunk",
            "kor_name": "캐나다 코스트코 네슬레 킷캣 F1 레이싱카 밀크초콜릿 693g",
            "qty": 2,
        }
    ],
    "recipients": [
        {
            "name": "홍길동",
            "items": [
                {
                    "product_id": "100",
                    "option": "맛: Chunk",
                    "kor_name": "캐나다 코스트코 네슬레 킷캣 F1 레이싱카 밀크초콜릿 693g",
                    "qty": 2,
                }
            ],
        }
    ],
    "buyer_count": 1,
    "shopping_line_count": 1,
}


class DraftVerificationTest(unittest.TestCase):
    def test_content_preserves_full_name_and_option(self):
        content = item_content(PARSED["shopping"][0])
        self.assertEqual(
            content,
            "캐나다 코스트코 네슬레 킷캣 F1 레이싱카 밀크초콜릿 693g (맛: Chunk) × 2",
        )

    def test_exact_draft_passes(self):
        draft = expected_draft(PARSED)
        self.assertIsNone(first_difference(draft, draft))

    def test_shortened_product_name_fails(self):
        expected = expected_draft(PARSED)
        shortened = copy.deepcopy(expected)
        shortened["shopping"][0]["kor_name"] = "킷캣 F1 레이싱카 밀크초콜릿 693g"
        self.assertIsNotNone(first_difference(expected, shortened))

    def test_shortened_option_fails(self):
        expected = expected_draft(PARSED)
        shortened = copy.deepcopy(expected)
        shortened["recipients"][0]["items"][0]["option"] = "Chunk"
        self.assertIsNotNone(first_difference(expected, shortened))

    def test_due_date_on_child_fails(self):
        expected = expected_draft(PARSED)
        child_due = copy.deepcopy(expected)
        child_due["shopping"][0]["dueString"] = "2026-08-01"
        self.assertIsNotNone(first_difference(expected, child_due))

    def test_due_policy_is_parents_only(self):
        draft = expected_draft(PARSED)
        self.assertEqual(draft["due_policy"], "parents_only")


if __name__ == "__main__":
    unittest.main()
