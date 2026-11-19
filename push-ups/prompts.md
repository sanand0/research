# Prompts

## Identify quality and approach, 19 Nov 2026

<!--
cd ~/code/research/
claude --model opus --effort high
-->

I have videos of me doing push-ups in ~/r2/media/2026-11-push-ups/ which is synced to https://media.s-anand.net/2026-11-push-ups/.

I want to identify the quality of my push-ups.
I want to find the best library, tool, technique, approach, ... to do this.
I want the output as a single HTML page that shows the quality score of each push-up and the overall score across push-ups for each of the videos, with a visual annotation that proves the score.

By quality, I broadly refer to:

- how straight my back is, in line with how it's supposed to be in a push-up, i.e. is the angle of the back correct
- how low I go
- how straight my arms are
- how straight my head is
- etc.


What would be great is if there were a set of lines drawn through the relevant frames of the video that show the angles, height, etc. along with the metrics - as an overlap. That way, I'd be able to see the quality of each push-up visually, and just jump to any specific push-up from a metrics table.

But, of course, to do this, we need to identify the best approach, library, tool, technique, ... to do this.

I would also like a comparison of the approaches you used - so I should be able to toggle between the different approaches in the HTML file and see the differences in the results as well as the quality of the results. Make it easy for me to compare side-by-side, or overlap / swipe, or animations, or any other way of making it easy to compare the quality of different approaches.

Plan, experiment, review, iterate, and use relevant skills. Prefer re-using knowledge / research / code rather than inventing from scratch.

Save everything in push-ups/.

---

This rebooted my system. Maybe the system got too hot? Or some GPU issue? Diagnose, avoid repetition, and continue.

---

Pause work for a bit and we can continue later.

---

Continue

---

Crashed again! Heated up, I guess. Continue, carefully.

---

Here is a note offered by a side agent:

> Heads up · The rising form scores (about 68 → 76 → 85) could partly come from camera position and clothing changing each day, not only from better push-ups.
>
> **Score trend may reflect camera setup, not just form**
> - The scores come from **2D angles** measured on the flat video image, mainly the bend at the hips (the "body line" score), which drives most of the result.
> - 2D angles shift if the camera sits at a slightly different height, distance or tilt each day. A camera that isn't square to your side can make a straight body look bent, or the reverse.
> - Each session also has different clothes and light (dark shorts on 7 Nov, white shorts against a bright window on 15 Nov). The pose models guess where your hip is under the shorts, so that guess can move too.
> - So a better score may be real, or partly a measurement change.
> - **Worth asking the main agent to check this**: compare your plank at the top of each rep across days, or keep the camera in a fixed, marked spot for future videos.

FYI - I do know that especially betwen the first and the remainining sessions, I consciously improved my form.

---

Continue

---

Amend the commit to use maximally compressed .webp files and remove anything that's not necessary. Compress data files as well reasonably. Do we need to commit the model files? Think about it - and, if you think it's important, happy to keep that in GitHub releases rather than as a commit.

---

Create a summary video of my push-up sessions over the 4 days, compressed like how `videocompress` in ~/code/scripts/setup.fish compresses, at ~/r2/media/push-ups/2026-11-push-ups-summary.webm.
Maybe take 6 seconds from the second push-up onwards from each day and stitch them together.
Before each video, flash the date and the overall score for that day and any other highlights. For 2 seconds, maybe. Design for clarity - people should be able to absorb the info in the 2 seconds they have. A continued story (e.g. hips sagged, then flipped to a pike, overcorrected, etc.) matters more than numbers.
Make sure the overlay lines, angles, annotations, etc. that are shown in the HTML are present just like in the HTML.
No commit required.

<!-- claude --resume 0f39461f-8e4b-4b64-a6be-31d50d26cd16 -->
