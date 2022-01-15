install:
	poetry build \
	&& cd dist \
	&& find *.whl | xargs pip install --user --force-reinstall \
	&& cd ../ \
	&& rm -rf dist
