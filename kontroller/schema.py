import pandera.pandas as pa
import pandas as pd
import sys

kundschema = pa.DataFrameSchema(
    {
        "kund_id": pa.Column(int, unique=True, nullable=False),
        "alder": pa.Column(int, pa.Check.in_range(0, 120), nullable=False),
        "region": pa.Column(str, nullable=False),
        "abonnemang": pa.Column(str, nullable=False),
        "manadskostnad": pa.Column(float, pa.Check.ge(0), nullable=False),
        "data_gb_per_manad": pa.Column(float, pa.Check.ge(0), nullable=False),
        "supportarenden_12m": pa.Column(int, pa.Check.ge(0), nullable=False),
        "avslutat": pa.Column(int, pa.Check.isin(0, 1), nullable=False),
    }
)


if __name__ == "__main__":
    filnamn = sys.argv[1] if len(sys.argv) > 1 else "data/kundbas.csv"

    df = pd.read_csv(filnamn)
    kundschema.validate(df, lazy=True)

    print(f"Datavalidering godkänd: {filnamn}")
