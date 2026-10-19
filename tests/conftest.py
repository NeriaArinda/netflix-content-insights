import io

import pandas as pd
import pytest

from netflix_insights.cleaning import clean, load_raw

SAMPLE = """show_id,type,title,director,cast,country,date_added,release_year,rating,duration,listed_in,description
s1,Movie,Alpha,Jane Doe,"A, B",United States,"September 25, 2021",2020,PG-13,90 min,"Dramas, Comedies",x
s2,TV Show,Beta,,"C",India,"September 24, 2021",2021,TV-MA,2 Seasons,"International TV Shows, TV Dramas",x
s3,Movie,Gamma,John Roe,,"United States, India"," August 1, 2019",2015,R,120 min,Dramas,x
s4,Movie,Delta,Louis C.K.,,United States,"April 4, 2017",2017,74 min,,Movies,x
s5,Movie,Alpha,Jane Doe,"A, B",United States,"September 25, 2021",2020,PG-13,90 min,"Dramas, Comedies",x
s6,TV Show,Epsilon,,,,,2018,TV-14,1 Season,Kids' TV,x
"""


@pytest.fixture
def raw() -> pd.DataFrame:
    return load_raw(io.StringIO(SAMPLE))


@pytest.fixture
def df(raw) -> pd.DataFrame:
    return clean(raw)


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_text(SAMPLE, encoding="utf-8")
    return path
