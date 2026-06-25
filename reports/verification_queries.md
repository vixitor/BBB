# 数据库验证查询

## table_counts

```sql
SELECT 'teams' AS table_name, COUNT(*) AS row_count FROM teams
        UNION ALL SELECT 'games', COUNT(*) FROM games
        UNION ALL SELECT 'players', COUNT(*) FROM players
        UNION ALL SELECT 'rankings', COUNT(*) FROM rankings
        UNION ALL SELECT 'player_game_stats', COUNT(*) FROM player_game_stats;
```

| table_name | row_count |
| --- | --- |
| teams | 30 |
| games | 26622 |
| players | 7228 |
| rankings | 210313 |
| player_game_stats | 668339 |

## season_distribution

```sql
SELECT season, COUNT(*) AS games
        FROM games
        GROUP BY season
        ORDER BY season
        LIMIT 20;
```

| season | games |
| --- | --- |
| 2003 | 1385 |
| 2004 | 1362 |
| 2005 | 1432 |
| 2006 | 1419 |
| 2007 | 1411 |
| 2008 | 1425 |
| 2009 | 1424 |
| 2010 | 1422 |
| 2011 | 1104 |
| 2012 | 1420 |
| 2013 | 1427 |
| 2014 | 1418 |
| 2015 | 1416 |
| 2016 | 1405 |
| 2017 | 1382 |
| 2018 | 1378 |
| 2019 | 1241 |
| 2020 | 1220 |
| 2021 | 1389 |
| 2022 | 542 |

## top_team_avg_points

```sql
SELECT t.nickname AS team, ROUND(AVG(team_points), 2) AS avg_points
        FROM (
            SELECT home_team_id AS team_id, pts_home AS team_points FROM games
            UNION ALL
            SELECT visitor_team_id AS team_id, pts_away AS team_points FROM games
        ) s
        JOIN teams t ON t.team_id = s.team_id
        GROUP BY t.team_id, t.nickname
        ORDER BY avg_points DESC
        LIMIT 10;
```

| team | avg_points |
| --- | --- |
| Warriors | 107.5 |
| Suns | 106.47 |
| Nuggets | 106.19 |
| Thunder | 103.79 |
| Rockets | 103.78 |
| Lakers | 103.56 |
| Kings | 103.44 |
| Mavericks | 103.14 |
| Clippers | 102.84 |
| Raptors | 102.67 |
