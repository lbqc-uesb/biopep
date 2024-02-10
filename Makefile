# run options
query=""
receptor=""
site=""
task="task"
cutoff="30"

.PHONY:install
install:
	@./bin/install

.PHONY:run
run:
	@./bin/run -q $(query) -r $(receptor) -s $(site) -t $(task) -c $(cutoff)
