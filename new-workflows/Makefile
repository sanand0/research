# Creative Makefile: Data Pipeline Orchestration
# Demonstrates using Make for workflow automation with dependency tracking

.PHONY: all clean demo help

# Default data source
USERNAME ?= torvalds

# File targets with automatic dependency tracking
all: demo

help: ## Show this help message
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  Creative Makefile: Workflow Orchestration                    ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

demo: demo-data.svg demo-data.wav ## Run complete multi-format visualization demo
	@echo "✓ Demo complete! All artifacts generated."
	@echo "  Files: demo-data.json, demo-data.svg, demo-data.wav"

live: ## Fetch live GitHub data and visualize (usage: make live USERNAME=torvalds)
	@python3 live-dashboard.py $(USERNAME)

# SVG depends on JSON - will only regenerate if JSON changes
demo-data.svg: demo-data.json visualize.py
	@echo "→ Generating SVG from JSON data..."
	@python3 visualize.py demo-data.json > /dev/null 2>&1
	@echo "✓ SVG generated: $@"

# WAV depends on JSON - demonstrates smart rebuilding
demo-data.wav: demo-data.json visualize.py
	@echo "→ Generating audio sonification..."
	@python3 visualize.py demo-data.json > /dev/null 2>&1
	@echo "✓ Audio generated: $@"

# Show that Make tracks dependencies intelligently
test-incremental: ## Test incremental rebuilds (only rebuilds if JSON changes)
	@echo "First build (will generate all files):"
	@$(MAKE) demo
	@echo ""
	@echo "Second build (should skip - no changes):"
	@$(MAKE) demo
	@echo ""
	@echo "Now modifying JSON..."
	@touch demo-data.json
	@echo "Third build (will regenerate only dependent files):"
	@$(MAKE) demo

stats: demo-data.json ## Show statistics from JSON data using jq
	@echo "Data Statistics:"
	@echo "  Total months: $$(cat demo-data.json | jq '.data | length')"
	@echo "  Average response time: $$(cat demo-data.json | jq '[.data[].avg_response] | add / length | floor')ms"
	@echo "  Max response time: $$(cat demo-data.json | jq '[.data[].avg_response] | max')ms"
	@echo "  Min response time: $$(cat demo-data.json | jq '[.data[].avg_response] | min')ms"

ascii: demo-data.json ## Quick ASCII visualization using jq
	@echo "ASCII Visualization:"
	@cat demo-data.json | jq -r '.data[] | "\(.month): " + ("█" * (.avg_response / 10 | floor))'

clean: ## Remove generated files
	@rm -f demo-data.svg demo-data.wav
	@echo "✓ Cleaned generated files"

benchmark: ## Benchmark different visualization approaches
	@echo "Benchmarking visualization methods..."
	@echo ""
	@echo "1. Pure jq (fastest):"
	@time -f "  Time: %E" cat demo-data.json | jq -r '.data[] | "\(.month): " + ("█" * (.avg_response / 10 | floor))' > /dev/null
	@echo ""
	@echo "2. Python visualization (most features):"
	@time -f "  Time: %E" python3 visualize.py demo-data.json > /dev/null 2>&1
	@echo ""
	@echo "3. Full pipeline with SVG+Audio (most comprehensive):"
	@time -f "  Time: %E" $(MAKE) clean && $(MAKE) demo > /dev/null 2>&1

# Pattern rule: Convert any JSON to SVG
%.svg: %.json visualize.py
	@python3 visualize.py $< > /dev/null 2>&1

# Pattern rule: Convert any JSON to WAV
%.wav: %.json visualize.py
	@python3 visualize.py $< > /dev/null 2>&1

.DEFAULT_GOAL := help
