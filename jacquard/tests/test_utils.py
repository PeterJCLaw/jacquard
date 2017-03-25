import pytest
import hypothesis
import hypothesis.strategies

from jacquard.utils import check_keys


def get_error(passed_keys, known_keys):
    try:
        check_keys(passed_keys, known_keys)
    except ValueError as e:
        return str(e)
    else:
        raise AssertionError("ValueError not raised")


@hypothesis.given(
    keys=hypothesis.strategies.lists(hypothesis.strategies.text()),
    included=hypothesis.strategies.streaming(hypothesis.strategies.booleans()),
)
def test_accepts_with_all_known_keys(keys, included):
    known_keys = keys
    used_keys = [
        key
        for key, should_include in zip(keys, included)
        if should_include
    ]
    check_keys(used_keys, known_keys)


@hypothesis.given(
    passed_keys=hypothesis.strategies.lists(
        hypothesis.strategies.text(),
        min_size=2,
        unique=True,
    ),
    known_keys=hypothesis.strategies.sets(
        hypothesis.strategies.text(),
    )
)
def test_rejects_with_multiple_unknown_keys(passed_keys, known_keys):
    hypothesis.assume(not any(
        x in known_keys
        for x in passed_keys
    ))

    error_message = get_error(passed_keys, known_keys)

    for passed_key in passed_keys:
        assert passed_key in error_message


@hypothesis.given(
    actual_key=hypothesis.strategies.text(),
    extra_character=hypothesis.strategies.characters(),
)
def test_offers_correction_for_minor_error(actual_key, extra_character):
    incorrect_key = actual_key + extra_character
    error_message = get_error({incorrect_key}, {actual_key})

    assert incorrect_key in error_message
    assert actual_key in error_message


@hypothesis.given(
    actual_key=hypothesis.strategies.text(),
    extra_character=hypothesis.strategies.characters(),
    other_keys=hypothesis.strategies.sets(
        hypothesis.strategies.text(),
        min_size=3,
    ),
)
def test_offers_correction_for_minor_error_with_many_possible_keys(
    actual_key,
    extra_character,
    other_keys,
):
    incorrect_key = actual_key + extra_character
    hypothesis.assume(incorrect_key not in other_keys)

    error_message = get_error({incorrect_key}, {actual_key, *other_keys})

    assert incorrect_key in error_message
    assert actual_key in error_message