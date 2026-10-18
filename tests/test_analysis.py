"""Analysis tests. Invariants: brands are returned in order of first mention without double counting;
look-alike names (RACV, RACQ) never count as RAC WA; URLs are classified by owner and PDS-ness."""
import pytest

from pds_agents import analysis


def test_brands_in_first_mention_order():
    text = "I'd start with Youi, then AAMI. Youi again. Budget Direct is cheaper."
    assert analysis.brands_mentioned(text) == ["youi", "aami", "budget_direct"]


@pytest.mark.parametrize("text,expected", [
    ("RACV and RACQ are clubs.", ["racv", "racq"]),
    ("RAC WA is the WA option.", ["rac_wa"]),
    ("RAC Insurance covers Perth.", ["rac_wa"]),
    ("RAC home insurance is decent.", ["rac_wa"]),
])
def test_rac_disambiguation(text, expected):
    assert analysis.brands_mentioned(text) == expected


def test_empty_text_has_no_brands():
    assert analysis.brands_mentioned("") == []


@pytest.mark.parametrize("url,kind,brand,is_pds", [
    ("https://www.nrma.com.au/content/dam/x/nrma-home-pds-rev2.pdf", "insurer", "nrma", True),
    ("https://qmdocumentlibrary.qbe.com/getfile?revision=ABC", "insurer", "qbe", False),
    ("https://www.einsure.com.au/wb/public/openPolicyDocument/POL1/$FILE/POL1.pdf?open", "insurer", "allianz", True),
    ("https://www.youi.com.au/GetPDS?riskType=VEH", "insurer", "youi", True),
    ("https://www.canstar.com.au/home-insurance/", "comparator", None, False),
    ("https://moneysmart.gov.au/home-insurance", "official", None, False),
    ("https://www.reddit.com/r/AusFinance/x", "forum", None, False),
    ("https://example.com/blog", "other", None, False),
])
def test_classify_url(url, kind, brand, is_pds):
    c = analysis.classify_url(url)
    assert (c["kind"], c["brand"], c["is_pds"]) == (kind, brand, is_pds)


def test_summarise_counts():
    row = analysis.summarise({"text": "Choose Suncorp or GIO.", "citations": [
        {"url": "https://www.suncorp.com.au/a.pdf"}, {"url": "https://www.finder.com.au/b"}],
        "search_queries": ["q1"], "persona": "p"})
    assert row["first_brand"] == "suncorp" and row["n_study_brands"] == 2
    assert row["n_pds_citations"] == 1 and row["n_comparator_citations"] == 1 and row["n_searches"] == 1
