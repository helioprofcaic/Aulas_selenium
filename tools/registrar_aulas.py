"""
================================================================================
Assistente de Registro de Aulas - registrar_aulas.py
================================================================================

Este script é a etapa final do fluxo de automação. Ele utiliza o Selenium para
automatizar o processo de registro de aulas no portal da Seduc, com base nos
planos de aula previamente preparados.

Funcionalidades:
- Lê os arquivos de plano de aula `.txt` da pasta `aulas/`, que já devem estar
  preenchidos.
- Realiza o login no portal da Seduc.
- Navega para a turma e disciplina corretas.
- Preenche o formulário de registro de aula em múltiplas etapas, incluindo:
  - Conteúdo e estratégia.
  - Vínculo de recursos didáticos (links).
- Automatiza a seleção da data no componente de calendário da interface.
- Pausa para intervenção manual na seleção do horário, que é dinâmico.
- Após o registro bem-sucedido, o arquivo `.txt` correspondente é excluído
  para evitar duplicidade.
- Em caso de falha, um screenshot é salvo na pasta `screenshots/` e o arquivo
  `.txt` é mantido para uma nova tentativa.
- Toda a execução é registrada em um arquivo de log na pasta `aulas/`.

Dependências e Pré-requisitos:
1.  **Arquivos de Dados (pasta `data/`):**
    - `credentials.json`: Usuário e senha para o login.
    - `mapa_turmas.json`: Mapeamento de nomes curtos para nomes completos das turmas.
    - `turmas_com_disciplinas.json`: Mapeamento de códigos de disciplina para nomes completos.

2.  **Planos de Aula (pasta `aulas/`):**
    - Os arquivos `.txt` devem existir e estar completamente preenchidos, sem
      marcadores como "Preencher". Este preenchimento é feito pelo script `preenchedor_planos.py`.

3.  **Ordem de Execução:**
    - Este script deve ser executado após `preparar_planos.py` e `preenchedor_planos.py`.
"""
import json
import os
import re
import time
from datetime import datetime
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager

