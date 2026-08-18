.PHONY: demo test validate package editor

demo:
	python -m archi_studio.cli build examples/sample_input --out examples/sample_output --non-interactive

test:
	python -m pytest

validate:
	./scripts/validate.sh

package:
	./scripts/package_skill.sh

editor:
	python -m archi_studio.cli serve-editor examples/sample_output/interactive_editor.html
