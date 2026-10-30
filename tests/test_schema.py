import pandas as pd
import pandera.pandas as pa
import pytest

from kontroller.schema import kundschema


def test_invalid_age():
    df = pd.read_csv("data/kundbas.csv")
    df.loc[0, "alder"] = 999

    with pytest.raises(pa.errors.SchemaErrors):
        kundschema.validate(df, lazy=True)


def test_valid_data():
    df = pd.read_csv("data/kundbas.csv")
    kundschema.validate(df, lazy=True)
