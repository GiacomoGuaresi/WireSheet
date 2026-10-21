from wiresheet.__main__ import self_test


def test_self_test_writes_pdf_and_template(app, tmp_path):
    self_test(tmp_path / "out")
    assert (tmp_path / "out" / "demo.pdf").stat().st_size > 0
    assert (tmp_path / "out" / "template.xlsx").stat().st_size > 0
