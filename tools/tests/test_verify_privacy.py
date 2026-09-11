import os
import subprocess
from tools.verify_privacy import name_hash, scan_text, load_hashes, main, scan_binary

FAKE = "Zelda Quux"

def test_name_hash_normalises_case_and_spacing():
    assert name_hash("Zelda  QUUX") == name_hash("zelda quux")

def test_full_name_and_parts_are_caught():
    hashes = {name_hash(FAKE), name_hash("Zelda")}
    assert (1, "name") in scan_text("Report by zelda quux.\n", hashes)
    assert scan_text("ok\nZelda said\n", hashes) == [(2, "name")]

def test_clean_text_passes():
    assert scan_text("Participant P1 rated activation easy.\n", {name_hash(FAKE)}) == []

def test_windows_user_path_is_caught():
    text = "C:" + "\\Users\\someone\\Desktop\\x.prt\n"
    assert (1, "windows-path") in scan_text(text, set())

def test_email_is_caught():
    text = "contact " + "jane.doe" + "@" + "example.org\n"
    assert (1, "email") in scan_text(text, set())

def test_the_group_contact_address_is_allowed():
    text = "mailto:" + "ghe" + "@" + "mavt.ethz.ch\n"
    assert scan_text(text, set()) == []

def test_load_hashes_ignores_comments(tmp_path):
    p = tmp_path / "h.txt"
    p.write_text("# comment\n" + name_hash(FAKE) + "\n\n")
    assert load_hashes(str(p)) == {name_hash(FAKE)}

def test_main_exit_codes(tmp_path):
    h = tmp_path / "h.txt"; h.write_text(name_hash(FAKE) + "\n")
    good = tmp_path / "g.md"; good.write_text("P1 and P2\n")
    bad = tmp_path / "b.md"; bad.write_text("thanks to Zelda Quux\n")
    assert main([str(good)], hashes_path=str(h)) == 0
    assert main([str(bad)], hashes_path=str(h)) == 1

def test_main_fails_closed_on_empty_hash_file(tmp_path):
    h = tmp_path / "empty.txt"; h.write_text("# comment\n")
    good = tmp_path / "g.md"; good.write_text("P1 and P2\n")
    assert main([str(good)], hashes_path=str(h)) == 1

def test_main_fails_closed_on_missing_hash_file(tmp_path):
    missing = tmp_path / "does-not-exist.txt"
    good = tmp_path / "g.md"; good.write_text("P1 and P2\n")
    assert main([str(good)], hashes_path=str(missing)) == 1

def _init_git_repo(path):
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test" + "@" + "example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, check=True)


def _commit_binary_file(path, name, data):
    (path / name).write_bytes(data)
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "add binary"], cwd=path, check=True)


def test_main_default_binary_branch_catches_a_windows_path(tmp_path):
    """main()'s default (patterns=None) branch scans tracked non-text
    files with scan_binary, not just scan_text on the patterns branch."""
    _init_git_repo(str(tmp_path))
    h = tmp_path / "h.txt"
    h.write_text(name_hash(FAKE) + "\n")
    path_bytes = ("C:" + "\\Users\\someone\\Desktop\\x").encode("ascii")
    _commit_binary_file(tmp_path, "part.prt", b"\x00\x01" + path_bytes + b"\x00")
    assert main(hashes_path=str(h), root=str(tmp_path)) == 1


def test_main_default_binary_branch_passes_on_clean_binary(tmp_path):
    _init_git_repo(str(tmp_path))
    h = tmp_path / "h.txt"
    h.write_text(name_hash(FAKE) + "\n")
    _commit_binary_file(tmp_path, "part.prt", os.urandom(64))
    assert main(hashes_path=str(h), root=str(tmp_path)) == 0


def test_binary_windows_path_is_caught(tmp_path):
    path_bytes = b"\\Users\\someone\\x"
    ascii_bin = tmp_path / "x.bin"
    ascii_bin.write_bytes(b"\x00\x01" + b"C:" + path_bytes + b"\x00")
    assert scan_binary(str(ascii_bin)) is True

    utf16_bin = tmp_path / "y.bin"
    utf16_bin.write_bytes(b"\x00\x01" + ("C:" + path_bytes.decode("ascii")).encode("utf-16-le") + b"\x00")
    assert scan_binary(str(utf16_bin)) is True

    clean_bin = tmp_path / "z.bin"
    clean_bin.write_bytes(os.urandom(64))
    assert scan_binary(str(clean_bin)) is False
