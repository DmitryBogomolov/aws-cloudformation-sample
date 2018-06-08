build:
	docker build -t xawscf .

run:
	docker run -dt --name xawscf xawscf

stop:
	docker rm -f xawscf

exec:
	docker exec -it xawscf sh

install:
	python3 setup.py install

develop:
	python3 setup.py develop

test:
	python3 test.py -v

test-ex:
	python3 setup.py test
