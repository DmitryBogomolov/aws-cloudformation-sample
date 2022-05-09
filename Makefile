name = xawscf

build:
	docker build -t $(name) .

remove:
	docker rmi $(name)

run:
	docker run -dt --name $(name) $(name)

stop:
	docker rm -f $(name)

exec:
	docker exec -it $(name) sh

make-env:
	python3 -m venv env

install-requirements:
	pip3 install -r requirements.txt
	pip3 install pylint

install:
	python3 setup.py install

develop:
	python3 setup.py develop

lint:
	pylint $(name)

test:
	python3 -m unittest discover -p "*_test.py" -v

test-ex:
	python3 setup.py test

run-test-command:
	docker run -it --rm $(name) /bin/sh -c "cd functions && xawscf process"
