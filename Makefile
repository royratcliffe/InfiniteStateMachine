PYTHON=python

.PHONY: prettify-json extract-st update-st

# Prettify *staged* JSON files in the project directory. Run `git config
# core.hooksPath .githooks` to enable the pre-commit hook for
# prettifying JSON files.
prettify-json:
	$(PYTHON) ./scripts/prettify_json.py

extract-st:
	$(PYTHON) ./scripts/extract_st.py

update-st:
	$(PYTHON) ./scripts/update_st.py
