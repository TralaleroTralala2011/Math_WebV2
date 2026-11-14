from pathlib import Path
import pytest
from fastapi import HTTPException
from app import verified_bank_routes as bank


def test_git_lfs_pointer_is_not_claimed_as_real_bank(tmp_path):
    f=tmp_path/'test.jsonl'
    f.write_text('version https://git-lfs.github.com/spec/v1\noid sha256:abcdef\nsize 999\n',encoding='utf8')
    with pytest.raises(HTTPException) as error:
        bank.load_bank(f)
    assert error.value.status_code == 503
    with pytest.raises(HTTPException) as error:
        bank._indexed_bank(f)
    assert error.value.status_code == 503