class Registrador:
    def __init__(self, project_root):
        self.project_root = project_root
        self.driver = None
        self.wait = None

    # Mapeamento reverso para meses (para navegação no calendário)
    MESES_MAP_REVERSE = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
        "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
        "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12 # Corrigido o mapeamento de novembro
    }

    def _initialize_driver(self):
        print("[Registrador] Inicializando o WebDriver...")
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized") # Iniciar maximizado
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 30)
        # REMOVIDO: set_window_size, pois --start-maximized já cuida disso
        print("  -> Navegador iniciado maximizado.")
        self.driver.execute_script("document.body.style.zoom = '80%'") # Mantendo o zoom
        print("  -> Zoom da página definido para 80%.")


    def _take_screenshot(self, name):
        try:
            screenshots_dir = os.path.join(self.project_root, 'screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            path = os.path.join(screenshots_dir, f"registro_erro_{name}.png")
            self.driver.save_screenshot(path)
            print(f"  -> Screenshot de erro salvo em: {path}")
        except NoSuchWindowException:
            print("  -> ERRO: Não foi possível tirar screenshot porque a janela do navegador já foi fechada.")

    def _login_and_navigate_to_turmas(self, url, credenciais):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(credenciais['username'])
        self.driver.find_element(By.ID, 'password').send_keys(credenciais['password'])
        self.driver.find_element(By.CSS_SELECTOR, 'button[ng-click="logar(login)"]').click()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.collection-item[ng-click="selecionarPerfil(perfil)"]'))).click()
        self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'iframe-container')))
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ABRIR')]"))).click()
        self.driver.switch_to.default_content()

    def _navigate_to_disciplina(self, turma, disciplina):
        print(f"\n--- Navegando para: {turma} / {disciplina} ---")
        try:
            # Garante que o driver está no contexto principal antes de tentar mudar para o iframe
            self.driver.switch_to.default_content()
            turmas_iframe_selector = (By.CSS_SELECTOR, 'iframe[src*="listagem-turmas"]')
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(turmas_iframe_selector))
            
            # Espera por um elemento genérico dentro do iframe para garantir que o conteúdo carregou
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[div/h3]"))) # Espera por qualquer card de turma
            
            card_xpath = f"//div[div/h3[normalize-space()='{turma}'] and div/p[normalize-space()='{disciplina}']]"
            card = self.wait.until(EC.presence_of_element_located((By.XPATH, card_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
            registro_aulas_link = card.find_element(By.XPATH, ".//p[normalize-space()='Registro de aulas']")
            self.driver.execute_script("arguments[0].click();", registro_aulas_link)
            time.sleep(1)
            print("[Navegação] Acessou a página de 'Registro de aulas'.")
            return True
        except TimeoutException:
            print(f"ERRO: Não foi possível encontrar o card para a disciplina '{disciplina}' na turma '{turma}'.")
            self._take_screenshot(f"card_nao_encontrado_{turma}_{disciplina}")
            return False

    def _navigate_back_to_turmas(self):
        try:
            print("[Recuperação] Tentando voltar para a lista de turmas para continuar...")
            if not self.driver.window_handles:
                print("ERRO CRÍTICO: A janela do navegador não está mais disponível.")
                return

            print("  -> Usando o comando 'voltar' do navegador...")
            self.driver.back()
            time.sleep(2)

            print("  -> Verificando se o iframe da lista de turmas recarregou...")
            self.driver.switch_to.default_content()
            turmas_iframe_selector = (By.CSS_SELECTOR, 'iframe[src*="listagem-turmas"]')
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(turmas_iframe_selector))
            
            print("[Recuperação] Retorno à lista de turmas bem-sucedido.")

        except Exception as e:
            print(f"ERRO CRÍTICO: O comando 'voltar' falhou. Tentando URL direta como fallback. Erro: {e}")
            self._take_screenshot("erro_fatal_navegar_voltar")
            try:
                self.driver.get("https://portal.seduc.pi.gov.br/#!/turmas")
                # Após um hard reload, precisamos passar pela dança inicial do iframe novamente
                self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'iframe-container')))
                self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ABRIR')]"))).click()
                self.driver.switch_to.default_content()
                print("[Recuperação] Fallback para URL direta parece ter funcionado.")
            except Exception as e2:
                print(f"ERRO CRÍTICO: Fallback para URL direta também falhou. O script pode não conseguir continuar. Erro: {e2}")
                raise e2

    def _click_save_and_next(self):
        """Encontra o botão 'Salvar e Avançar' visível, rola até ele e clica."""
        try:
            save_button_xpath = "//button[contains(normalize-space(), 'Salvar e Avançar')]"
            save_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, save_button_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", save_button)
            return True
        except (TimeoutException, NoSuchElementException):
            print("ERRO: Botão 'Salvar e Avançar' não foi encontrado ou não é clicável.")
            return False
            
    def _wait_for_active_step(self, step_text):
        """Espera a etapa na barra de progresso se tornar ativa."""
        print(f"[Formulário] Esperando pela Aba '{step_text}' se tornar ativa na barra de progresso...")
        step_xpath = f"//nav[@aria-label='Progress']//div[@aria-current='step' and contains(., '{step_text}')]"
        try:
            self.wait.until(EC.visibility_of_element_located((By.XPATH, step_xpath)))
            print(f"  -> Aba '{step_text}' está ativa.")
            return True
        except TimeoutException:
            print(f"ERRO: A Aba '{step_text}' não se tornou ativa a tempo.")
            return False

    def _select_date_from_picker(self, target_date_str):
        """
        Abre o date picker e seleciona a data desejada.
        target_date_str format: YYYY-MM-DD
        """
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        target_day = target_date.day
        target_month = target_date.month
        target_year = target_date.year

        print(f"  -> Automatizando seleção de data: {target_date.strftime('%d/%m/%Y')}")

        # 1. Clicar no botão que abre o calendário (o que exibe a data atual)
        date_input_button_xpath = "//button[@type='button' and @aria-haspopup='dialog' and .//span[normalize-space()='Escolha uma data']]"
        date_input_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, date_input_button_xpath)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", date_input_button)
        self.driver.execute_script("arguments[0].click();", date_input_button) # Clicar via JS
        print("    -> Calendário aberto.")

        # 2. Navegar para o mês/ano correto
        calendar_dialog_xpath = "//div[@role='dialog' and contains(@id, 'radix-')]"
        self.wait.until(EC.visibility_of_element_located((By.XPATH, calendar_dialog_xpath)))

        while True:
            current_month_year_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, f"{calendar_dialog_xpath}//div[@class='text-sm font-medium']")))
            current_month_year_text = current_month_year_element.text
            
            # Parse current month and year from text like "setembro 2025"
            parts = current_month_year_text.split()
            current_month_name = parts[0].lower()
            current_year = int(parts[1])
            current_month = self.MESES_MAP_REVERSE[current_month_name]

            print(f"    -> Calendário atual: {current_month_year_text}. Alvo: {target_date.strftime('%B %Y')}")

            if current_year == target_year and current_month == target_month:
                print("    -> Mês e ano corretos encontrados.")
                break
            elif target_date < datetime(current_year, current_month, 1):
                # Target date is in the past relative to current calendar view
                prev_month_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"{calendar_dialog_xpath}//button[@name='previous-month']")))
                self.driver.execute_script("arguments[0].click();", prev_month_button) # Clicar via JS
                print("    -> Clicando no mês anterior.")
            else:
                # Target date is in the future relative to current calendar view
                next_month_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"{calendar_dialog_xpath}//button[@name='next-month']")))
                self.driver.execute_script("arguments[0].click();", next_month_button) # Clicar via JS
                print("    -> Clicando no próximo mês.")
            time.sleep(0.5) # Pequena pausa entre cliques de mês

        # 3. Selecionar o dia
        day_button_xpath = f"{calendar_dialog_xpath}//button[@name='day' and normalize-space()='{target_day}']"
        time.sleep(0.5) # Pausa adicional para a interface estabilizar antes de clicar no dia
        try:
            day_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, day_button_xpath)))
            self.driver.execute_script("arguments[0].click();", day_button) # Clicar via JS
            print(f"    -> Dia {target_day} selecionado automaticamente.")
            time.sleep(1) # Pausa após selecionar o dia
        except (TimeoutException, NoSuchElementException):
            print("\n" + "!"*15 + " AÇÃO MANUAL NECESSÁRIA " + "!"*15)
            print(f"    -> Não foi possível selecionar o dia {target_day} automaticamente.")
            print(f"    -> Por favor, selecione o dia {target_day} no calendário do navegador.")
            input("    -> Após selecionar, pressione ENTER para continuar...")
            print("!"*55)
            time.sleep(1) # Pausa após a ação manual


    def registrar_aula(self, aula_info, plano_de_aula):
        if not self._navigate_to_disciplina(aula_info['turma'], aula_info['disciplina']):
            return False # Retorna False para que o loop principal possa tentar a recuperação

        try:
            print("[Formulário] Procurando e clicando em 'Adicionar aula'...")
            # Espera o overlay de carregamento desaparecer antes de clicar em 'Adicionar aula'
            loading_overlay_xpath = "//div[contains(@class, 'flex justify-center items-center mt-[50vh]')]"
            self.wait.until(EC.invisibility_of_element_located((By.XPATH, loading_overlay_xpath)))
            
            add_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Adicionar aula')]")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
            add_button.click()
            print("  -> Botão 'Adicionar aula' clicado.")

            self.driver.switch_to.default_content()
            # CORREÇÃO: Fechar o colchete corretamente
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, 'iframe[src*="listagem-turmas"]')))
            
            if not self._wait_for_active_step("1 - Conteúdo"): raise Exception("Aba 1 não carregou.")

            # --- AUTOMAÇÃO DA SELEÇÃO DE DATA ---
            self._select_date_from_picker(aula_info['data'])
            # --- FIM DA AUTOMAÇÃO DA SELEÇÃO DE DATA ---

            print("\n" + "!"*15 + " AÇÃO MANUAL NECESSÁRIA " + "!"*15)
            print(f"Por favor, selecione o HORÁRIO ({aula_info['horario']}) da aula.")
            input("Após selecionar, pressione ENTER para continuar...")
            print("!"*55 + "\n  -> Retomando automação...")

            print("[Formulário] Preenchendo campos da Aba 1...")
            self.driver.find_element(By.XPATH, "//label[contains(., 'Conteúdo abordado')]/following-sibling::textarea").send_keys(plano_de_aula.get('conteudo', ''))
            self.driver.find_element(By.XPATH, "//label[contains(., 'Estratégia metodológica')]/following-sibling::textarea").send_keys(plano_de_aula.get('estrategia', ''))
            print("  -> Campos preenchidos.")

            if not self._click_save_and_next(): raise Exception("Falha ao salvar Aba 1.")
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Sim']"))).click()
            print("[Formulário] Aba 1 (Criação da Aula) salva com sucesso.")

            if not self._wait_for_active_step("2 - Plano de aula"): raise Exception("Aba 2 não ativou.")
            if not self._click_save_and_next(): raise Exception("Falha ao salvar Aba 2.")
            print("[Formulário] Aba 2 salva.")

            if not self._wait_for_active_step("3 - Frequência"): raise Exception("Aba 3 não ativou.")
            if not self._click_save_and_next(): raise Exception("Falha ao salvar Aba 3.")
            print("[Formulário] Aba 3 salva.")

            if not self._wait_for_active_step("4 - Recursos didáticos"): raise Exception("Aba 4 não ativou.")
            link_recurso = plano_de_aula.get('recurso_link')
            if link_recurso:
                print("  -> Clicando em 'Adicionar novo recurso didático'...")
                add_recurso_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Adicionar novo recurso didático')]")))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_recurso_button)
                add_recurso_button.click()
                
                dialog_xpath = "//div[@role='dialog' and .//h2[normalize-space()='Adicionar/Editar recurso didático']]"
                self.wait.until(EC.visibility_of_element_located((By.XPATH, dialog_xpath)))
                print("  -> Formulário de recurso aberto. Aguardando estabilização...")
                time.sleep(1)
                print("  -> Preenchendo campos...")
                
                resource_type = "Arquivo PDF"
                print(f"    -> Selecionando tipo de recurso: '{resource_type}'.")
                
                combobox_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"{dialog_xpath}//button[@role='combobox']")))
                combobox_button.click()
                
                option_xpath = f"//div[normalize-space()='{resource_type}']"
                link_option = self.wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
                link_option.click()
                print(f"    -> Opção '{resource_type}' selecionada.")

                recurso_titulo = plano_de_aula.get('recurso_titulo', '')
                self.driver.find_element(By.XPATH, f"{dialog_xpath}//label[contains(.,'Nome do recurso')]/following-sibling::div/input").send_keys(recurso_titulo)
                self.driver.find_element(By.XPATH, f"{dialog_xpath}//label[contains(.,'URL do recurso')]/following-sibling::div/input").send_keys(plano_de_aula.get('recurso_link', ''))
                self.driver.find_element(By.XPATH, f"{dialog_xpath}//textarea").send_keys(plano_de_aula.get('recurso_comentario', ''))
                
                print("  -> Clicando em 'Salvar' para confirmar o recurso...")
                confirm_add_button_xpath = f"{dialog_xpath}//button[contains(@class, 'bg-[#007521]')]"
                save_button_dialog = self.wait.until(EC.element_to_be_clickable((By.XPATH, confirm_add_button_xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button_dialog)
                self.driver.execute_script("arguments[0].click();", save_button_dialog)
                
                print("  -> Aguardando o formulário de recurso fechar...")
                self.wait.until(EC.invisibility_of_element_located((By.XPATH, dialog_xpath)))
                
                print(f"  -> Verificando se o recurso '{recurso_titulo}' apareceu na lista...")
                recurso_adicionado_xpath = f"//td[normalize-space()='{recurso_titulo}']"
                self.wait.until(EC.visibility_of_element_located((By.XPATH, recurso_adicionado_xpath)))
                print("  -> Recurso confirmado na lista. Aguardando 2 segundos...")
                time.sleep(2)

            if not self._click_save_and_next(): raise Exception("Falha ao salvar Aba 4.")
            print("[Formulário] Aba 4 salva.")

            if not self._wait_for_active_step("5 - Atividade"): raise Exception("Aba 5 não ativou.")
            final_button_xpath = "//button[contains(normalize-space(), 'Salvar e Finalizar')]"
            final_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, final_button_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", final_button)
            final_button.click()
            print("[Formulário] Aba 5 finalizada.")

            print("[Formulário] Aguardando o balão de confirmação final 'Atenção'...")
            modal_atencao_xpath = "//div[@role='dialog' and .//h2[normalize-space()='Atenção']]" # Usando normalize-space()
            self.wait.until(EC.visibility_of_element_located((By.XPATH, modal_atencao_xpath)))
            
            print("  -> Balão 'Atenção' apareceu. Clicando em 'Fechar'...")
            fechar_button_xpath = f"{modal_atencao_xpath}//button[normalize-space()='Fechar']"
            fechar_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, fechar_button_xpath)))
            self.driver.execute_script("arguments[0].click();", fechar_button)
            print("  -> Botão 'Fechar' clicado. Balão de confirmação fechado.")

            print(f"SUCESSO: Aula de {aula_info['disciplina']} em {aula_info['data']} registrada!")
            
            self._navigate_back_to_turmas()
            return True

        except Exception as e:
            print(f"\nERRO INESPERADO: Ocorreu uma falha durante o registro da aula.")
            print(f"  -> Detalhe: {e}")
            self._take_screenshot(f"{aula_info['turma']}_{aula_info['data']}")
            self._navigate_back_to_turmas()
            return False

