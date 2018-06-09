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

install:
	python3 setup.py install

develop:
	python3 setup.py develop

test:
	python3 test.py -v

test-ex:
	python3 setup.py test
