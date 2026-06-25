from __future__ import annotations

from pathlib import Path

from docx import Document


ROOT_DIR = Path(__file__).resolve().parents[1]
DOCX_PATH = ROOT_DIR / "reports" / "实验报告.docx"


TEAM_ROWS = [
    ["组员", "邹传涛", "37220232203970", "环境搭建、报告整合、提交材料检查"],
    ["组长", "何后天", "37220232203673", "项目统筹、数据获取、pandas 清洗、SQLite 建库与验证查询"],
    ["组员", "彭泽喜", "37220232203792", "LangChain Data Agent、DeepSeek API 接入、Streamlit 可视化"],
]


def update_docx_team_table() -> None:
    doc = Document(DOCX_PATH)
    for table in doc.tables:
        header = [cell.text.strip() for cell in table.rows[0].cells]
        if header[:4] != ["角色", "姓名", "学号", "任务分工"]:
            continue
        if len(table.rows) < 4:
            continue
        for row, values in zip(table.rows[1:4], TEAM_ROWS):
            for cell, value in zip(row.cells, values):
                cell.text = value
        break
    else:
        raise RuntimeError("Could not find team member table in report DOCX.")
    doc.save(DOCX_PATH)
    print(f"Updated leader in {DOCX_PATH}")


if __name__ == "__main__":
    update_docx_team_table()