# --- Funções de Parsing (sem alterações) ---
def parse_plan_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
    except FileNotFoundError: return None
    plan_data = {}
    for line in content.splitlines():
        if line.startswith('# Data:'): plan_data['data'] = line.split(':', 1)[1].strip()
        elif line.startswith('# Horário:'): plan_data['horario'] = line.split(':', 1)[1].strip()
    blocos = ['[CONTEUDO]', '[ESTRATEGIA]', '[RECURSO_TITULO]', '[RECURSO_LINK]', '[RECURSO_COMENTARIO]']
    for i, bloco_atual in enumerate(blocos):
        try:
            start_index = content.index(bloco_atual) + len(bloco_atual)
            end_index = len(content)
            if i + 1 < len(blocos):
                next_block_start = content.find(blocos[i+1], start_index)
                if next_block_start != -1: end_index = next_block_start
            valor = content[start_index:end_index].strip()
            if bloco_atual in ['[CONTEUDO]', '[ESTRATEGIA]'] and (not valor or "Preencher" in valor): return None
            plan_data[bloco_atual.strip('[]').lower()] = valor
        except ValueError: continue
    return plan_data if 'data' in plan_data and 'horario' in plan_data else None

def find_plans_to_register(project_root, mapa_turmas, turmas_disciplinas):
    aulas_para_registrar = []
    aulas_dir = os.path.join(project_root, 'aulas')
    mapa_turmas_reverso = {v.replace(' ', ''): k for k, v in mapa_turmas.items()}
    mapa_disciplinas_reverso = {disc['codigoDisciplina']: disc['nomeDisciplina'] for turma in turmas_disciplinas for disc in turma['disciplinas']}
    if not os.path.exists(aulas_dir): return []
    for nome_pasta_turma in sorted(os.listdir(aulas_dir)):
        caminho_pasta_turma = os.path.join(aulas_dir, nome_pasta_turma)
        # Ignora arquivos de log e outros diretórios especiais como 'inputs'
        if not os.path.isdir(caminho_pasta_turma) or nome_pasta_turma == 'inputs':
            continue

        for nome_arquivo in sorted(os.listdir(caminho_pasta_turma)):
            if not nome_arquivo.endswith('.txt'): continue
            caminho_arquivo = os.path.join(caminho_pasta_turma, nome_arquivo)
            plano = parse_plan_file(caminho_arquivo)
            if plano:
                # CORREÇÃO: Atualiza a regex para corresponder ao novo formato de nome de arquivo
                # que inclui o horário (ex: DISC_AAAAMMDD_HHMM.txt).
                match = re.match(r'(.+)_(\d{8})_\d{4}\.txt$', nome_arquivo)
                if not match: continue
                disciplina_curta = match.group(1)
                nome_curto_turma_normalizado = nome_pasta_turma.replace('_', 'º').replace(' ', '')
                turma_completa = mapa_turmas_reverso.get(nome_curto_turma_normalizado)
                disciplina_completa = mapa_disciplinas_reverso.get(disciplina_curta)
                if not turma_completa or not disciplina_completa:
                    print(f"AVISO: Mapeamento não encontrado para '{nome_pasta_turma}/{disciplina_curta}'. Pulando.")
                    continue
                aula_info = {'data': datetime.strptime(plano['data'], "%d/%m/%Y").strftime("%Y-%m-%d"), 'horario': plano['horario'], 'turma': turma_completa, 'disciplina': disciplina_completa, 'caminho_arquivo': caminho_arquivo}
                aulas_para_registrar.append({'info': aula_info, 'plano': plano})
            else:
                print(f"INFO: Plano '{nome_arquivo}' ignorado por estar incompleto (contém 'Preencher').")
    return aulas_para_registrar

