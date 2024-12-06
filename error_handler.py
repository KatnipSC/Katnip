"""
Functions for throwing neat and descriptive errors
"""

errors = []
def add_error(reason, relavent_code, line_num):
    errors.append(f"❌ - {reason} in code '{relavent_code}' on line [{line_num}]\n")

def throw_errors():
    if errors:
        for error in errors:
            print(error)
        total_errors = len(errors)
        errors.clear()

        raise Exception(f"[{total_errors}] invalid commands found. See above for details.")