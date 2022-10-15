SHELL := /bin/bash


install:
	curl -sSL https://install.python-poetry.org | python3 -
	cd scrape_lambda && poetry install --no-root
	cd report_lambda && poetry install --no-root


freeze: install
	cd scrape_lambda && poetry export --without-hashes --format=requirements.txt > requirements.txt
	cd report_lambda && poetry export --without-hashes --format=requirements.txt > requirements.txt


build: freeze
	-rm scrape_lambda/_lambda_payload.zip
	-rm -r scrape_lambda/_build
	mkdir -p scrape_lambda/_build
	cd scrape_lambda && poetry run pip install -r requirements.txt -t _build/
	cd scrape_lambda/_build && zip -r ../_lambda_payload.zip * 
	cd scrape_lambda/src && zip -ur ../_lambda_payload.zip *	
	
	-rm report_lambda/_lambda_payload.zip
	-rm -r report_lambda/_build
	mkdir -p report_lambda/_build
	cd report_lambda && poetry run pip install -r requirements.txt -t _build/
	#mkdir -p report_lambda/_assets
	#curl https://files.pythonhosted.org/packages/95/2f/0644216547beb6b6b6ffab234a4eceb5bcba8b4a859676898027f5d57d06/numpy-1.23.4-pp38-pypy38_pp73-win_amd64.whl -sSL -C - -o report_lambda/_assets/numpy.whl
	#curl https://files.pythonhosted.org/packages/91/e2/61f674f92e4a13a9c4b24260d2ca8c964e4affccfa3cb9fc2284996618a3/pandas-1.5.0-cp311-cp311-win_amd64.whl -sSL -C - -o report_lambda/_assets/pandas.whl
	#cd report_lambda/_assets && unzip -n numpy.whl && unzip -n pandas.whl && rm -r *.dist-info
	#cd report_lambda/_build && rm -rf numpy pandas && \
	#       	cp -r ../_assets/numpy . && cp -r ../_assets/pandas .
	#-cd report_lambda && poetry run pip install --platform manylinux2014_x86_64 --target=_build --implementation cp --python 3.9 --only-binary=:all: --upgrade numpy 
	#rm -r report_lambda/_build/*.dist-info
	cd report_lambda/_build && zip -r ../_lambda_payload.zip * 
	cd report_lambda/src && zip -ur ../_lambda_payload.zip *	


test-csvs: install
	cd scrape_lambda && source env.env && poetry run python3 src/pull_csvs.py


test-api: install
	cd scrape_lambda && source env.env && poetry run python3 src/hit_api.py


test-scrape: install
	cd scrape_lambda && source env.env && poetry run python3 src/lambda_handler.py


test-report: install
	cd report_lambda && source env.env && poetry run python3 src/lambda_handler.py


plan: build
	terraform plan


apply: plan
	terraform apply -auto-approve

clean:
	terraform destroy
