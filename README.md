# FN Lock Simulator

Este programa simula a funcionalidade de "FN Lock" (ou camadas de teclado) via software, permitindo remapear teclas específicas quando ativado. É ideal para teclados compactos (60%, 65%) ou para quem deseja ter atalhos de navegação (como setas) nas teclas de letras (como WASD) sem precisar segurar a tecla FN física.

## Funcionalidades Principais

*   **Remapeamento Dinâmico**: Transforme teclas comuns em outras funções quando o modo está ativo (ex: W, A, S, D viram Setas Direcionais).
*   **Smart Typing (Digitação Inteligente)**: O programa detecta automaticamente quando você começa a digitar um texto normal e pausa o remapeamento temporariamente. Assim, você pode digitar sem precisar desligar o FN Lock manualmente.
*   **Tecla de Ativação Configurável**: Escolha qual tecla ativa/desativa o modo. O padrão é o **Alt Direito** (compatível com **Alt Gr** em teclados ABNT2), mas você pode escolher outras opções como Caps Lock, Ctrl Direito, teclas F1-F12, etc.
*   **Interface Visual**: Configure suas teclas facilmente através de uma interface gráfica moderna, sem precisar editar arquivos de configuração manualmente.
*   **Overlay de Status**: Um indicador visual discreto aparece na tela para informar se o modo está Ativo, Pausado ou Inativo.
*   **Minimizar para Bandeja**: O programa roda silenciosamente em segundo plano na bandeja do sistema (System Tray).
*   **Inicialização Automática**: Opção integrada para iniciar o programa junto com o Windows.

## Como Usar

### 1. Ativação
Existem três formas de ativar ou desativar o FN Lock:
*   **Atalho de Teclado**: Pressione a tecla de ativação configurada (Padrão: `Alt Direito` / `Alt Gr`).
*   **Interface Principal**: Clique no botão grande "ATIVAR" / "DESATIVAR".
*   **Bandeja do Sistema**: Clique com o botão direito no ícone do FN Lock na barra de tarefas.

### 2. Configuração de Teclas
1.  Abra a interface principal e clique em **"Configurar Teclas"**.
2.  **Origem**: Digite a tecla que você vai pressionar (ex: `w`).
3.  **Destino**: Digite a função que ela deve executar (ex: `up` para seta para cima).
4.  Clique no botão **"+"** para adicionar.
5.  Quando terminar, clique em **"Salvar e Fechar"**.

### 3. Configuração da Tecla de Ativação
1.  Vá em **"Configurar Teclas"**.
2.  No menu **"Tecla de Ativação"**, selecione a tecla desejada.
    *   *Nota: A opção "right alt" já cobre o funcionamento do Alt Gr em teclados brasileiros.*

### 4. Smart Typing
Marque a caixa **"Smart Typing (Auto-pause)"** na tela principal.
*   Quando ativado, se você pressionar qualquer tecla que **não** esteja mapeada, o programa entende que você está digitando um texto e pausa o FN Lock.
*   Após cerca de 1 segundo sem digitar, o FN Lock é reativado automaticamente.

## Instalação e Execução

O programa é distribuído como um executável portátil (`.exe`).
1.  Baixe ou compile o arquivo `FN-LOCK.exe`.
2.  Execute o arquivo.
3.  Opcional: Marque a caixa "Iniciar com o Windows" para que ele abra sempre que ligar o PC.

## Requisitos (para rodar código fonte)

Se preferir rodar via código Python:
*   Python 3.x
*   Dependências:
    ```bash
    pip install -r requirements.txt
    ```
