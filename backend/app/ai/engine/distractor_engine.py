import math
import random
import re
from fractions import Fraction


class DistractorEngine:
    """Creates plausible, non-trivial MCQ distractors without changing the answer."""

    _FRACTION_RE = re.compile(r"^\s*(-?\d+)\s*/\s*(-?\d+)\s*$")
    _NUMBER_RE = re.compile(r"^\s*-?\d+(?:\.\d+)?\s*$")
    _TUPLE_RE = re.compile(r"^\s*\((-?\d+)\s*[,;]\s*(-?\d+)\)\s*$")

    def build(self, answer, supplied=(), question="", topic="", game_id="", count=3):
        answer_s = self._norm(answer)
        candidates = []
        # Fractions are handled by a dedicated pool first so distractors do not
        # inherit crude values such as answer-1/answer+1 from older banks.
        if self._FRACTION_RE.match(answer_s):
            candidates.extend(self._fraction_candidates(answer_s, topic, game_id))
            for value in supplied or ():
                if self._fraction_allowed(value, topic, game_id):
                    self._add(candidates, value, answer_s)
        elif self._TUPLE_RE.match(answer_s):
            for value in supplied or ():
                self._add(candidates, value, answer_s)
            candidates.extend(self._tuple_candidates(answer_s))
        elif self._NUMBER_RE.match(answer_s):
            for value in supplied or ():
                self._add(candidates, value, answer_s)
            candidates.extend(self._number_candidates(answer_s, topic, game_id))
        else:
            for value in supplied or ():
                self._add(candidates, value, answer_s)
            candidates.extend(self._text_candidates(answer_s, supplied, topic))

        result = []
        for value in self._shuffle_unique(candidates):
            if self._is_obvious_numeric_variant(answer_s, self._norm(value)):
                continue
            if self._looks_too_similar(answer_s, self._norm(value)):
                continue
            if self._norm(value) not in {self._norm(x) for x in result}:
                result.append(self._norm(value))
            if len(result) >= count:
                break

        # Last-resort candidates are still deliberately non-adjacent, never answer +/- 1/2.
        if len(result) < count and self._NUMBER_RE.match(answer_s):
            base = float(answer_s)
            fallback = [base * 2, base / 2 if base else 3, -base if base else -3,
                        base * 3, base / 3 if base else 5, base + 10, base - 10]
            for value in fallback:
                text = self._format_number(value)
                if self._valid(text, answer_s) and not self._is_obvious_numeric_variant(answer_s, text):
                    result.append(text)
                    result = list(dict.fromkeys(result))
                    if len(result) >= count:
                        break
        return result[:count]

    def _fraction_candidates(self, text, topic="", game_id=""):
        f = self._fraction(text)
        if not f:
            return []
        n, d = f.numerator, f.denominator
        values = []
        topic_l = (topic + " " + game_id).lower()
        if "xác suất" in topic_l or "probability" in topic_l:
            # Plausible probability choices: all in [0,1], visually varied and
            # unrelated to the correct fraction by a trivial +/- operation.
            values += [Fraction(3, 5), Fraction(6, 7), Fraction(9, 11), Fraction(4, 9), Fraction(5, 8), Fraction(2, 3), Fraction(7, 10), Fraction(5, 12)]
            if d > 1:
                values += [Fraction(d - n, d), Fraction(n + 1, d + 1)]
        else:
            if d > 1:
                values += [Fraction(d - n, d), Fraction(n + 1, d + 1), Fraction(max(1, n - 1), d)]
            if n != 0:
                values += [Fraction(d, n), Fraction(-n, d)]
            values += [Fraction(2, 3), Fraction(3, 5), Fraction(4, 7), Fraction(5, 8), Fraction(6, 7), Fraction(7, 9), Fraction(9, 11)]
        random.shuffle(values)
        return [self._format_fraction(x) for x in values]

    def _fraction_allowed(self, value, topic, game_id):
        if not self._FRACTION_RE.match(self._norm(value)):
            return True
        f = self._fraction(self._norm(value))
        topic_l = (topic + " " + game_id).lower()
        if "xác suất" in topic_l or "probability" in topic_l:
            return f is not None and 0 <= f <= 1
        return True

    def _number_candidates(self, text, topic, game_id):
        x = float(text)
        integer = x.is_integer()
        n = int(x) if integer else x
        values = []
        # Topic-aware conceptual confusions.
        topic_l = (topic + " " + game_id).lower()
        if "xác suất" in topic_l:
            values += [Fraction(1, 2), Fraction(1, 3), Fraction(2, 3), Fraction(3, 5), Fraction(4, 7), Fraction(5, 8)]
        elif "thống kê" in topic_l:
            values += [n * 2, n / 2 if n else 1, abs(n), n + 3, n - 3]
        elif "hình" in topic_l:
            values += [n * 2, n / 2 if n else 1, n + 5, max(0, n - 5)]
        elif "tổ hợp" in topic_l or "chỉnh hợp" in topic_l:
            values += [n * 2, max(1, n // 2), n + 10, max(1, n - 10)]
        else:
            values += [n * 2, n / 2 if n else 1, -n, n + 5, n - 5, n + 10, n - 10]
        random.shuffle(values)
        return [self._format_number(v) for v in values]

    def _tuple_candidates(self, text):
        m = self._TUPLE_RE.match(text)
        x, y = int(m.group(1)), int(m.group(2))
        vals = [(y, x), (-x, y), (x, -y), (x + 2, y - 1), (x - 1, y + 2), (y + 1, x - 1)]
        random.shuffle(vals)
        return [f"({a};{b})" for a, b in vals]

    def _text_candidates(self, answer, supplied, topic):
        # For conceptual/set/inequality answers, preserve the bank's semantic choices.
        vals = list(supplied or [])
        random.shuffle(vals)
        return vals

    def _add(self, arr, value, answer):
        v = self._norm(value)
        if self._valid(v, answer):
            arr.append(v)

    def _valid(self, value, answer):
        return bool(value) and self._norm(value) != self._norm(answer)

    def _is_obvious_numeric_variant(self, answer, candidate):
        if not (self._NUMBER_RE.match(answer) and self._NUMBER_RE.match(candidate)):
            return False
        a, b = float(answer), float(candidate)
        return abs(a - b) in (1, 2) or (a != 0 and abs(b / a) in (1.0,))

    def _looks_too_similar(self, answer, candidate):
        if answer == candidate:
            return True
        # Do not accept formatting-only changes.
        try:
            af, cf = self._fraction(answer), self._fraction(candidate)
            if af is not None and cf is not None and af == cf:
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def _norm(value):
        return str(value).strip()

    @staticmethod
    def _fraction(text):
        m = DistractorEngine._FRACTION_RE.match(text)
        if not m:
            return None
        try:
            return Fraction(int(m.group(1)), int(m.group(2)))
        except ZeroDivisionError:
            return None

    @staticmethod
    def _format_fraction(value):
        f = Fraction(value)
        return str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}"

    @staticmethod
    def _format_number(value):
        if isinstance(value, Fraction):
            return DistractorEngine._format_fraction(value)
        if abs(float(value) - round(float(value))) < 1e-9:
            return str(int(round(float(value))))
        return f"{float(value):.4f}".rstrip("0").rstrip(".")

    @staticmethod
    def _shuffle_unique(values):
        vals = list(dict.fromkeys(str(x).strip() for x in values if str(x).strip()))
        random.shuffle(vals)
        return vals
