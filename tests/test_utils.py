from flxtrd import utils
import pytest

@pytest.mark.parametrize(
    "epoch_time, expected",
    [
        ("1627986547", "2021-08-03T10:29:07.000Z"),
        ("1627986547123", "2021-08-03T10:29:07.123Z"),
        ("1627986547123456", "2021-08-03T10:29:07.123Z"),
        ("1627986547123456789", "2021-08-03T10:29:07.123Z"),
        ("1627986547123456789123", "2021-08-03T10:29:07.123Z"),
        (1627986547, "2021-08-03T10:29:07.000Z"),
        (1627986547123, "2021-08-03T10:29:07.123Z"),
        (1627986547123456, "2021-08-03T10:29:07.123Z"),
        (1627986547123456789, "2021-08-03T10:29:07.123Z"),
        (1627986547123456789123, "2021-08-03T10:29:07.123Z"),
    ],
)
def test_epoch_time_to_isoformat(epoch_time, expected):
    """Test epoch_time_to_isoformat"""
    isoformat = utils.epoch_time_to_isoformat(epoch_time)
    assert isoformat == expected, f"Got unexpected isoformat {isoformat}"