from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "db" / "nba_analysis.sqlite"
FIG_DIR = ROOT_DIR / "reports" / "figures"
OUT_DIR = ROOT_DIR / "output" / "pdf"
OUT_PATH = OUT_DIR / "实验报告.pdf"

TEAM_ROWS = [
    ["组员", "邹传涛", "37220232203970", "环境搭建、报告整合、提交材料检查"],
    ["组长", "何后天", "37220232203673", "项目统筹、数据获取、pandas 清洗、SQLite 建库与验证查询"],
    ["组员", "彭泽喜", "37220232203792", "LangChain Data Agent、DeepSeek API 接入、Streamlit 可视化"],
]


def query(sql: str) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn)


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def bullet_list(items: list[str], styles) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, styles["Body"]), leftIndent=12) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=16,
        bulletFontName="STSong-Light",
    )


def numbered_list(items: list[str], styles) -> ListFlowable:
    return ListFlowable(
        [ListItem(p(item, styles["Body"]), leftIndent=12) for item in items],
        bulletType="1",
        leftIndent=18,
        bulletFontName="STSong-Light",
    )


def df_table(df: pd.DataFrame, col_widths: list[float] | None = None) -> Table:
    data = [[str(col) for col in df.columns]]
    for _, row in df.iterrows():
        values = []
        for col in df.columns:
            value = row[col]
            if isinstance(value, float):
                value = f"{value:.2f}"
            values.append(str(value))
        data.append(values)
    widths = [w * inch for w in col_widths] if col_widths else None
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F4F7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1F4D78")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9D1D9")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def code_block(code: str, styles) -> Table:
    para = p(code.strip(), styles["Code"])
    table = Table([[para]], colWidths=[6.35 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F6F9")),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D7DE")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def build_styles():
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "TitleCn",
            parent=base["Title"],
            fontName="STSong-Light",
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#0B2545"),
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "Subtitle": ParagraphStyle(
            "SubtitleCn",
            parent=base["Normal"],
            fontName="STSong-Light",
            fontSize=15,
            leading=20,
            textColor=colors.HexColor("#2E74B5"),
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "H1": ParagraphStyle(
            "H1Cn",
            parent=base["Heading1"],
            fontName="STSong-Light",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#2E74B5"),
            spaceBefore=14,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "H2": ParagraphStyle(
            "H2Cn",
            parent=base["Heading2"],
            fontName="STSong-Light",
            fontSize=12.5,
            leading=16,
            textColor=colors.HexColor("#1F4D78"),
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "BodyCn",
            parent=base["BodyText"],
            fontName="STSong-Light",
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "Small": ParagraphStyle(
            "SmallCn",
            parent=base["BodyText"],
            fontName="STSong-Light",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#555555"),
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "Code": ParagraphStyle(
            "CodeCn",
            parent=base["Code"],
            fontName="STSong-Light",
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#24292F"),
        ),
    }


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("STSong-Light", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawCentredString(4.25 * inch, 0.45 * inch, f"实验7 NBA 数据分析智能体实验报告 - 第 {doc.page} 页")
    canvas.restoreState()


def add_case(story, styles, title, question, sql, result, analysis):
    story.append(p(title, styles["H2"]))
    story.append(p("自然语言问题：" + question, styles["Body"]))
    story.append(p("智能体生成或等价执行 SQL：", styles["Body"]))
    story.append(code_block(sql, styles))
    story.append(Spacer(1, 5))
    story.append(p("SQL 查询结果节选：", styles["Body"]))
    story.append(df_table(result))
    story.append(p("自然语言解释：" + analysis, styles["Body"]))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    styles = build_styles()
    story = []

    profile = pd.DataFrame(
        [
            ["teams", 30, 30, 0, 4, 4],
            ["games", 26651, 26622, 29, 1188, 1287],
            ["players", 7228, 7228, 0, 0, 0],
            ["rankings", 210342, 210313, 29, 206352, 206323],
            ["game_details", 668628, 668339, 289, 3804854, 2268343],
        ],
        columns=["表", "原始行数", "清洗后行数", "删除重复行数", "清洗前缺失单元格", "清洗后缺失单元格"],
    )
    table_counts = query(
        """
        SELECT 'teams' AS table_name, COUNT(*) AS row_count FROM teams
        UNION ALL SELECT 'games', COUNT(*) FROM games
        UNION ALL SELECT 'players', COUNT(*) FROM players
        UNION ALL SELECT 'rankings', COUNT(*) FROM rankings
        UNION ALL SELECT 'player_game_stats', COUNT(*) FROM player_game_stats
        """
    )
    season_counts = query("SELECT season AS 赛季, COUNT(*) AS 比赛数量 FROM games GROUP BY season ORDER BY season LIMIT 8")
    home_win = query("SELECT season AS 赛季, ROUND(AVG(home_team_wins)*100,2) AS 主队胜率百分比 FROM games WHERE home_team_wins IS NOT NULL GROUP BY season ORDER BY season LIMIT 8")
    team_avg = query(
        """
        SELECT t.nickname AS 球队, ROUND(AVG(team_points),2) AS 场均得分
        FROM (SELECT home_team_id AS team_id, pts_home AS team_points FROM games
              UNION ALL SELECT visitor_team_id AS team_id, pts_away AS team_points FROM games) s
        JOIN teams t ON t.team_id=s.team_id
        GROUP BY t.team_id,t.nickname
        ORDER BY 场均得分 DESC
        LIMIT 10
        """
    )
    player_top = query(
        """
        SELECT player_name AS 球员, team_abbreviation AS 球队, game_id AS 比赛ID, pts AS 得分
        FROM player_game_stats
        WHERE pts IS NOT NULL
        ORDER BY pts DESC
        LIMIT 10
        """
    )
    season_points = query("SELECT season AS 赛季, ROUND(AVG(total_points),2) AS 场均总得分 FROM games WHERE total_points IS NOT NULL GROUP BY season ORDER BY season LIMIT 8")

    story.append(p("数据库系统原理期末大作业", styles["Title"]))
    story.append(p("实验7：NBA 数据分析智能体的设计与实现", styles["Subtitle"]))
    story.append(df_table(pd.DataFrame([
        ["课程", "数据库系统原理"],
        ["项目主题", "基于 NBA 公开数据集的数据分析智能体"],
        ["技术路线", "Python + pandas + SQLite + LangChain + DeepSeek API + Streamlit"],
        ["提交形式", "RAR 压缩包，包含报告、代码、数据或数据获取说明、运行截图"],
    ], columns=["项目", "内容"]), [1.2, 5.1]))
    story.append(Spacer(1, 10))
    story.append(df_table(pd.DataFrame(TEAM_ROWS, columns=["角色", "姓名", "学号", "任务分工"]), [0.7, 0.85, 1.35, 3.43]))
    story.append(p("说明：DeepSeek API Key 仅保存在本地 .env 文件中，报告和提交材料不包含真实密钥。", styles["Small"]))
    story.append(PageBreak())

    story.append(p("一、实验目的与总体要求", styles["H1"]))
    story.append(p("本实验围绕公开 NBA 篮球比赛数据集，设计并实现一个能够回答业务分析问题的数据智能体。项目覆盖真实数据集下载、清洗、关系数据库建模、SQL 查询、可视化展示和大模型辅助分析的完整流程。", styles["Body"]))
    story.append(bullet_list([
        "使用 Python 和 pandas 完成数据读取、清洗、字段转换和统计概要生成。",
        "使用 SQLite 建立关系数据库，提供建表、导入、索引和验证查询。",
        "使用 LangChain 连接数据库，并结合 DeepSeek API 完成自然语言问题到 SQL 查询再到分析解释的流程。",
        "使用 Streamlit 展示自然语言提问、SQL、查询结果、自然语言解释和图表。",
    ], styles))

    story.append(p("二、开发环境与工具", styles["H1"]))
    story.append(df_table(pd.DataFrame([
        ["操作系统", "macOS，本地目录 /Users/whe/Desktop/BBB"],
        ["Python", "3.10.14"],
        ["数据处理", "pandas 2.3.3"],
        ["数据库", "SQLite，本地文件 db/nba_analysis.sqlite"],
        ["Agent 框架", "LangChain 1.3.11, langchain-openai 1.3.3"],
        ["大模型 API", "DeepSeek API，base_url=https://api.deepseek.com"],
        ["界面与可视化", "Streamlit 1.58.0, Plotly 6.8.0, Matplotlib 3.10.9"],
        ["版本控制", "Git，本项目已分阶段提交"],
    ], columns=["类别", "说明"]), [1.35, 4.95]))

    story.append(p("三、数据集来源与字段说明", styles["H1"]))
    story.append(p("本项目选用 Kaggle 公开数据集 nathanlauga/nba-games。该数据集包含 2003 到 2022 年左右的 NBA 比赛、球队、球员、排名和球员单场技术统计数据，适合多表建模、关联查询和业务分析。", styles["Body"]))
    story.append(df_table(pd.DataFrame([
        ["games.csv", "比赛事实表", "比赛日期、赛季、主客队、比分、命中率、篮板、助攻、主队是否获胜等。"],
        ["games_details.csv", "球员单场统计", "球员、球队、上场时间、投篮、三分、罚球、篮板、助攻、抢断、盖帽、得分等。"],
        ["players.csv", "球员信息", "球员姓名、球员 ID、所属球队、赛季。"],
        ["ranking.csv", "球队排名", "球队、日期、赛季、胜负场、胜率、主客场战绩等。"],
        ["teams.csv", "球队信息", "球队 ID、缩写、城市、昵称、主场球馆、建队年份等。"],
    ], columns=["原始文件", "用途", "主要字段"]), [1.35, 1.15, 3.8]))

    story.append(p("四、数据预处理", styles["H1"]))
    story.append(p("数据预处理由 src/preprocess.py 完成。脚本读取 data/raw 下的 5 个 CSV 文件，统一字段名、转换类型、处理缺失值和重复记录，并输出清洗后的 CSV 到 data/processed。", styles["Body"]))
    story.append(bullet_list([
        "字段名统一转为小写，便于 SQL 查询。",
        "日期字段转为 YYYY-MM-DD 文本格式。",
        "分数、命中率、篮板、助攻、抢断、盖帽等字段转为数值类型。",
        "球员未上场记录保留，并使用 played 字段标记。",
        "计数类技术统计缺失值按 0 处理；命中率类字段无法计算时保留为空。",
        "按业务主键去除明显重复记录。",
    ], styles))
    story.append(df_table(profile, [0.9, 0.8, 0.85, 0.85, 1.45, 1.45]))

    story.append(p("五、数据库设计与建库", styles["H1"]))
    story.append(p("数据库使用 SQLite，建库脚本为 src/build_database.py。该脚本会重新生成 db/nba_analysis.sqlite，创建表结构、导入清洗后的 CSV、建立索引，并输出验证查询结果。", styles["Body"]))
    story.append(df_table(pd.DataFrame([
        ["teams", "team_id", "球队维表，保存球队城市、昵称、缩写、主场、建队年份等。"],
        ["games", "game_id", "比赛事实表，保存赛季、日期、主客队、比分、命中率和主队胜负。"],
        ["players", "player_id + team_id + season", "球员赛季信息表。"],
        ["rankings", "自增 id", "球队排名表，保存胜负场、胜率、主客场战绩。"],
        ["player_game_stats", "自增 id，唯一索引 game_id + player_id", "球员单场技术统计表。"],
    ], columns=["表名", "主键/唯一约束", "说明"]), [1.3, 2.1, 2.9]))
    story.append(p("常用查询字段建立了索引，包括 games(season)、games(game_date)、games(home_team_id)、games(visitor_team_id)、player_game_stats(game_id)、player_game_stats(player_id)、player_game_stats(team_id)、rankings(team_id)、rankings(standings_date)。", styles["Body"]))
    story.append(df_table(table_counts, [3.1, 1.4]))

    story.append(p("六、Data Agent 设计与实现", styles["H1"]))
    story.append(p("数据智能体由 src/agent.py 实现。系统采用 LangChain 的 SQLDatabase 读取 SQLite schema，使用 langchain-openai 的 ChatOpenAI 以 OpenAI 兼容方式接入 DeepSeek API。", styles["Body"]))
    story.append(numbered_list([
        "用户在 Streamlit 页面输入中文业务问题。",
        "系统读取 SQLite 数据库表结构，并把 schema 和用户问题一起传给 DeepSeek。",
        "DeepSeek 生成 SQLite 只读 SQL。",
        "src/sql_safety.py 校验 SQL，只允许 SELECT 或 WITH，禁止危险语句。",
        "SQL 校验通过后连接 SQLite 执行查询，返回真实结果表。",
        "系统将问题、SQL 和结果样例传给 DeepSeek，生成中文业务分析结论。",
    ], styles))
    story.append(df_table(pd.DataFrame([
        ["SQL 生成提示词", "要求模型只输出 SQLite SQL，不输出 Markdown 或解释；只能使用 SELECT/WITH；字段必须来自 schema。"],
        ["结果解释提示词", "要求模型只基于用户问题、SQL 和查询结果前 20 行作答，禁止编造事实。"],
        ["人工修改内容", "人工补充 SQL 安全检查、默认 LIMIT、错误提示和 Streamlit 展示逻辑。"],
    ], columns=["项目", "内容"]), [1.5, 4.8]))

    story.append(p("七、Streamlit 界面与可视化", styles["H1"]))
    story.append(p("界面由 src/app.py 实现，页面显示数据库状态、示例问题、用户输入框、生成 SQL、查询结果、智能体解释和固定业务图表。固定图表不依赖大模型，能够直接用 SQLite 真实查询结果展示。", styles["Body"]))
    for image_name, caption in [
        ("season_avg_total_points.png", "图 1 赛季场均总得分趋势。2003 赛季场均总得分为 186.00，后续赛季整体呈上升趋势。"),
        ("team_avg_points_top10.png", "图 2 球队场均得分 Top 10。Warriors、Suns、Nuggets 位居前列。"),
        ("home_win_rate_by_season.png", "图 3 主队胜率随赛季变化。多数赛季主队胜率约在 57% 到 61% 之间。"),
    ]:
        path = FIG_DIR / image_name
        if path.exists():
            story.append(KeepTogether([Image(str(path), width=6.2 * inch, height=3.1 * inch), p(caption, styles["Small"])]))

    story.append(p("八、业务分析案例", styles["H1"]))
    add_case(story, styles, "案例 1：每个赛季比赛数量", "每个赛季的比赛数量是多少？", "SELECT season AS 赛季, COUNT(*) AS 比赛数量 FROM games GROUP BY season ORDER BY season LIMIT 8;", season_counts, "2003 到 2010 年每个完整赛季大多在 1360 到 1430 场左右，2011 赛季比赛数量明显较少。")
    add_case(story, styles, "案例 2：每个赛季主队胜率", "每个赛季主队胜率是多少？", "SELECT season AS 赛季, ROUND(AVG(home_team_wins)*100,2) AS 主队胜率百分比 FROM games WHERE home_team_wins IS NOT NULL GROUP BY season ORDER BY season LIMIT 8;", home_win, "主队胜率多数年份在 58% 到 61% 左右，说明主场优势在 NBA 比赛数据中较为明显。")
    add_case(story, styles, "案例 3：球队场均得分排名", "哪些球队场均得分最高？", "SELECT t.nickname AS 球队, ROUND(AVG(team_points),2) AS 场均得分 FROM ... GROUP BY t.team_id,t.nickname ORDER BY 场均得分 DESC LIMIT 10;", team_avg, "Warriors 以 107.50 的场均得分位居第一，Suns 和 Nuggets 紧随其后。")
    add_case(story, styles, "案例 4：球员单场得分 Top 10", "单场得分最高的 10 名球员是谁？", "SELECT player_name AS 球员, team_abbreviation AS 球队, game_id AS 比赛ID, pts AS 得分 FROM player_game_stats WHERE pts IS NOT NULL ORDER BY pts DESC LIMIT 10;", player_top, "Kobe Bryant 的 81 分位列第一，Devin Booker 的 70 分位列第二；Top 10 中 Kobe Bryant 多次出现。")
    add_case(story, styles, "案例 5：赛季场均总得分趋势", "不同赛季的场均总得分趋势如何变化？", "SELECT season AS 赛季, ROUND(AVG(total_points),2) AS 场均总得分 FROM games WHERE total_points IS NOT NULL GROUP BY season ORDER BY season LIMIT 8;", season_points, "2003 到 2010 年场均总得分从 186.00 上升到 200 分左右，整体反映进攻产出提高。")

    story.append(p("九、大模型使用说明", styles["H1"]))
    story.append(df_table(pd.DataFrame([
        ["模型名称", "默认 deepseek-v4-flash，可通过 DEEPSEEK_MODEL 环境变量切换。"],
        ["接口方式", "OpenAI 兼容方式，base_url 为 https://api.deepseek.com。"],
        ["使用环节", "自然语言问题理解、SQL 生成、SQL 查询结果中文解释。"],
        ["关键控制", "temperature=0，提示词要求只输出 SQL，SQL 安全模块二次检查。"],
        ["人工修改", "人工编写数据清洗、建库、SQL 安全、错误处理、界面展示和报告内容。"],
    ], columns=["项目", "说明"]), [1.4, 4.9]))

    story.append(p("十、运行步骤与复现说明", styles["H1"]))
    story.append(code_block(
        """
cd /Users/whe/Desktop/BBB
source .venv/bin/activate
python src/download_data.py
python src/preprocess.py
python src/build_database.py
python src/smoke_test.py
streamlit run src/app.py
        """,
        styles,
    ))
    story.append(p("如果需要启用 DeepSeek 智能问答，需要复制 .env.example 为 .env，并填写新的 DeepSeek API Key。真实 key 不写入报告和 Git。", styles["Body"]))

    story.append(p("十一、测试与验收结果", styles["H1"]))
    story.append(df_table(pd.DataFrame([
        ["依赖导入", "python src/smoke_test.py", "通过，关键依赖均可导入。"],
        ["数据库检查", "python src/smoke_test.py", "通过，检测到 6 张表和 26622 场比赛。"],
        ["SQL 安全检查", "python src/smoke_test.py", "通过，DROP TABLE 等危险语句被拒绝。"],
        ["Streamlit 页面", "streamlit run src/app.py", "通过，本地健康检查返回 ok。"],
        ["无 API Key 情况", "python src/agent.py", "通过，提示配置 DEEPSEEK_API_KEY，不直接崩溃。"],
    ], columns=["测试项", "命令/方式", "结果"]), [1.4, 1.8, 3.1]))

    story.append(p("十二、总结", styles["H1"]))
    story.append(p("本实验完成了从 NBA 公开数据集下载、pandas 清洗、SQLite 建模、SQL 查询验证，到 LangChain + DeepSeek Data Agent 和 Streamlit 可视化展示的完整流程。系统能够根据中文业务问题生成只读 SQL，执行真实数据库查询，并基于查询结果生成中文解释。实验过程中重点保证了数据链路可复现、SQL 查询结果真实、API Key 不泄露、危险 SQL 被拦截，符合课程对数据处理、建库、查询、智能体和可视化展示的综合要求。", styles["Body"]))

    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=letter,
        rightMargin=0.8 * inch,
        leftMargin=0.8 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.7 * inch,
        title="实验7 NBA 数据分析智能体实验报告",
        author="何后天、邹传涛、彭泽喜",
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(OUT_PATH)


if __name__ == "__main__":
    main()
