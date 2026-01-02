
import json
import os
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

class Scraper:
    """
    Um scraper em Python usando Selenium para automatizar a coleta de dados de aulas
    de um portal educacional, replicando a funcionalidade de um script Puppeteer.
    """

    def __init__(self, project_root):
        self.project_root = project_root
        self.data_path = os.path.join(self.project_root, 'data')
        self.driver = None
        self.wait = None
        self.mapeamento_turmas = {}
        self.mapa_turmas_reverso = {} # NOVO: Para mapear nome curto -> nome completo
        self.turmas_para_coletar = []
        self.nome_professor = ""

        # NOVO: Para filtrar disciplinas já completas
        self.disciplinas_completas = set()
        self.dados_antigos_completos = []

    def _initialize_driver(self):
        """Inicializa o WebDriver do Selenium."""
        print("[Scraper] Inicializando o WebDriver do Chrome...")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless") # Descomente para rodar em segundo plano
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20) # Timeout padrão de 20 segundos
        except Exception as e:
            raise RuntimeError(f"Falha ao inicializar o WebDriver: {e}")

    def _analisar_aulas_existentes(self):
        """
        Lê 'aulas_coletadas.json', identifica disciplinas com 40h ou mais,
        e as adiciona à lista de exclusão para a coleta.
        """
        aulas_existentes_path = os.path.join(self.data_path, 'aulas_coletadas.json')
        if not os.path.exists(aulas_existentes_path):
            print("[Análise Prévia] Arquivo 'aulas_coletadas.json' não encontrado. Todas as disciplinas serão coletadas.")
            return

        print("[Análise Prévia] Lendo 'aulas_coletadas.json' para otimizar a coleta...")
        with open(aulas_existentes_path, 'r', encoding='utf-8-sig') as f:
            aulas_existentes = json.load(f)

        # Contagem de aulas por (turma, disciplina)
        contagem = {}
        for aula in aulas_existentes:
            chave = (aula.get('turma'), aula.get('componenteCurricular'))
            if all(chave):
                contagem[chave] = contagem.get(chave, 0) + 1
        
        # Identifica disciplinas completas (>= 40h)
        for chave, total_aulas in contagem.items():
            if total_aulas >= 40:
                self.disciplinas_completas.add(chave)

        if not self.disciplinas_completas:
            print("[Análise Prévia] Nenhuma disciplina com 40h ou mais encontrada. Todas serão coletadas.")
            return

        print(f"[Análise Prévia] {len(self.disciplinas_completas)} disciplina(s) com carga horária completa serão ignoradas na coleta.")
        
        # Salva a lista de disciplinas ignoradas em um CSV
        csv_path = os.path.join(self.data_path, 'disciplinas_ignoradas_coleta.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            f.write("turma;disciplina\n")
            for turma, disciplina in sorted(list(self.disciplinas_completas)):
                f.write(f'"{turma}";"{disciplina}"\n')
        print(f"[Análise Prévia] Lista de disciplinas ignoradas salva em: {csv_path}")

        # Guarda os dados das disciplinas completas para adicionar ao resultado final
        self.dados_antigos_completos = [
            aula for aula in aulas_existentes if (aula.get('turma'), aula.get('componenteCurricular')) in self.disciplinas_completas
        ]
        print(f"[Análise Prévia] {len(self.dados_antigos_completos)} registros de aulas completas foram preservados.")

    def _load_configs(self):
        """Carrega os arquivos de configuração necessários."""
        print(f"[Scraper] Lendo configurações de: {self.data_path}")
        try:
            with open(os.path.join(self.data_path, 'config.json'), 'r', encoding='utf-8-sig') as f:
                config_data = json.load(f)
            with open(os.path.join(self.data_path, 'horarios_semanais_oficial.json'), 'r', encoding='utf-8-sig') as f:
                horarios_data = json.load(f)
            with open(os.path.join(self.data_path, 'turmas_com_disciplinas.json'), 'r', encoding='utf-8-sig') as f:
                self.mapeamento_turmas = json.load(f)
            with open(os.path.join(self.data_path, 'mapa_turmas.json'), 'r', encoding='utf-8-sig') as f:
                mapa_turmas_data = json.load(f)

            # Executa a análise das aulas existentes ANTES de prosseguir
            self._analisar_aulas_existentes()

            self.nome_professor = config_data.get('professor')
            if not self.nome_professor:
                raise ValueError('Nome do professor não encontrado em data/config.json')

            # CORREÇÃO: Acessa os dados de horário considerando que pode ser uma lista.
            # Baseado na lógica do scraper.js, que verifica se horariosData é um array.
            if isinstance(horarios_data, list) and horarios_data:
                # Pega o primeiro item da lista, que deve conter os dados dos professores.
                horarios_do_professor = horarios_data[0].get('professores', {}).get(self.nome_professor)
                if horarios_do_professor and 'turmas' in horarios_do_professor:
                    self.turmas_para_coletar = list(horarios_do_professor['turmas'].keys())
                else:
                    horarios_do_professor = None # Garante que não prossiga se não encontrar
            else:
                horarios_do_professor = None

            if not self.turmas_para_coletar or horarios_do_professor is None:
                 raise ValueError(f"Nenhuma turma encontrada para o professor '{self.nome_professor}' em horarios_semanais_oficial.json")
            
            # NOVO: Cria o mapa reverso para encontrar o nome completo a partir do nome curto
            # Ex: {'1º DS': 'EMI-INT CT DES SIST-1ª SÉRIE -I-A'}
            self.mapa_turmas_reverso = {v: k for k, v in mapa_turmas_data.items()}

            print(f"[Scraper] Turmas a serem coletadas: {', '.join(self.turmas_para_coletar)}")

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {e.filename}")
        except (json.JSONDecodeError, ValueError) as e:
            raise RuntimeError(f"Erro ao ler ou processar arquivos de configuração: {e}")


    def _take_screenshot(self, name):
        """Tira um screenshot da tela atual para depuração."""
        if not self.driver:
            print("AVISO: Não foi possível tirar screenshot porque o navegador não foi inicializado.")
            return

        # Cria o diretório de screenshots se ele não existir
        screenshots_dir = os.path.join(self.project_root, 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)

        safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        path = os.path.join(screenshots_dir, f"erro_{safe_name}.png")
        try:
            self.driver.save_screenshot(path)
            print(f"Screenshot de erro salvo em: {path}")
        except Exception as e:
            print(f"Falha ao salvar screenshot: {e}")

    def _login(self, url, credenciais):
        """Navega para a URL e realiza o login."""
        if not credenciais or not credenciais.get('username') or not credenciais.get('password'):
            raise ValueError('As credenciais (usuário/senha) não foram fornecidas.')

        print(f"Navegando para {url}...")
        self.driver.get(url)

        time.sleep(0.5) # Pausa para observação
        print("Preenchendo formulário de login...")
        self.wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(credenciais['username'])
        time.sleep(0.5)
        self.driver.find_element(By.ID, 'password').send_keys(credenciais['password'])
        
        print("Clicando no botão de login...")        
        self.driver.find_element(By.CSS_SELECTOR, 'button[ng-click="logar(login)"]').click()

    def _select_profile_and_institution(self):
        """Seleciona o perfil de professor e a instituição."""
        try:
            # Etapa: Escolher Perfil
            print("Aguardando seleção de perfil 'Professor(a)'...")
            profile_selector = (By.CSS_SELECTOR, 'a.collection-item[ng-click="selecionarPerfil(perfil)"]')
            time.sleep(0.5)
            self.wait.until(EC.element_to_be_clickable(profile_selector)).click()
            print("Perfil 'Professor(a)' selecionado.")

            # Etapa: Escolher Instituição (dentro de um iframe)
            print("Aguardando iframe de seleção de instituição...")
            iframe_selector = (By.ID, 'iframe-container')
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(iframe_selector))
            
            print("Dentro do iframe, clicando no botão 'ABRIR'...")
            # Em Selenium, usamos XPath para encontrar um elemento pelo texto contido nele
            open_button_selector = (By.XPATH, "//button[contains(., 'ABRIR')]")
            time.sleep(0.5)
            self.wait.until(EC.element_to_be_clickable(open_button_selector)).click()
            
            # Sair do iframe atual para o contexto da página principal
            self.driver.switch_to.default_content()
            print("Botão 'ABRIR' clicado. Retornando ao conteúdo principal.")

        except TimeoutException as e:
            self._take_screenshot("selecao_perfil_instituicao")
            raise TimeoutException(f"Tempo esgotado ao selecionar perfil ou instituição: {e.msg}")

    def _extract_table_data(self):
        """Extrai os dados da tabela de aulas na página atual."""
        try:
            # Espera o spinner de loading desaparecer
            spinner_selector = (By.CSS_SELECTOR, "svg.animate-spin")
            print("[Extração] Aguardando tabela carregar (spinner desaparecer)...")
            self.wait.until(EC.invisibility_of_element_located(spinner_selector))
        except TimeoutException:
            print("[Extração] AVISO: Spinner de loading não desapareceu no tempo esperado. A tabela pode estar vazia ou já carregada.")

        # Verifica se há a mensagem "Nenhum registro encontrado"
        try:
            if self.driver.find_element(By.XPATH, "//td[contains(., 'Nenhum registro encontrado')]" ).is_displayed():
                print("[Extração] Mensagem 'Nenhum registro encontrado' detectada.")
                return []
        except NoSuchElementException:
            pass # É o esperado, significa que a tabela tem dados

        # Extrai os dados
        linhas_dados = []
        # CORREÇÃO: Re-localiza a tabela a cada chamada para evitar StaleElementReferenceException.
        # A tabela é buscada aqui, e suas linhas e cabeçalhos são processados imediatamente.
        try:
            table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            headers = [th.text.strip() for th in table.find_elements(By.CSS_SELECTOR, "thead th")]
        except StaleElementReferenceException:
            print("[Extração] AVISO: A tabela ficou obsoleta durante a extração. Tentando novamente...")
            table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            headers = [th.text.strip() for th in table.find_elements(By.CSS_SELECTOR, "thead th")]
        header_map = {
            'Data da Aula': 'dataAula',
            'Horário (inicial ~ final)': 'horario',
            'Turma': 'turma',
            'Componente': 'componenteCurricular',
            'Data de Cadastro da Aula': 'data_cadastro',
            'Situação': 'status'
        }

        for linha in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
            celulas = linha.find_elements(By.TAG_NAME, "td")
            if not celulas: continue
            
            # Pula linhas que são apenas placeholders de "nenhum registro"
            if len(celulas) == 1 and "Nenhum registro encontrado" in celulas[0].text:
                continue

            linha_dict = {}
            for i, header_text in enumerate(headers):
                key = header_map.get(header_text)
                if key and i < len(celulas):
                    linha_dict[key] = celulas[i].text.strip()
            linhas_dados.append(linha_dict)
        
        return linhas_dados

    def _collect_with_pagination(self):
        """
        Coleta dados de todas as páginas da tabela, navegando pela paginação.
        """
        all_data = []
        page_count = 1
        
        # Otimização: Tenta configurar a paginação para 50 registros por página
        try:
            print("[Paginação] Tentando configurar para 50 registros por página...")
            # Encontra o botão do combobox que controla os registros por página
            registros_combobox = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@role='combobox' and contains(., 'Registros')]")
            ))
            
            # Só clica se não estiver já em 50
            if "50 Registros" not in registros_combobox.text:
                self.driver.execute_script("arguments[0].click();", registros_combobox)
                time.sleep(0.5) # Pausa para o dropdown abrir
                
                # Clica na opção "50"
                option_50 = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'z-50')]//button[contains(., '50')]")
                ))
                self.driver.execute_script("arguments[0].click();", option_50)
                print("[Paginação] Configurado para 50 registros. Aguardando recarregamento...")
                # Espera a tabela recarregar após a mudança
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "svg.animate-spin")))
            else:
                print("[Paginação] Já está configurado para 50 registros por página.")
        except TimeoutException:
            print("[Paginação] AVISO: Não foi possível configurar para 50 registros. Continuando com o padrão.")

        while True:
            print(f"[Paginação] Coletando dados da página {page_count}...")
            
            # Extrai os dados da página atual
            data_on_page = self._extract_table_data()
            # CORREÇÃO: A condição foi simplificada para `if data_on_page:`
            # para garantir que qualquer dado retornado pela extração (incluindo aulas
            # com status "Excluída") seja contabilizado e processado.
            if data_on_page: 
                all_data.extend(data_on_page)
                print(f"[Paginação] {len(data_on_page)} aulas encontradas na página {page_count}. Total até agora: {len(all_data)}")
            else:
                print("[Paginação] Nenhuma aula encontrada na página atual.")

            # Verifica se o botão "Próxima" existe e está habilitado
            try:
                # Localiza o botão que contém o texto "Próxima"
                next_button_xpath = "//button[contains(., 'Próxima')]"
                next_button = self.wait.until(EC.presence_of_element_located((By.XPATH, next_button_xpath)))
                
                # O atributo 'disabled' determina se o botão está clicável
                is_disabled = next_button.get_attribute('disabled')
                
                if is_disabled:
                    print("[Paginação] Botão 'Próxima' está desabilitado. Fim da coleta.")
                    break
                
                # Se não estiver desabilitado, clica para ir para a próxima página
                print("[Paginação] Clicando no botão 'Próxima'...")
                time.sleep(0.5) # Pausa antes do clique para estabilidade
                self.driver.execute_script("arguments[0].click();", next_button)
                page_count += 1
                
                # Aguarda o recarregamento da tabela (o spinner é um bom indicador)
                # Esta espera é crucial para evitar coletar dados antigos antes da página atualizar
                spinner_selector = (By.CSS_SELECTOR, "svg.animate-spin")
                # Pausa após o clique para dar tempo do spinner aparecer
                time.sleep(1)
                self.wait.until(EC.invisibility_of_element_located(spinner_selector))

            except TimeoutException:
                # Se o botão "Próxima" não for encontrado, significa que não há mais páginas
                print("[Paginação] Botão 'Próxima' não encontrado. Fim da coleta.")
                break
            except Exception as e:
                print(f"[Paginação] Erro inesperado ao tentar paginar: {e}")
                break
        
        return all_data

    def _navigate_and_collect(self):
        """Navega pelas turmas e disciplinas, coletando os dados."""
        all_collected_data = []

        # Espera o iframe das turmas aparecer
        turmas_iframe_selector = (By.CSS_SELECTOR, 'iframe[src*="listagem-turmas"]')
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(turmas_iframe_selector))
        print("Iframe de listagem de turmas carregado.")

        for nome_turma_curto in self.turmas_para_coletar:
            print(f"\n--- [LOOP] Iniciando coleta para a turma: {nome_turma_curto} ---")
            
            # CORREÇÃO: Usa o mapa reverso para obter o nome completo da turma.
            nome_completo_turma = self.mapa_turmas_reverso.get(nome_turma_curto)
            if not nome_completo_turma:
                print(f"[LOOP] AVISO: Mapeamento não encontrado para a turma '{nome_turma_curto}'. Pulando...")
                continue

            print(f"[LOOP] Nome completo na página: '{nome_completo_turma}'")

            # Encontra as disciplinas para a turma atual usando o nome completo
            # CORREÇÃO 1: Usar "nomeTurma" para corresponder ao JSON.
            turma_disciplinas_info = next((turma for turma in self.mapeamento_turmas if turma.get("nomeTurma") == nome_completo_turma), None)
            
            # CORREÇÃO 2: Extrair apenas o nome da disciplina do objeto.
            disciplinas_da_turma = [d.get('nomeDisciplina') for d in turma_disciplinas_info.get('disciplinas', [])] if turma_disciplinas_info else []

            print(f"[LOOP] Disciplinas a coletar: {', '.join(disciplinas_da_turma)}")
            
            # A cada iteração de disciplina, a página recarrega.
            # Então, para cada disciplina, precisamos re-localizar o card correto.
            for i, nome_disciplina in enumerate(disciplinas_da_turma):
                print(f"\n--- [SUB-LOOP] Processando disciplina: '{nome_disciplina}' ({i+1}/{len(disciplinas_da_turma)}) ---")

                # NOVO: Verifica se a disciplina está na lista de exclusão
                chave_disciplina = (nome_completo_turma, nome_disciplina)
                if chave_disciplina in self.disciplinas_completas:
                    print(f"[SUB-LOOP] IGNORANDO: A disciplina '{nome_disciplina}' da turma '{nome_turma_curto}' já possui 40h ou mais.")
                    continue # Pula para a próxima disciplina

                
                try:
                    # Re-localiza todos os cards da turma e seleciona o da disciplina atual
                    card_xpath = f"//div[div/h3[normalize-space()='{nome_completo_turma}'] and div/p[normalize-space()='{nome_disciplina}']]"
                    card = self.wait.until(EC.presence_of_element_located((By.XPATH, card_xpath)))

                    # Clica em "Registro de aulas" dentro do card correto
                    time.sleep(0.5)
                    registro_aulas_link = card.find_element(By.XPATH, ".//p[normalize-space()='Registro de aulas']")
                    self.driver.execute_script("arguments[0].click();", registro_aulas_link) # Click com JS para evitar problemas de visibilidade
                    print("[SUB-LOOP] Clicou em 'Registro de aulas'.")

                    # Coleta com paginação
                    dados_disciplina = self._collect_with_pagination() # SUBSTITUÍDO
                    all_collected_data.extend(dados_disciplina)
                    print(f"[SUB-LOOP] {len(dados_disciplina)} aulas coletadas para '{nome_disciplina}'.")

                    # Voltar para a lista de disciplinas
                    print("[SUB-LOOP] Voltando para a lista de turmas/disciplinas...")
                    time.sleep(0.5)
                    voltar_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Voltar"]')))
                    self.driver.execute_script("arguments[0].click();", voltar_btn)
                    
                    # Espera a lista de cards recarregar
                    self.wait.until(EC.presence_of_element_located((By.XPATH, f"//h3[normalize-space()='{nome_completo_turma}']")))
                    print("[SUB-LOOP] Retornou à lista.")

                except (TimeoutException, StaleElementReferenceException) as e:
                    print(f"[SUB-LOOP] Erro ao processar a disciplina '{nome_disciplina}': {e}")
                    self._take_screenshot(f"erro_disciplina_{nome_turma_curto}_{nome_disciplina}")
                    
                    # Tenta voltar para a lista para continuar com a próxima disciplina/turma
                    try:
                        print("[SUB-LOOP] Tentando voltar para a lista (após erro)...")
                        time.sleep(0.5)
                        voltar_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Voltar"]')))
                        self.driver.execute_script("arguments[0].click();", voltar_btn)
                        self.wait.until(EC.presence_of_element_located((By.XPATH, f"//h3[normalize-space()='{nome_completo_turma}']")))
                        print("[SUB-LOOP] Retornou à lista (após erro).")
                    except Exception as nav_error:
                        print(f"Falha crítica ao tentar voltar para a lista após erro: {nav_error}. Interrompendo o scraper.")
                        raise
                    continue # Pula para a próxima disciplina
        
        # Ao final, retorna para o contexto principal para que o chamador possa continuar
        self.driver.switch_to.default_content()
        return all_collected_data
    
    def capturar_dados(self, url, credenciais, disciplina_alvo=None):
        """
Método principal que orquestra todo o processo de scraping.
        """
        # MODIFICAÇÃO: Não carrega mais configs nem inicializa o driver aqui.
        # Isso será feito pelo script que o chama.
        try:
            self._login(url, credenciais)
            self._select_profile_and_institution()

            # Se uma disciplina específica for fornecida, a lógica de navegação mudará.
            # Esta parte pode ser expandida se a navegação direta for necessária.
            # Por enquanto, a lógica principal de coleta já itera sobre as turmas.
            collected_data = self._navigate_and_collect()
            
            # NOVO: Adiciona os dados das disciplinas que já estavam completas de volta ao resultado
            if self.dados_antigos_completos:
                print(f"\n[Consolidação] Adicionando {len(self.dados_antigos_completos)} registros de aulas (que foram ignoradas na coleta) ao resultado final.")
                collected_data.extend(self.dados_antigos_completos)

            print(f"\n--- FIM DO SCRAPING ---")
            print(f"Total de aulas coletadas de todas as turmas: {len(collected_data)}")
            return collected_data

        except Exception as e:
            print(f"Ocorreu um erro fatal durante o scraping: {e}")
            self._take_screenshot("erro_fatal")
            # Re-lança a exceção para que o chamador saiba que algo deu errado
            raise

        # MODIFICAÇÃO: A responsabilidade de fechar o driver passa a ser do chamador.
        # finally:
        #     if self.driver:
        #         print("Fechando o navegador.")
        #         self.driver.quit()

    def coletar_dados_disciplina(self, nome_turma_completo, nome_disciplina_completo):
        """
        Coleta dados de uma única disciplina específica. Assume que o driver já está logado.
        """
        try:
            # O login e a seleção de perfil/instituição agora são feitos pelo chamador.

            # Espera o iframe das turmas aparecer
            turmas_iframe_selector = (By.CSS_SELECTOR, 'iframe[src*="listagem-turmas"]')
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(turmas_iframe_selector))
            print(f"Iframe de listagem de turmas carregado. Navegando para a disciplina '{nome_disciplina_completo}'...")

            # OTIMIZAÇÃO: Verifica primeiro o cartão de resumo de aulas pendentes.
            try:
                # XPath para encontrar o número dentro do card "Aulas aguardando confirmação"
                pending_count_xpath = "//div[div[normalize-space()='Aulas aguardando confirmação']]//div[contains(@class, 'font-bold')]"
                pending_count_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, pending_count_xpath)))
                pending_count = int(pending_count_element.text.strip())
                
                print(f"  -> Verificação rápida: Encontradas {pending_count} aulas aguardando confirmação no resumo.")

                # Se não houver aulas pendentes, não há necessidade de varrer a tabela.
                if pending_count == 0:
                    print("  -> Nenhuma aula pendente encontrada. Retornando lista vazia para economizar tempo.")
                    self.driver.switch_to.default_content()
                    return []
            except (TimeoutException, ValueError) as e:
                # Se os cartões de resumo não forem encontrados ou o valor não for um número,
                # o script continua com a varredura completa da tabela como fallback.
                print(f"  -> AVISO: Não foi possível verificar o resumo de aulas pendentes (erro: {e}).")
                print("     -> Prosseguindo com a varredura completa da tabela como garantia.")
                pass


            # Navega para a disciplina e coleta os dados
            card_xpath = f"//div[div/h3[normalize-space()='{nome_turma_completo}'] and div/p[normalize-space()='{nome_disciplina_completo}']]"
            card = self.wait.until(EC.presence_of_element_located((By.XPATH, card_xpath)))

            registro_aulas_link = card.find_element(By.XPATH, ".//p[normalize-space()='Registro de aulas']")
            self.driver.execute_script("arguments[0].click();", registro_aulas_link)
            print("Clicou em 'Registro de aulas'.")

            dados_disciplina = self._collect_with_pagination()
            print(f"{len(dados_disciplina)} aulas coletadas para '{nome_disciplina_completo}'.")

            # Volta para a lista de disciplinas para a próxima iteração do loop no planejador
            print("  -> Voltando para a lista de turmas/disciplinas...")
            voltar_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Voltar"]')))
            self.driver.execute_script("arguments[0].click();", voltar_btn)
            self.wait.until(EC.presence_of_element_located((By.XPATH, f"//h3[normalize-space()='{nome_turma_completo}']")))
            print("  -> Retornou à lista.")

            # CORREÇÃO: Sai do iframe para o contexto principal, preparando para a próxima iteração do loop.
            self.driver.switch_to.default_content()

            return dados_disciplina

        except Exception as e:
            print(f"Ocorreu um erro fatal durante a coleta da disciplina: {e}")
            self._take_screenshot(f"erro_coleta_disciplina_{nome_turma_completo}")
            raise





