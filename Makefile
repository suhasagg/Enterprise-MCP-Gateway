up:
	docker compose up --build
down:
	docker compose down -v
python-test:
	cd python-gateway && pytest -q
java-test:
	cd java-services && mvn test
security-eval:
	cd evals && python security_eval.py
