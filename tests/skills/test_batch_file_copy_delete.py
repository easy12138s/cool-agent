import pytest

from src.agents.tools.registry import ToolRegistry


@pytest.mark.anyio
async def test_skill_batch_file_copy_can_run(tmp_path) -> None:
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_dir.mkdir()
    dst_dir.mkdir()

    (src_dir / "a.txt").write_text("a", encoding="utf-8")
    (src_dir / "b.log").write_text("b", encoding="utf-8")

    registry = ToolRegistry()
    registry.scan_skills()
    tool = registry.get_tool("batch-file-copy")
    assert tool is not None

    result = await tool.run(
        source_path=str(src_dir),
        target_path=str(dst_dir),
        file_filter=".txt",
        copy_subfolders=False,
        duplicate_strategy="rename",
    )

    assert result.get("error_msg") == ""
    assert result.get("success_count") == 1
    assert (dst_dir / "a.txt").exists()
    assert (dst_dir / "b.log").exists() is False
    assert (src_dir / "a.txt").exists()


@pytest.mark.anyio
async def test_skill_batch_file_delete_dry_run_then_delete(tmp_path) -> None:
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "a.log").write_text("a", encoding="utf-8")
    (target_dir / "b.txt").write_text("b", encoding="utf-8")

    registry = ToolRegistry()
    registry.scan_skills()
    tool = registry.get_tool("batch-file-delete")
    assert tool is not None

    preview = await tool.run(
        target_path=str(target_dir),
        file_filter=".log",
        delete_subfolders=False,
        dry_run=True,
        max_delete=200,
    )
    assert preview.get("error_msg") == ""
    assert preview.get("would_delete_count") == 1
    assert (target_dir / "a.log").exists()

    executed = await tool.run(
        target_path=str(target_dir),
        file_filter=".log",
        delete_subfolders=False,
        dry_run=False,
        max_delete=200,
    )
    assert executed.get("error_msg") == ""
    assert executed.get("success_count") == 1
    assert (target_dir / "a.log").exists() is False
    assert (target_dir / "b.txt").exists()

