# Prompts

<!--
dev.sh -v /home/sanand/code/blog:/home/sanand/code/blog:ro
-->

## Download songs (Claude Code - MiniMax M2.7)

Download the 20-50 most popular Tamil film songs of each date since 1950 and save them.

Search online for the most popular songs. See what's available from YouTube using `yt-dlp` (check length, prefer official sources), create a catalog called `songs.csv` with all song metadata that'll be useful.

Write a resumable script to download the songs using `yt-dlp` and save them in a structured way. Handle errors, retries, etc.

Run and test for a small batch. Fix any errors, optimize as required, take my help or my inputs if required - else fetch them all.

---

Now fetch them all.

---

Write and run a script that will capture a 50-second clip from each song starting at 30 seconds and save it as a separate file.

---

I interrupted to guide you on how to create the embeddings and the UMAP.
Read the content at /home/sanand/code/blog/analysis/embeddings and create the embeddings and UMAP based on that.
Reuse the code by copying it to the scripts/ directory and editing as required.
No need to create the visualizations yet. Just the embeddings and UMAP.

---

Gracefully stop the script so that the DuckDB database is not corrupted. Merge the .wal if required. Give me the instructions to run it manually. I will re-run this shortly.

---

<!-- DuckDB WAL needs checkpointing. Here's how to do it manually: ... -->

I did that. Modify the script to log progress so that tail -f tells me the extent of progress and restart the scripts.

---

Modify all code to use paths relative to the script rather than absolute paths.

---

Get more old songs. At least 15 per decade. Then proceed with embeddings and umap

---

Double-check the song metadata - especially year.
Research and fill out all the composer (music director), singer and lyricist names and standardize them. We want to be able to filter by these fields.
Songs may have multiple composers, singers, and lyricists - so allow that field to have multiple values. Ensure that each value is standardized and consistent across songs.

---

Create the visualization similar to how it's done in /home/sanand/code/blog/analysis/embeddings and generate the HTML file. A few notes on the visualization:

- Allow coloring by composer, lyricist, singer, decade.
- Allow filtering by composer, lyricist, singer.
- Brushing should show a WIDE table with movie, song, composer, singer, lyricist, year, duration -- all sortable. Clicking on any row should open the video on YouTube in a new tab.
- The date range slider should be a year slider that allows selecting a range of years (e.g. 1950-1960) and filters the songs accordingly.

Use right, bright colors.

---

Rename visualize.html to index.html. Do we need songs_backup.csv? If not, delete it to avoid confusion.
Are there any other files that we should delete because they do not form any part of the workflow, e.g backup files? If so, delete them.
Create a comprehensive and useful README.md.

<!-- claude --resume f4d3a74b-0bc8-4431-8084-f56be44a4a53 -->
