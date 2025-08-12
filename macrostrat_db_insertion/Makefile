build:
	export CURRENT_DIR=$(shell pwd)
	docker rm -f db_insert 2>/dev/null || true
	docker build -t db_insert:latest .
	docker run -d -v $CURRENT_DIR:/working_dir/ --name=db_insert --entrypoint /bin/bash -p 9543:9543 db_insert:latest -c "sleep infinity"
	docker exec -it db_insert bash
