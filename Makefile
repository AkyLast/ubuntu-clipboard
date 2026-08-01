APP_NAME = ubuntu-clipboard
VERSION = 1.0.0
BUILD_DIR = build
DIST_DIR = dist

.PHONY: all clean lint test package install

all: clean lint test package

clean:
	@echo "Limpando artefatos antigos..."
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	@echo "Instalando dependências de desenvolvimento..."
	pip install -r requirements-dev.txt

lint:
	@echo "Executando linter (Flake8)..."
	flake8 src/ tests/ clipboard.py setup_autostart.py --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics

test:
	@echo "Executando suite de testes (Pytest)..."
	pytest tests/ -v

package:
	@echo "Empacotando a versão $(VERSION)..."
	mkdir -p $(DIST_DIR)
	zip -r $(DIST_DIR)/$(APP_NAME)-$(VERSION).zip clipboard.py setup_autostart.py src/ requirements.txt README.md docs/ Makefile
	@echo "✅ Empacotamento concluído em $(DIST_DIR)/$(APP_NAME)-$(VERSION).zip"
	@echo "Para criar um Release no GitHub, suba este zip na interface gráfica de Releases."
