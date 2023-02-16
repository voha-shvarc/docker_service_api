VENV := venv
PIDS = $(shell pidof python3)
all: venv

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

venv: $(VENV)/bin/activate
	@echo "run venv"

run: venv shutdown worker
	./$(VENV)/bin/python3 app.py

shutdown:
	@if [ -n "$(PIDS)" ]; then\
  	  kill $(PIDS);\
  	  echo "Successfully killed";\
  	else\
  	  echo "No running python3 processes were found";\
  	fi

worker: venv
	@./$(VENV)/bin/python3 worker.py > ./.worker.log 2>&1 &
	@echo "run worker"

clean:
	rm -rf $(VENV)
	find . -type f -name '*.pyc' -delete

.PHONY: all venv run clean shutdown