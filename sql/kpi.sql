-- View KPI Project 14. Dijalankan oleh src/04_sql_kpi.py.
CREATE OR REPLACE VIEW v_fb_er AS
SELECT post_id, type, paid_label, hour_bucket, weekday, hour, reach, total,
       total * 1.0 / reach AS er
FROM fb_posts;

CREATE OR REPLACE VIEW v_fb_type_median AS
SELECT type, COUNT(*) AS n, median(er) AS median_er
FROM v_fb_er
GROUP BY type
ORDER BY median_er DESC, type ASC;

CREATE OR REPLACE VIEW v_yt_er AS
SELECT video_id, keyword, likes, comments, views,
       (likes + comments) * 1.0 / views AS er
FROM yt_videos;

CREATE OR REPLACE VIEW v_yt_keyword_median AS
SELECT keyword, COUNT(*) AS n, median(er) AS median_er
FROM v_yt_er
GROUP BY keyword
ORDER BY median_er DESC, keyword ASC;
