.PHONY: all build verify pdf clean

all: build

build:
	python3 scripts/build_and_verify.py

pdf: build

verify:
	python3 scripts/build_and_verify.py

clean:
	rm -f index.html cv.pdf media/preview-*.png
