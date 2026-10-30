.PHONY: all build verify pdf clean

all: build

build:
	python3 scripts/build_and_verify.py

pdf: build

verify:
	python3 scripts/build_and_verify.py

clean:
	rm -f index.html index-cn.html "CV Sisheng Chris Zhang.pdf" "CV 简历 张斯盛 西班牙庞培法布拉大学博士.pdf" cv-bilingual.pdf media/preview-*.png