class Logger:
    """Redireciona a saída do console (stdout) para um arquivo de log e para o terminal."""
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, "a", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

if __name__ == '__main__':
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(PROJECT_ROOT, 'data')
    try:
        with open(os.path.join(DATA_PATH, 'credentials.json'), 'r', encoding='utf-8-sig') as f: creds = json.load(f)
        with open(os.path.join(DATA_PATH, 'mapa_turmas.json'), 'r', encoding='utf-8-sig') as f: mapa_turmas = json.load(f)
        with open(os.path.join(DATA_PATH, 'turmas_com_disciplinas.json'), 'r', encoding='utf-8-sig') as f: turmas_disciplinas = json.load(f)
    except FileNotFoundError as e:
        print(f"ERRO: Arquivo de configuração não encontrado: {e.filename}")
        exit(1)

    # --- Configuração do Log ---
    AULAS_DIR = os.path.join(PROJECT_ROOT, 'aulas')
    LOGS_DIR = os.path.join(AULAS_DIR, 'logs') # Diretório específico para logs
    os.makedirs(LOGS_DIR, exist_ok=True)

    log_filename = f"log_registro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    log_filepath = os.path.join(LOGS_DIR, log_filename)
    sys.stdout = Logger(log_filepath)
    print(f"--- Log de execução iniciado. Salvo em: {log_filepath} ---")

    aulas_para_registrar = find_plans_to_register(PROJECT_ROOT, mapa_turmas, turmas_disciplinas)
    if not aulas_para_registrar:
        print("\nNenhum plano de aula encontrado para registrar.")
        exit(0)

    print(f"\nEncontradas {len(aulas_para_registrar)} aulas para registrar.")
    
    registrador = Registrador(project_root=PROJECT_ROOT)
    registrador._initialize_driver()
    registrador._login_and_navigate_to_turmas("https://portal.seduc.pi.gov.br/#!/turmas", creds)
    
    try:
        for i, item in enumerate(aulas_para_registrar):
            info = item['info']
            print(f"\n>>> Próxima aula a registrar ({i+1}/{len(aulas_para_registrar)}):")
            print(f"  - Data:      {info['data']}")
            print(f"  - Horário:   {info['horario']}")
            print(f"  - Turma:     {info['turma']}")
            print(f"  - Disciplina: {info['disciplina']}")
            
            user_choice = input("Deseja registrar esta aula? (s = sim / n = pular / parar = encerrar): ").lower()

            if user_choice == 'n':
                print("  -> Aula pulada pelo usuário. O arquivo será mantido.")
                continue
            elif user_choice == 'parar':
                print("  -> Processo encerrado pelo usuário.")
                break
            elif user_choice != 's':
                print("  -> Opção inválida. Pulando aula por segurança.")
                continue

            if registrador.registrar_aula(info, item['plano']):
                print(f"SUCESSO: Aula registrada. Removendo arquivo: {info['caminho_arquivo']}")
                os.remove(info['caminho_arquivo'])
            else:
                print(f"FALHA: O registro da aula falhou. O arquivo será mantido para nova tentativa.")
            
            time.sleep(2)
    finally:
        if registrador.driver and registrador.driver.window_handles:
            registrador.driver.quit()
            print("\nProcesso finalizado.")
        else:
            print("\nProcesso finalizado. O navegador parece já ter sido fechado.")
        
        if isinstance(sys.stdout, Logger):
            sys.stdout.close()
            sys.stdout = sys.stdout.terminal