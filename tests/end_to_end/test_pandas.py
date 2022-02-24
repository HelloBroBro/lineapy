import pytest


def test_pandas_subscript(execute):
    code = """import pandas as pd
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
df["C"] = df["A"] + df["B"]
"""
    res = execute(code, artifacts=["df"])
    # assert res.values["df"].to_csv(index=False) == "A,B,C\n1,4,5\n2,5,7\n3,6,9\n"
    assert res.artifacts["df"] == code


def test_pandas_inplace_executes(execute):
    code = """import pandas as pd
df = pd.DataFrame({"A": [2, 4, None], "B": [4, 5, 6]})
mdf = df['A'].mean()
df['A'].fillna(mdf, inplace=True)
"""
    res = execute(code, artifacts=["df"])
    assert res.values["df"].to_csv(index=False) == "A,B\n2.0,4\n4.0,5\n3.0,6\n"
    assert res.artifacts["df"] == code


@pytest.mark.slow
def test_pandas(execute):
    code = """from pandas import DataFrame
v = 4
df = DataFrame([[1,2], [3,v]])
df[0].astype(str)
assert df.size == 4
new_df = df.iloc[:, 1]
assert new_df.size == 2
"""
    res = execute(code, snapshot=False)
    assert res.values["new_df"].size == 2
