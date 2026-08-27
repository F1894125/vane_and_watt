import re


NAME_REGEX = re.compile(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ' \-]{1,9}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")