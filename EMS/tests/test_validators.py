"""
Unit tests for input validators.
"""
import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.validators import (
    validate_email, validate_phone, validate_name,
    validate_salary, validate_date, validate_date_range,
    validate_username, validate_password, validate_rating,
    validate_emp_code, validate_allowance_deduction,
)


class TestEmailValidator(unittest.TestCase):

    def test_valid_email(self):
        ok, _ = validate_email("user@example.com")
        self.assertTrue(ok)

    def test_valid_email_subdomain(self):
        ok, _ = validate_email("user.name+tag@sub.example.co.uk")
        self.assertTrue(ok)

    def test_empty_email(self):
        ok, msg = validate_email("")
        self.assertFalse(ok)
        self.assertIn("required", msg.lower())

    def test_no_at_sign(self):
        ok, _ = validate_email("userexample.com")
        self.assertFalse(ok)

    def test_no_domain(self):
        ok, _ = validate_email("user@")
        self.assertFalse(ok)

    def test_spaces_invalid(self):
        ok, _ = validate_email("user @example.com")
        self.assertFalse(ok)


class TestPhoneValidator(unittest.TestCase):

    def test_valid_us_phone(self):
        ok, _ = validate_phone("+1-555-0101")
        self.assertTrue(ok)

    def test_optional_empty(self):
        ok, _ = validate_phone("")
        self.assertTrue(ok)

    def test_too_short(self):
        ok, _ = validate_phone("123")
        self.assertFalse(ok)

    def test_valid_plain_digits(self):
        ok, _ = validate_phone("5550101234")
        self.assertTrue(ok)


class TestNameValidator(unittest.TestCase):

    def test_valid_name(self):
        ok, _ = validate_name("Alice")
        self.assertTrue(ok)

    def test_name_with_hyphen(self):
        ok, _ = validate_name("Mary-Jane")
        self.assertTrue(ok)

    def test_too_short(self):
        ok, _ = validate_name("A")
        self.assertFalse(ok)

    def test_numbers_invalid(self):
        ok, _ = validate_name("Alice123")
        self.assertFalse(ok)

    def test_empty_name(self):
        ok, msg = validate_name("")
        self.assertFalse(ok)
        self.assertIn("required", msg.lower())

    def test_too_long(self):
        ok, _ = validate_name("A" * 51)
        self.assertFalse(ok)


class TestSalaryValidator(unittest.TestCase):

    def test_valid_salary(self):
        ok, _ = validate_salary("60000")
        self.assertTrue(ok)

    def test_valid_decimal(self):
        ok, _ = validate_salary("75000.50")
        self.assertTrue(ok)

    def test_zero_salary(self):
        ok, _ = validate_salary("0")
        self.assertTrue(ok)

    def test_negative_salary(self):
        ok, _ = validate_salary("-100")
        self.assertFalse(ok)

    def test_non_numeric(self):
        ok, _ = validate_salary("abc")
        self.assertFalse(ok)

    def test_empty_salary(self):
        ok, _ = validate_salary("")
        self.assertFalse(ok)

    def test_excessive_salary(self):
        ok, _ = validate_salary("999999999")
        self.assertFalse(ok)


class TestDateValidator(unittest.TestCase):

    def test_valid_iso_date(self):
        ok, _ = validate_date("2024-06-15")
        self.assertTrue(ok)

    def test_valid_us_format(self):
        ok, _ = validate_date("06/15/2024")
        self.assertTrue(ok)

    def test_empty_date(self):
        ok, _ = validate_date("")
        self.assertFalse(ok)

    def test_invalid_format(self):
        ok, _ = validate_date("15-Jun-2024")
        self.assertFalse(ok)

    def test_impossible_date(self):
        ok, _ = validate_date("2024-13-01")
        self.assertFalse(ok)


class TestDateRangeValidator(unittest.TestCase):

    def test_valid_range(self):
        ok, _ = validate_date_range("2024-01-01", "2024-01-10")
        self.assertTrue(ok)

    def test_same_day(self):
        ok, _ = validate_date_range("2024-06-15", "2024-06-15")
        self.assertTrue(ok)

    def test_reversed_range(self):
        ok, _ = validate_date_range("2024-06-20", "2024-06-10")
        self.assertFalse(ok)

    def test_invalid_start(self):
        ok, _ = validate_date_range("bad-date", "2024-06-10")
        self.assertFalse(ok)


class TestUsernameValidator(unittest.TestCase):

    def test_valid_username(self):
        ok, _ = validate_username("john_doe")
        self.assertTrue(ok)

    def test_too_short(self):
        ok, _ = validate_username("ab")
        self.assertFalse(ok)

    def test_special_chars(self):
        ok, _ = validate_username("john@doe!")
        self.assertFalse(ok)

    def test_empty_username(self):
        ok, _ = validate_username("")
        self.assertFalse(ok)


class TestPasswordValidator(unittest.TestCase):

    def test_valid_password(self):
        ok, _ = validate_password("secure123")
        self.assertTrue(ok)

    def test_too_short(self):
        ok, _ = validate_password("abc")
        self.assertFalse(ok)

    def test_empty_password(self):
        ok, _ = validate_password("")
        self.assertFalse(ok)


class TestRatingValidator(unittest.TestCase):

    def test_valid_ratings(self):
        for r in range(1, 6):
            ok, _ = validate_rating(r)
            self.assertTrue(ok, f"Rating {r} should be valid")

    def test_zero_invalid(self):
        ok, _ = validate_rating(0)
        self.assertFalse(ok)

    def test_six_invalid(self):
        ok, _ = validate_rating(6)
        self.assertFalse(ok)

    def test_string_number(self):
        ok, _ = validate_rating("4")
        self.assertTrue(ok)

    def test_non_numeric(self):
        ok, _ = validate_rating("excellent")
        self.assertFalse(ok)


class TestEmpCodeValidator(unittest.TestCase):

    def test_valid_code(self):
        ok, _ = validate_emp_code("EMP001")
        self.assertTrue(ok)

    def test_lowercase_accepted(self):
        ok, _ = validate_emp_code("emp001")
        self.assertTrue(ok)

    def test_no_digits(self):
        ok, _ = validate_emp_code("EMPXYZ")
        self.assertFalse(ok)

    def test_too_few_letters(self):
        ok, _ = validate_emp_code("E001")
        self.assertFalse(ok)

    def test_empty(self):
        ok, _ = validate_emp_code("")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main(verbosity=2)