# Exemplo de como usar a classe (pode ser chamado por outro script)
if __name__ == '__main__':
    # Este bloco agora serve apenas para execução direta e independente do scraper.
    # A lógica principal foi movida para ser reutilizável.
    # Este bloco só será executado se você rodar o script diretamente
    # Ex: python tools/scraper.py
    
    # O caminho raiz do projeto (assumindo que 'tools' está dentro dele)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if getattr(sys, 'frozen', False):
        PROJECT_ROOT = os.path.dirname(sys.executable)
    
    # Carrega credenciais de um arquivo (mais seguro do que colocar no código)
    try:
        with open(os.path.join(PROJECT_ROOT, 'data', 'credentials.json'), 'r', encoding='utf-8-sig') as f:
            creds = json.load(f)
    except FileNotFoundError:
        print("ERRO: Arquivo 'data/credentials.json' não encontrado.")
        print("Crie o arquivo com o formato: {\"username\": \"seu_usuario\", \"password\": \"sua_senha\"}")
        exit(1)
    except json.JSONDecodeError:
        print("ERRO: O arquivo 'data/credentials.json' está mal formatado.")
        exit(1)

    TARGET_URL = "https://portal.seduc.pi.gov.br/#!/turmas" # Substitua se necessário

    scraper_instance = Scraper(project_root=PROJECT_ROOT)    
    try:
        # A inicialização e carregamento de configs agora acontecem aqui para execução direta
        scraper_instance._load_configs()
        scraper_instance._initialize_driver()

        final_data = scraper_instance.capturar_dados(TARGET_URL, creds)
        
        # Salva os dados coletados em um arquivo JSON
        output_path = os.path.join(PROJECT_ROOT, 'data', 'aulas_coletadas.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print(f"\nDados salvos com sucesso em: {output_path}")

    except Exception as e:
        print(f"\nO processo de scraping falhou. Causa: {e}")
    finally:
        # Garante que o driver seja fechado ao executar diretamente
        if scraper_instance and scraper_instance.driver:
            print("Fechando o navegador.")
            scraper_instance.driver.quit()