# Prompts

##

<!--
cd $PWD
dev.sh -p ~/code/
claude --dangerously-skip-permission
-->

Read ~/code/blog/posts/2026/proving-code-works-with-z3.md

Write a single-page data story `index.html` (use the data-story SKILL) that explains how to use Z3 to formally verify code, highlighting that this led to a successful issue submission and a PR, as documented in this repo.

Explain how this is relevant in the AI coding agent era where generation is cheap and verification is expensive.

Use the chats for


## Fix bug

<!--
cd ~/code/research/xarray-linspace/xarray
dev.sh codex --yolo --model gpt-5.5 --config model_reasoning_effort=medium
-->

<!-- Ideation: https://chatgpt.com/c/6a39c54b-ad50-83ee-b14d-98de7b789e34 -->

I've cloned https://github.com/pydata/xarray/ here. Fix https://github.com/pydata/xarray/issues/11397 - i.e. MINIMALLY and ELEGANTLY modify `xarray/indexes/range_index.py` as a small maintainer-friendly change so that

- it doesn't increase the number of code lines and
- works when num = 1, matching the NumPy behaviour, i.e. `np.linspace(0, 1, num=1)` returns `array([0.])`

I believe adding `and num > 1` to the `if` condition in `xarray/indexes/range_index.py` would fix this.

```python
if endpoint and num > 1:
    stop += (stop - start) / (num - 1)
```

Begin by writing a regression test like the below (but write it consistent wit the xarray test style) to verify that the bug is fixed:

```python
def test_range_index_linspace_num_1():
    index = RangeIndex.linspace(0.0, 1.0, num=1, dim="x")
    assert_array_equal(index.transform.generate_coords()["x"], np.array([0.0]))

def test_range_index_linspace_num_1_endpoint_false():
    index = RangeIndex.linspace(0.0, 1.0, num=1, endpoint=False, dim="x")
    assert_array_equal(index.transform.generate_coords()["x"], np.array([0.0]))
```

Run and test, make sure the tests fail (before the fix) only because of the bug and pass after the fix.

---

We ran this code on https://github.com/pydata/xarray - which I've now forked into https://github.com/sanand0/xarray

Update .git/config accordingly (or do whatever is needed) to commit and push the changes to my fork.

---

You made some changes to my configuration - as a result, I get the following error/warning when I try to push:

/home/vscode/.local/share/mise/installs/github-cli/2.95.0/gh_2.95.0_linux_amd64/bin/gh auth git-credential get: 1: /home/vscode/.local/share/mise/installs/github-cli/2.95.0/gh_2.95.0_linux_amd64/bin/gh: not found
/home/vscode/.local/share/mise/installs/github-cli/2.95.0/gh_2.95.0_linux_amd64/bin/gh auth git-credential store: 1: /home/vscode/.local/share/mise/installs/github-cli/2.95.0/gh_2.95.0_linux_amd64/bin/gh: not found

Let me know what the changes were and revert them.

---

Is it possible to fold the test into an existing test function so that the test code becomes more elegant and maintainable? If so, do that.

<!-- codex resume 019ef1b2-5aea-7221-982b-95c519fa8641 --yolo -->
